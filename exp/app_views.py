from django.http import HttpResponse
from django.shortcuts import render
from exp.models import Session, Report, ReportForm, Experiment, Security

from datetime import date, datetime, timedelta
from django.conf import settings
from django.utils import timezone

import time

# These are the functions that work with apps
# exp/group/<groupToken>
# exp/consent/<groupToken> (?sessionToken)
# exp/start/<sessionToken>
# exp/report/<sessionToken>

# New structure
# exp/start/<groupToken> -- return sessionToken, config, consent, created workerId
# exp/start/<groupToken>/<workerId> -- return sessionToken, config, consent for workerId
#   In this mode, workerId checked on participant list
#   If workerId is on the list, return the associated session token (last?)
# exp/new/<groupToken>/<workerId> -- force new session token for this participant (if not disallowed by Exp)
#
# exp/report/<sessionToken> -- modified to include the config file

# XML format
# <Empirical:session>
# <Empirical:config>
# <Empirical:consent>
# <Empirical:workerid>
# <Empirical:privatedata>  -- marks info that needs to be removed to deidentify data records
# <Empirical:datalog>      -- data that can eventually be shared

# <Empirical:status>
# <Empirical:uploaddate>
# <Empirical:timesince>

# special data event types:
# 'start' created when config file handed out, contains workerid verbatim
# 'status' written/read by apps, no xml formatting
# 'private' for non-shared data from the app, wrapped in xnl private tags
# 'complete' type used to facilitate download (by restriction to just these events)
# Conventionally, 'partial' types are used to reflect progress, 'complete' at finish but these aren't required


def empirical_error(msg):
    r="Error: %s\n" % msg
    r=r+settings.VERSION+'\n'
    r=r+("At: %s\n" % datetime.now())
    return r

def xml_string(xmldict):
    r="<root xmlns:Empirical=\"https://www.reberlab.org/\">\n"
    for i in xmldict.keys():
        r=r+"<%s>%s</%s>\r\n" % (i,xmldict[i],i)
    r=r+"\n</root>\n"
    return r

def session_order(e, session_list): # e is the experiment, session_list is a list of strings of sessionTokens
    configs=Session.objects.filter(exp=e)
    order=[]
    for i in configs:
        if i.sessionToken in session_list:
            if i.lastStarted is None:
                d = timezone.make_aware(datetime(2, 1, 1, tzinfo=None), timezone.get_default_timezone())
                #d = timezone.make_aware(datetime.min, timezone.get_default_timezone())
            else:
                d = i.lastStarted
            order.append((d,i))
    order.sort()
    (date_list, session_list)=zip(*order)
    return session_list

def start_session(request, groupToken, workerId=''):
    try:
        e=Experiment.objects.get(groupToken=groupToken)
    except:
        return HttpResponse(empirical_error('Invalid group token %s' % groupToken))

    s=e.study
    try:
        consent=s.consentJSON
    except:
        try:
            return HttpResponse(empirical_error('Unable to get consent info from %s' % s.name))
        except:
            return HttpResponse(empirical_error('Bad study linked to %s' % e.name))

    session_list=e.groupSessions.split()[:e.numTokens] # sessionlist of tokens to be used
    c=None
    has_prior = False
    demo_mode = False
    prior_session=''
    if workerId.lower()=='demo':
        # demo session
        session=session_list[0]
        config = ''
        demo_mode=True
    elif workerId!='':
        # check for existing workerId
        prior=s.participants.split()
        for i in prior:
            if ':' in i:
                t = i.split(':')
                if len(t)==2:
                    worker=t[0]
                    token=t[1]
                else:
                    worker=t[0]
                    token=t[-1]
                #(worker,token)=i.split(':')
            else:
                worker=i
                token=''
            if worker==workerId:
                has_prior=True
                prior_session=token
                break
    else: # create a synthetic workerId if not provided
        workerId='NoId_%s' % datetime.now().strftime("%m%d%Y_%H%M%S")
    if has_prior: # either returning to finish or restarting
        # if there is no token, will have to search the db to find the session -- to do
        if prior_session=='':
            # search
            r=Report.objects.filter(eventType='start').order_by('-uploadDate')
            for i in r:
                if i.dataLog==workerId:
                    prior_session=i.sessionToken
                    break
            # if prior_session doesn't get set, the participant might be 'blacklisted'
            if prior_session=='':
                return HttpResponse(empirical_error('Participant %s on exclusion list' % workerId))
        else:
            session=prior_session
    elif not demo_mode:
        # get new session token
        # sort on lastUpdated
        config_list=session_order(e,session_list) # sorting needs to be done manually in the function above

        # if no recycle, only return if lastUpdated is None
        if e.recycle==False:
            if config_list[0].lastStarted==None:
                c = config_list[0]
                session=c.sessionToken
            else:
                return HttpResponse(empirical_error('No tokens are available for %s' % e.name))
        else:
            c = config_list[0]
            session = c.sessionToken
        # for new workers, create started datalog event
        r = Report(sessionToken=session,sessionKey=c,eventType='start',dataLog=workerId) # workerId stored in this event to catch re-use later
        r.save()
        # and update study particpant list
        s.addParticipant(workerId,session)

    if c==None:
        try:
            c=Session.objects.get(sessionToken=session)
        except:
            return HttpResponse(empirical_error('Invalid session token %s' % session))
    config=c.configFile

    # update last started
    if not demo_mode:
        c.lastStarted=datetime.now()
        c.save()

    start_xml={}
    start_xml['Empirical:workerid']=workerId
    start_xml['Empirical:consent']="<![CDATA[%s]]>" % consent
    start_xml['Empirical:config']="<![CDATA[%s]]>" % config
    start_xml['Empirical:session']=session

    return HttpResponse(xml_string(start_xml))

# Used to force restarting with a new session token -- assumes no restart from status

def newstart_session(request, groupToken, workerId=''):
    try:
        e=Experiment.objects.get(groupToken=groupToken)
    except:
        return HttpResponse(empirical_error('Invalid group token %s' % groupToken))

    s=e.study
    try:
        consent=s.consentJSON
    except:
        try:
            return HttpResponse(empirical_error('Unable to get consent info from %s' % s.name))
        except:
            return HttpResponse(empirical_error('Bad study linked to %s' % e.name))

    session_list=e.groupSessions.split()[:e.numTokens] # sessionlist of tokens to be used
    c=None
    has_prior = False
    if workerId.lower()=='demo':
        # demo session
        session=session_list[0]
    elif workerId=='': # create a synthetic workerId if not provided
        workerId='NoId_%s' % datetime.now().strftime("%m%d%Y_%H%M%S")

    config_list=session_order(e,session_list) # sorting needs to be done manually in the function above
    if e.recycle==False:
        if config_list[0].lastStarted==None:
            c=config_list[0]
            session=c.sessionToken
        else:
            return HttpResponse(empirical_error('No tokens are available for %s' % e.name))
    else:
        c = config_list[0]
        session = c.sessionToken

    if c==None:
        try:
            c=Session.objects.get(sessionToken=session)
        except:
            return HttpResponse(empirical_error('Invalid session token %s' % session))
    config=c.configFile

    # update last started
    c.lastStarted=datetime.now()
    c.save()

    # update study particpant list
    s.addParticipant(workerId,session)

    # create started datalog event
    r = Report(sessionToken=session,sessionKey=c,eventType='start',dataLog=workerId) # workerId stored in this event to catch re-use later
    r.save()

    start_xml={}
    start_xml['Empirical:workerid']=workerId
    start_xml['Empirical:consent']="<![CDATA[%s]]>" % consent
    start_xml['Empirical:config']="<![CDATA[%s]]>" % config
    start_xml['Empirical:session']=session

    return HttpResponse(xml_string(start_xml))


# return_status() reports back on the latest status report for that sessionToken, used for continuing/restarting
def return_status(request, sessionToken, workerId=''):
    try:
        reports = Report.objects.filter(sessionToken=sessionToken,eventType='status').order_by('-uploadDate') # returns last status
    except:
        return HttpResponse('None') # no status is available, no data for this session yet
    if not reports.exists():
        return HttpResponse('None') # no status reports

    # wrap report in XML to include the timestamp and time since
    status_xml = {}
    status_xml['Empirical:status'] = reports[0].dataLog[:256]  # datalog length is limited to returning 256 to avoid abuse
    status_xml['Empirical:uploaddate'] = reports[0].uploadDate
    dt = timezone.now() - reports[0].uploadDate
    status_xml['Empirical:timesince'] = "%.4f" % (dt.seconds / 3600.0)
    status_response=xml_string(status_xml)

    # check to make sure workerId matches, necessary if recycle is set
    if workerId!='':
        starts = Report.objects.filter(sessionToken=sessionToken,eventType='start').order_by('-uploadDate')
        for s in starts:
            if s.dataLog==workerId:
                if s.uploadDate<reports[0].uploadDate: # workerid matches and status came after start event
                    return HttpResponse(status_response)
                else:
                    return HttpResponse('None') # this is the start event for this session, status was from prior
        # technically this line shouldn't be reached since there should be a start event for workerid
        # but just in case, we'll simply return None if there was no start event
        return HttpResponse('None')

    return HttpResponse(status_response)


# report() is thje data upload function
# security_check() attempts to protect against spammed uploads

def security_check(sessionToken,eventType):
    # check if already locked
    try:
        s=Security.objects.filter(sessionToken=sessionToken).latest('creationDate')
    except Security.DoesNotExist:
        s=None
    if s!=None and s.locked:
        return False
    r=Report.objects.filter(sessionToken=sessionToken).order_by('-uploadDate')
    for i in r:
        if i.eventType==eventType:
            elap=datetime.now(i.uploadDate.tzinfo)-i.uploadDate
            if elap.total_seconds()<settings.SECURITY_UPLOAD_MIN_TIME:
                # add security event object
                if s!=None:
                    s.hit_count=s.hit_count+1
                    if s.count>settings.MAX_SECURITY_COUNT:
                        s.locked=True
                    s.securityLog=s.securityLog+'%d seconds since last update; ' % elap.total_seconds()
                    s.save()
                else:
                    s=Security(sessionToken=sessionToken,hit_count=0)
                    s.securityLog='%d seconds since last update; ' % elap.total_seconds()
                    s.save()
                return False
    return True

# to do -- wrap upload in xml structure adding worker id, configfile
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def report(request, sessionToken, workerid=''):
    if request.method=="POST":
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            r=report_form.save(commit=False)
            try:
                r.sessionKey=Session.objects.get(sessionToken=sessionToken)
            except:
                # not a valid session, maybe don't save?
                return HttpResponse(empirical_error('Invalid session token %s' % sessionToken))
            # here should check how long ago the token was given out or started and disallow data too long after start
            security_ok=security_check(sessionToken,report_form.cleaned_data['eventType'])
            if security_ok:
                if r.eventType=='private': # wrap content in private tags
                    report_xml={}
                    ip_addr=get_client_ip(request)
                    wrapped_report = xml_string(report_xml)
                    report_xml['Empirical:privatedata'] = "IP address: %s\n%s" % (ip_addr,r.dataLog)
                    r.dataLog = wrapped_report
                    r.save()
                elif r.eventType=='status': # no xml wrapping on status events
                    r.save()
                else:
                    report_xml={}
                    ip_addr=get_client_ip(request)
                    if workerid=='':
                        # find workerid from recent start event
                        start_event=Report.objects.filter(sessionToken=sessionToken, eventType='start').order_by('-uploadDate')
                        if len(start_event)==0:
                            workerid='None, no start event found'
                        else:
                            workerid=start_event[0].dataLog
                    report_xml['Empirical:config']=r.sessionKey.configFile
                    if r.eventType == 'private':  # wrap the data into the private section
                        report_xml['Empirical:privatedata'] = "WorkerId: %s\nIP address: %s\n%s" % (workerid, ip_addr, r.dataLog)
                    else: # typical format
                        report_xml['Empirical:privatedata']="WorkerId: %s\nIP address: %s" % (workerid,ip_addr)
                        report_xml['Empirical:datalog']=r.dataLog
                    wrapped_report=xml_string(report_xml)
                    r.dataLog=wrapped_report
                    r.save()
            return render(request, 'report_accepted.html',{'log':r.dataLog, 'security':security_ok})

    upload_form=ReportForm()
    return render(request, 'test_report.html',{'form':upload_form})




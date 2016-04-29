from django.shortcuts import render
from django.http import HttpResponse

from exp.models import Session, Report, ReportForm, TokenGeneration, TokenForm, Study, StudyForm, Security, ConfigForm
from django.contrib.auth.decorators import login_required

# Experiments as a structure don't exist in the db, each session has it's own line
#  so experiment information is assembled on the fly from what is in the db
class Experiment_desc():
    def __init__(self,name,fill=True):
        self.name=name
        if fill:
            self.find_sessions()

    def find_sessions(self):
        session_list=Session.objects.all().filter(expName=self.name).order_by('-creationDate')
        if session_list!=[]:
            self.date=session_list[0].creationDate # experiment creation date is assumed to be the same for all config files
            self.token=session_list[0].sessionToken # this sessionToken can be used as a link to the experiment display view
            cfg_list=[]
            for s in session_list:
                # check for data reports on this session
                report_list=Report.objects.all().filter(sessionToken=s.sessionToken)
                reports=[]
                for i in report_list:
                    r = (i.eventType,i.uploadDate)
                    reports.append(r)
                cfg_list.append((s.name,s.sessionToken,s.creationDate,reports))
            #cfg_list.sort()
            self.cfg_list=cfg_list
            self.num_sessions=len(cfg_list)
        return

    def find_data(self):
        session_list=Session.objects.all().filter(expName=self.name)
        reports=[]
        for s in session_list:
            report_list=Report.objects.all().filter(sessionToken=s.sessionToken).order_by('-uploadDate')
            if report_list.exists():
                for r in report_list:
                    reports.append((s.sessionToken,r.eventType,r.pk,r.uploadDate,data_summary(r.dataLog,10,'###')))
        return reports

# Data summarizing/shortening helper function
def data_summary(log,length,separator=''):
    lines=log.split('\n')
    count=0
    summary=''
    for i in lines:
        if count<length:
            summary=summary+('%d. ' % (count+1))+i+'\n'
        count=count+1
        if i[:len(separator)]==separator:
            summary=summary+separator+'\n'
            count=0
    return summary



# The following 3 functions display information about the experiments and sessions in the database

# index() displays a list of all experiments, up to 10 config files listed per experiment
@login_required
def index(request):
    session_list=Session.objects.all().order_by('-creationDate')
    experiment_names=[]
    for s in session_list:
        if s.expName not in experiment_names:
            experiment_names.append(s.expName)
    Exps=[]
    for j in experiment_names:
        e = Experiment_desc(j)
        Exps.append(e)
    return render(request, 'exp_index.html', {'experiments': Exps})

# experiment() displays information on a single experiment including every config file
@login_required
def experiment(request, sessionToken):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    e = Experiment_desc(s.expName)
    # find all grouptokens for this experiment
    Tokens=TokenGeneration.objects.all().filter(expName=e.name)
    groups=[]
    studies=[]
    for t in Tokens:
        for s in e.cfg_list:
            if s[1] in t.groupSessions:
                if t.groupToken!='' and t.groupToken not in groups:
                    groups.append(t.groupToken)
                    if t.studyName!=None:
                        studies.append(t.studyName.name)
                    else:
                        studies.append('None')
    return render(request, 'experiment_info.html', {'exp': e, 'session': sessionToken, 'groups': zip(groups,studies)})

# show_config() displays information on a single session
@login_required
def show_config(request, sessionToken):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    # Get any data reports on this session
    data_report = Report.objects.all().filter(sessionToken=sessionToken)
    return render(request, 'display_config.html', {'session': s, 'reports':data_report})

@login_required
def new_config(request, sessionToken='', edit=False):
    if request.method=="POST":
        # add the new config element to the db
        form=ConfigForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['sessionToken']!='None':
                try:
                    c=Session.objects.get(sessionToken=sessionToken)
                    c.configFile=form.cleaned_data['configFile']
                    c.creationDate=datetime.now()
                    c.save()
                except: # not sure how this could happen, but save as new
                    c=form.save()
            else:
                cfg=form.save(commit=False)
                c=Session.objects.create_session(cfg.name,cfg.configFile,cfg.expName)
            return render(request, 'display_config.html', {'session': c, 'reports':None})
        else:
            return HttpResponse("Unable to parse config file edit")

    # display form to create config -- to do: if sessionToken!='', include that information in the form; allow copy as well as edit links on config view
    if sessionToken=='':
        form=ConfigForm(initial={'sessionToken': 'None'})
    else:
        try:
            s=Session.objects.get(sessionToken=sessionToken)
        except:
            return render(request, 'session_not_found_error.html', {'token': sessionToken})
        if edit:
            form=ConfigForm(instance=s)
        else:
            form=ConfigForm(initial={'sessionToken': 'None', 'expName': s.expName})
    return render(request,'new_config.html', {'form': form, 'sessionToken': sessionToken})

@login_required
def edit_config(request,sessionToken):
    return new_config(request,sessionToken,True)

@login_required
def copy_config(request,sessionToken):
    try:
        s=Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})
    new_cfg=Session.objects.create_session(s.name,s.configFile,s.expName)
    return render(request,'display_config.html', {'session': new_cfg, 'reports':None})


@login_required
def show_data(request, sessionToken, pkid=''):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    if pkid!='':
        data_report = Report.objects.all().filter(sessionToken=sessionToken,pk=int(pkid))
    else: # assume we should show all the data for the experiment
        data_report = Report.objects.all().filter(sessionToken=sessionToken)

    return render(request, 'display_data.html', {'session': s, 'reports':data_report})

@login_required
def one_data_file(request, sessionToken, pkid):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    if pkid!='':
        data_report = Report.objects.all().filter(sessionToken=sessionToken,pk=int(pkid))
    else:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    if data_report.exists():
        output_filename="%s_data_%s_%s.txt" % (s.expName,date.today().strftime("%d%b%Y"),pkid)
        response=HttpResponse(data_report[0].dataLog,content_type='text/plain')
        response['Content-Disposition'] = "attachment; filename=%s" % output_filename
        return response
    return render(request, 'session_not_found_error.html', {'token': sessionToken})

@login_required
def exp_data(request, sessionToken):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    e = Experiment_desc(s.expName,False)
    reports=e.find_data()
    return render(request, 'display_exp_data.html', {'sessionToken': sessionToken, 'expName': e.name, 'reports': reports})

def add_token_creation_event(sessionToken,studyName):
    key=Session.objects.get(sessionToken=sessionToken)
    if studyName!=None:
        consent=studyName.consentJSON
    else:
        consent="None"
    token_report=Report(sessionToken=sessionToken,sessionKey=key,eventType='token',dataLog=consent)
    token_report.save()
    return

from mturk_hits import *
from django.templatetags.static import static

@login_required
def make_link_tokens(request, token):
    sessionToken=token
    try:
        exp_name=Session.objects.get(sessionToken=sessionToken).expName
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    all_sessions=Session.objects.all().filter(expName=exp_name).order_by('creationDate')  # oldest first
    # Check to see if there is a data report for the token, skip if so
    sessions=[]
    skip_sessions=[]
    for s in all_sessions:
        data_report = Report.objects.all().filter(sessionToken=s.sessionToken)
        if not data_report.exists():
            sessions.append(s)
        else:
            skip_sessions.append(s)

    if request.method=="POST":
        log=''
        form=TokenForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['priorTokens']>0:
                # add sessions to previous token group
                log+="Adding to token event %d;" % form.cleaned_data['priorTokens'].pk
                tc=form.cleaned_data['priorTokens']
                tc.groupSessions=tc.groupSessions+' '
            else:
                log+="Created token event;"
                tc=form.save(commit=False)
                tc.user=request.user
                tc.expName=exp_name
                tc.create_token()
                tc.groupSessions=''
            log+="Group token %s;" % tc.groupToken
            if settings.FORCE_EXTERNAL_APP_LINKS:
                groupURL="https://www.reberlab.org/"+static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken))
            else:
                groupURL=request.build_absolute_uri(static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken)))
            # the list of session tokens gets assembled here
            session_list=[]
            for s in sessions:
                log+="Found session %s;" % s.sessionToken
                session_list.append(s.sessionToken)
            session_list=session_list[:form.cleaned_data['numTokens']]
            log+="Truncated to %d;" % len(session_list)
            tc.groupSessions=tc.groupSessions+' '.join(session_list)
            tc.numTokens=len(tc.groupSessions.split())
            tc.save()

            # if AWS credentials, upload HITs
            if form.cleaned_data['mturk_key_id']!='' and form.cleaned_data['mturk_secret_key']!='':
                log+=mTurkHITs((form.cleaned_data['mturk_key_id'],form.cleaned_data['mturk_secret_key']),groupURL,tc.numTokens,
                              form.cleaned_data['mturk_title'],form.cleaned_data['mturk_description'],
                              form.cleaned_data['mturk_frame_size'],form.cleaned_data['mturk_amount'])
                log+="Finished mTurkHITs;"
            # if email address list (and no mturk -- don't mix), send emails
            elif form.cleaned_data['emailList']!='':
                log+=emailInvites(form.cleaned_data['emailList'],session_list)
            else:
                log+='Completed;'

            # log token creation events for all new links -- new 9/2/2015
            for s in session_list:
                add_token_creation_event(s,form.cleaned_data['studyName'])
        else:
            log=['Invalid Form']
            return render(request, 'link_tokens.html', {'app': 'None', 'groupToken': 'None', 'tokens': [], 'log': log})
        log_list=log.split(';')
        tokenURL=request.build_absolute_uri(static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken)))
        # participant list from Study
        if tc.studyName!=None:
            studyName=tc.studyName
            prior_ps=tc.studyName.participants.split()
        else:
            studyName=None
            prior_ps=''
        # list of data events in tokens should be null
        session_list=tc.groupSessions.split()
        session_data=[]
        num_available=0
        for s in session_list:
            num_events=len(Report.objects.all().filter(sessionToken=s))
            session_data.append((s,num_events))
            if num_events < 2:
                num_available=num_available+1

        return render(request, 'link_tokens.html', {'app': form.cleaned_data['appletName'],
                                                    'groupToken': tc.groupToken,
                                                    'groupTokenURL': tokenURL,
                                                    'study': studyName,
                                                    'excluded': prior_ps,
                                                    'tokens': session_data,
                                                    'status': (len(session_list),num_available),
                                                    'log': log_list})

    previous=TokenGeneration.objects.all().filter(expName=exp_name).order_by('-creationDate')
    previous_token_links=[]
    if not previous.exists():
        form = TokenForm()
    else:
        for t in previous:
            if t.groupToken!=None: # shouldn't happen unless there was a bug and malformed group token event
                previous_token_links.append(t)
        form = TokenForm(initial={'appletName': previous[0].appletName,
                                  'mturk_amount': previous[0].mturk_amount,
                                  'mturk_frame_size': previous[0].mturk_frame_size,
                                  'mturk_title': previous[0].mturk_title,
                                  'mturk_description': previous[0].mturk_description})
        form.fields['priorTokens'].queryset = previous
    return render(request, 'link_token_form.html', {'form': form, 'exp_name': exp_name, 'sessions': sessions, 'skipped':skip_sessions,
                                                    'priorLinks': previous_token_links})
# group token info and status
@login_required
def group_token(request, token):
    groupToken=token
    try:
        g=TokenGeneration.objects.get(groupToken=groupToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': groupToken})

    tokenURL=request.build_absolute_uri(static("%s?group=%s" % (g.appletName,g.groupToken)))
    sessionTokens=g.groupSessions.split()

    # to do -- indicate recycle status

    # study participants
    Study=g.studyName
    if Study!=None:
        studyName=Study
        prior_ps=Study.participants.split()
    else:
        studyName=None
        prior_ps=[]

    session_data=[]
    num_available=0
    for s in sessionTokens:
        num_events=len(Report.objects.all().filter(sessionToken=s))
        session_data.append((s,num_events))
        if num_events < 2:
            num_available=num_available+1

    return render(request, 'link_tokens.html', {'app': g.appletName,
                                                'groupToken': groupToken,
                                                'groupTokenURL': tokenURL,
                                                'tokens': session_data,
                                                'study': studyName,
                                                'excluded': prior_ps,
                                                'status': (len(sessionTokens),num_available),
                                                'log': []})

# study handling views
import json
@login_required
def studies(request, studyNumber=''):
    # allow upload
    if request.method=="POST":
        study_form = StudyForm(request.POST)
        if study_form.is_valid():
            s=study_form.save(commit=False)
            s.user=request.user
            try:
                consent=json.loads(s.consentJSON)
                s.save()
            except:
                consent={'Error': 'Unable to parse the JSON consent form, not saved'}
    else:
        consent={}
    # list all available studies
    s=None
    if studyNumber!='':
        try:
            s=Study.objects.get(pk=int(studyNumber))
        except:
            s=None
    if s!=None:
        form=StudyForm(instance=s)
    else:
        form=StudyForm()
    study_list=Study.objects.all()

    return render(request,'studies.html', {'form': form, 'study_list': study_list, 'consent': consent})

# start() is the core experiment app communication function that distributes the cfg file text
#  in addition, this function logs a 'start' event
from datetime import date, datetime

def start(request, sessionToken, args=''):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
        cfg = s.configFile
    except:
        return HttpResponse('No such config file associated with token %s' % sessionToken) # should have error template for bad info

    # add a line to the Report db indicating that this session was started unless in demo mode
    if args!='demo':
        r = Report(sessionToken=s.sessionToken,sessionKey=s,eventType='start',dataLog=datetime.now())
        r.save()

    return HttpResponse(cfg)

# This is a key function for getting a session assocaited with a group
# Often used as connection to mturk HITs with a group of sessiontokens on one URL
def get_session(request, groupToken, workerId=''):
    try:
        t=TokenGeneration.objects.get(groupToken=groupToken)
    except:
        return HttpResponse('Error: Invalid group %s' % groupToken)

    sessions=t.groupSessions.split()
    # check if this workerId has already been assigned a token and re-assign
    if workerId!='': # one was provided with the URL
        if workerId=='demo':  # this is a call to produce a demo cfg
            return HttpResponse(sessions[0])
        for s in sessions:
            r=Report.objects.filter(sessionToken=s,eventType='given')
            if r.exists():
                for i in r: # r should really have only one object, if this list is >1, something weird happened but we'll match anyway
                    if i.dataLog == workerId:
                        return HttpResponse("%s match to %s" % (s,workerId))

        # check the study to see if this workerId has already done a related experiment and return error if so
        study=t.studyName
        if study!=None and study.participants and study.unique_id:  # if unique_id is set, then check to make sure worker id is not in participants
            prev_ids=study.participants.split(' ')
            if workerId in prev_ids:
                return HttpResponse("Error: duplicate participant %s" % workerId)
    else:
        workerId='NoId_%s' % datetime.now()  # unique workerId string that embeds the date

    # used_list accumulates all the used sessions, to be used for recycling if needed
    debug_string=""
    used_list=[]
    session_match=None
    for s in sessions:
        r=Report.objects.filter(sessionToken=s,eventType='start').order_by('-uploadDate')  # somebody already started this session
        if not r.exists():
            debug_string+='No start for %s, checking given; ' % s
            r=Report.objects.filter(sessionToken=s,eventType='given')
            if not r.exists():
                debug_string+='Match on %s ;' % s
                session_match=s # found an unused session to give
                break
        debug_string+='Adding %s to used; ' % s
        used_list.append([r[0].uploadDate,s])

    # recycle a previously used token
    if session_match==None:
        study=t.studyName
        if study!=None and study.recycle:
            used_list.sort()  # sort session token by last data event date
            try:
                debug_string+='Matching from used %s; ' % used_list[0][1]
                session_match=used_list[0][1] # return oldest
            except:
                return HttpResponse('Error: Cannot recycle prior session')
        else:
            return HttpResponse('Error: No available sessions')

    # create the 'given' event for the session to be returned
    try:
        session=Session.objects.get(sessionToken=session_match)
    except:
        return HttpResponse('Error: Bad session number')
    r = Report(sessionToken=session_match,sessionKey=session,eventType='given',dataLog=workerId) # workerId stored in this event to catch re-use later
    r.save()
    # add worker_id to the study list
    study=t.studyName
    if study!=None and study.participants:
        study.participants=study.participants+' '+workerId
        study.save()
    debug_string=session_match+' '+debug_string  # for debugging recycling problems 04/29/2016 -- PJR
    #return HttpResponse(debug_string)
    return HttpResponse(session_match)

def return_status(request, sessionToken):
    try:
        reports = Report.objects.filter(sessionToken=sessionToken,eventType='status').order_by('-uploadDate') # returns last status
    except:
        return HttpResponse('None') # no status is available, no data for this session yet
    if not reports.exists():
        return HttpResponse('None') # no status reports
    return HttpResponse(reports[0].dataLog)  # datalog length could be limited here

def get_consent(request, sessionToken):
    try:
        reports = Report.objects.filter(sessionToken=sessionToken,eventType='token').order_by('-uploadDate') # returns last status
    except:
        return HttpResponse('None') # no token event is available, no associated study (sessiontoken given directly)
    if not reports.exists():
        return HttpResponse('None')
    return HttpResponse(reports[0].dataLog) # consent form text is put in the dataLog from the Study during token creation


def security_list(request):
    # show all security events in the db
    s=Security.objects.all()
    return render(request, 'security_event_list.html', {'event_list':s})

# to do:
# close sessions when done to block spam uploads
# database 'test' reset to archive (to mark all sessions as available and archive all status/data events)
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

def report(request, sessionToken):
    if request.method=="POST":
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            r=report_form.save(commit=False)
            try:
                r.sessionKey=Session.objects.get(sessionToken=sessionToken)
            except:
                # not a valid session, maybe don't save?
                return HttpResponse('Error: Invalid Session')
            # here should check how long ago the token was given out or started and disallow data too long after start
            security_ok=security_check(sessionToken,report_form.cleaned_data['eventType'])
            if security_ok:
                r.save()
            return render(request, 'report_accepted.html',{'log':r.dataLog, 'security':security_ok})

    upload_form=ReportForm()
    return render(request, 'test_report.html',{'form':upload_form})

import zipfile, os.path
from django.conf import settings
from django.core.files import File

# construct a unique .txt file output name
def unique_txt(fn_list,cfg_name,event_type):
    base=os.path.splitext(cfg_name)[0]
    fn="%s_%s.txt" % (base,event_type)
    count=0
    while (fn in fn_list):
        count=count+1
        fn="%s_%s_%d.txt" % (base,event_type,count)
    return fn

# bulk data download for an entire experiment
@login_required
def download_data(request, sessionToken):
    try:
        r=Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    count=0 # for duplicate filenames
    fn="%s_data_%s.zip" % (r.expName,date.today().strftime("%d%b%Y"))
    output_filename=os.path.join(settings.MEDIA_ROOT, settings.ZIP_TMP, fn)
    while os.path.exists(output_filename) and count<100:
        count=count+1
        fn="%s_data_%s_%d.zip" % (r.expName,date.today().strftime("%d%b%Y"),count)
        output_filename=os.path.join(settings.MEDIA_ROOT, settings.ZIP_TMP, fn)
    if count==100:
        return HttpResponse('Error creating output file')

    E=Experiment_desc(r.expName)
    output_zip=zipfile.ZipFile(output_filename, 'w')
    fn_list=[] # for tracking duplicate filenames in the output zip
    for s in E.cfg_list:
        # s[0]=name, s[1]=sessionToken, s[2]=list of report objects
        report_list=Report.objects.all().filter(sessionToken=s[1])
        for r in report_list:
            if len(r.dataLog.strip())>0: # only save events with some data -- the empty ones should be 'start' reports
                fn=unique_txt(fn_list,s[0],r.eventType)
                output_zip.writestr(fn,r.dataLog)
                fn_list.append(fn)

    output_zip.close()
    f=open(output_filename,'rb')
    response = HttpResponse(File(f),content_type='application/zip')
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(output_filename)
    response['Content-Length'] = os.path.getsize(output_filename)
    return response
    # filter by keywords like partial/complete?

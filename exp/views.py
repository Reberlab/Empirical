from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from exp.models import Session, Report, ReportForm, TokenGeneration, TokenForm, Study, StudyForm, Security, ConfigForm, Experiment_desc
from datetime import date, datetime
import time

from app_views import *
from data_views import *

# The following 3 functions display information about the experiments and sessions in the database
# index() displays a list of all experiments, up to 10 config files listed per experiment
@login_required
def index(request):
    log=[]
    start=time.time()
    session_list=Session.objects.all().order_by('-creationDate')
    done=time.time()
    log.append("Loaded %d objects, %.2f s" % (len(session_list),done-start))
    experiment_names=[]
    for s in session_list:
        if s.expName not in experiment_names:
            experiment_names.append(s.expName)
    done=time.time()
    log.append("Found %d objects, %.2f s" % (len(experiment_names),done-start))
    Exps=[]
    for j in experiment_names:
        e = Experiment_desc(j)
        Exps.append(e)
        done=time.time()
        log.append("Added %s experiments, %.2f s" % (j,done-start))
    done=time.time()
    log.append("Assembled %d experiments, %.2f s" % (len(Exps),done-start))
    return render(request, 'exp_index.html', {'experiments': Exps, 'log': log})

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

def add_token_creation_event(sessionToken,studyName):
    key=Session.objects.get(sessionToken=sessionToken)
    if studyName!=None:
        consent=studyName.consentJSON
    else:
        consent="None"
    token_report=Report(sessionToken=sessionToken,sessionKey=key,eventType='token',dataLog=consent)
    token_report.save()
    return

# from mturk_hits import *
from django.templatetags.static import static

# link token form to do
# -- get rid of the mturk form elements (eventually remove from table too)
# -- change the text field box to produce a set of name linked tokens: app?group=xx&workerid=yyy
# -- allow for resuse of used cfg files and selection of specific cfgs to put into a token generation event
#    maybe through radio check boxes to the left of the listed sessions? and/or a check box to "re-use all"
#    or maybe as an option in the number of tokens, add 'all unused' and 'all, reuse'

# Note -- how do we use this to replace/update a specific condition within a group token without changing
# the URL?  On mturk, changing the URL changes the HIT and that means people will sign out a HIT that
# we have to filter/prevent them from running.
# Seems like we might need another element of the token table listing a subset of session tokens in use
# out of a broader set to allow for focused subsets.

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
        log_list=[]
        adding_to_existing=False
        form=TokenForm(request.POST)
        if form.is_valid():
            # to do -- create individual session tokens with workerid=names from participantList
            if form.cleaned_data['priorTokens']>0:
                # add sessions to previous token group
                log_list.append("Adding to token event %d" % form.cleaned_data['priorTokens'].pk)
                tc=form.cleaned_data['priorTokens']
                adding_to_existing = True
                # tc.groupSessions=tc.groupSessions+' '
                # set numTokens to current addition, totalTokens to length of list -- ?
            else:
                log_list.append("Created token event")
                tc=form.save(commit=False)
                tc.user=request.user
                tc.expName=exp_name
                tc.create_token()
                tc.groupSessions=''
            log_list.append("Group token %s" % tc.groupToken)
            #if settings.FORCE_EXTERNAL_APP_LINKS:
            #    groupURL="https://www.reberlab.org/"+static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken))
            #else:
            #    groupURL=request.build_absolute_uri(static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken)))
            # the list of session tokens gets assembled here
            session_list=[]
            for s in sessions:
                log_list.append("Found session %s" % s.sessionToken)
                session_list.append(s.sessionToken)

            # if add used, include sessions with data
            if form.cleaned_data['readd_used']:
                for s in skip_sessions:
                    log_list.append("Found session %s" % s.sessionToken)
                    session_list.append(s.sessionToken)

            # if add all
            if not form.cleaned_data['add_all']:
                session_list = session_list[:form.cleaned_data['numTokens']]
                log_list.append("Truncated to %d" % len(session_list))
            else:
                log_list.append("All sessions included")

            # if adding, put new cfgs at front of list
            if adding_to_existing:
                tc.groupSessions=' '.join(session_list)+' '+tc.groupSessions
            else:
                tc.groupSessions=' '.join(session_list)
            tc.totalTokens=len(tc.groupSessions.split())

            # if restrict to new
            if form.cleaned_data['restrict_to_new']:
                tc.numTokens=len(session_list)
                log_list.append("Restricting to %d new tokens" % tc.numTokens)
            else:
                tc.numTokens=tc.totalTokens

            # participant list
            # create url list -- need definition of app syntax for workerid/name
            # create workerid tokens
            # add to Study participant ids?

            tc.save()

            # if AWS credentials, upload HITs
            #if form.cleaned_data['mturk_key_id']!='' and form.cleaned_data['mturk_secret_key']!='':
            #    log+=mTurkHITs((form.cleaned_data['mturk_key_id'],form.cleaned_data['mturk_secret_key']),groupURL,tc.numTokens,
            #                  form.cleaned_data['mturk_title'],form.cleaned_data['mturk_description'],
            #                  form.cleaned_data['mturk_frame_size'],form.cleaned_data['mturk_amount'])
            #    log+="Finished mTurkHITs;"
            # if email address list (and no mturk -- don't mix), send emails
            #elif form.cleaned_data['emailList']!='':
            #    log+=emailInvites(form.cleaned_data['emailList'],session_list)
            #else:
            log_list.append("Completed")

            # log token creation events for all new links -- new 9/2/2015
            for s in session_list:
                add_token_creation_event(s,form.cleaned_data['studyName'])
        else:
            log=['Invalid Form']
            return render(request, 'link_tokens.html', {'app': 'None', 'groupToken': 'None', 'tokens': [], 'log': log})
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
                                                    'status': (tc.numTokens,tc.totalTokens,num_available),
                                                    'log': log_list})

    previous=TokenGeneration.objects.all().filter(expName=exp_name).order_by('-creationDate')
    previous_token_links=[]
    if not previous.exists():
        form = TokenForm()
    else:
        for t in previous:
            if t.groupToken!=None: # shouldn't happen unless there was a bug and malformed group token event
                previous_token_links.append(t)
        form = TokenForm(initial={'appletName': previous[0].appletName})
                                  #'mturk_amount': previous[0].mturk_amount,
                                  #'mturk_frame_size': previous[0].mturk_frame_size,
                                  #'mturk_title': previous[0].mturk_title,
                                  #'mturk_description': previous[0].mturk_description})
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


# What calls this rendered list of security reports? -- PJR
def security_list(request):
    # show all security events in the db
    s=Security.objects.all()
    return render(request, 'security_event_list.html', {'event_list':s})

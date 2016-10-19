from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from exp.models import Session, Report, ReportForm, Study, StudyForm, Security, ConfigForm, Experiment, ExperimentForm
from datetime import date, datetime
import time
import json
from django.templatetags.static import static
#from django.templatetags.static import static

from app_views import *
from data_views import *

# The following 3 functions display information about the experiments and sessions in the database
# index() displays a list of all experiments, up to 10 config files listed per experiment

# to do: index will now show the study list with experiments linked to each study
# -- all studies
@login_required
def index(request):
    study_list=Study.objects.all()
    return render(request, 'study_index.html', {'studies': study_list})

# -- one study, list all associated experiments
@login_required
def one_study(request, studyNumber=''):
    try:
        s = Study.objects.get(pk=int(studyNumber))
    except:
        return render(request, 'Object_not_found.html', {'token': studyNumber, 'type': 'Study'})

    e = Experiment.objects.filter(study=s.pk)
    return render(request, 'one_study.html', {'study': s, 'exp_list': e})


# edit_study -- update for new study fields
@login_required
def edit_study(request, studyNumber=''):
    if studyNumber!='':
        try:
            s=Study.objects.get(pk=int(studyNumber))
        except:
            s=None
    else:
        s=None
    # allow upload
    if request.method=="POST":
        study_form = StudyForm(request.POST, instance=s)
        if study_form.is_valid():
            s=study_form.save(commit=False)
            s.user=request.user.username
            try:
                consent=json.loads(s.consentJSON) # test the JSON parsing of the consent form info
            except:
                return render(request, 'bad_consent_form.html', {'consent': s.consentJSON})
            s.save()
            return redirect('one_study', studyNumber=s.pk)
        return HttpResponse("Bad study form")

    if s!=None:
        form=StudyForm(instance=s)
    else:
        form=StudyForm()

    return render(request,'edit_study.html', {'form': form})


# experiment() displays information on a single experiment including every session
@login_required
def one_experiment(request, expNumber=''):
    try:
        e = Experiment.objects.get(pk=int(expNumber))
    except:
        return render(request, 'Object_not_found.html', {'token': expNumber, 'type': 'Experiment'})

    s = Session.objects.filter(exp=e.pk)
    # construct list that follows the sessionlist in e.sessions, breaks up if numtokens>sessiontokens
    # extract order from session token string
    session_order={}
    count=0
    for i in e.groupSessions.split():
        session_order[i]=count
        count=count+1
    # create a sortable list of the Session objects
    token_order=[]
    for i in s:
        if i.lastStarted is None:
            d=timezone.make_aware(datetime(2, 1, 1, tzinfo = None), timezone.get_default_timezone())
        else:
            d=i.lastStarted
        if session_order.has_key(i.sessionToken):
            if session_order[i.sessionToken]<e.numTokens:
                token_order.append((0, d, i))
            else:
                token_order.append((1, d, i))
                #token_order.append((session_order[i.sessionToken],i))
        else:
            token_order.append((99999, d, i))
    if token_order!=[]:
        token_order.sort()
        (count_list, date_list, session_list)=zip(*token_order)
    else:
        session_list=[]

    study=e.study
    applet_url=request.build_absolute_uri(static(study.appletName))
    link=e.link_url(applet_url)
    return render(request, 'experiment_info.html', {'exp': e, 'tokens': token_order, 'order': session_order, 'sessions': session_list, 'parent': study, 'link': link})

@login_required()
def edit_experiment(request, expNumber='', studyNumber=''):
    if expNumber!='':
        try:
            e=Experiment.objects.get(pk=int(expNumber))
        except:
            return render(request, 'Object_not_found.html', {'token': expNumber, 'type': 'Experiment'})
    else:
        e=None

    try:
        parent_study=Study.objects.get(pk=int(studyNumber))
    except:
        return render(request, 'Object_not_found.html', {'token': studyNumber, 'type': 'Study'})

    # edit the experiment object
    if request.method=="POST":
        exp_form = ExperimentForm(request.POST, instance=e)
        if exp_form.is_valid():
            e=exp_form.save(commit=False)
            e.user=request.user.username
            e.study=parent_study
            e.create_token()
            e.save()
            return redirect('one_experiment', expNumber="%d" % e.pk)
        else:
            return render(request, 'Object_not_found.html', {'token': expNumber, 'type': 'Experiment creation'})

    if e:
        s = e.study
        form = ExperimentForm(instance=e)
    else:
        try:
            s=Study.objects.get(pk=int(studyNumber))
        except:
            return render(request, 'Object_not_found.html', {'token': studyNumber, 'type': 'Study'})
        form=ExperimentForm()

    return render(request,'edit_experiment.html', {'form': form,  'study': s})


# show_config() displays information on a single session
@login_required
def one_session(request, sessionToken):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    # Get any data reports on this session
    data_report = Report.objects.all().filter(sessionToken=sessionToken)
    return render(request, 'display_config.html', {'session': s, 'exp': s.exp, 'reports':data_report})

# to do: force link to existing experiment...
@login_required
def new_config(request, expNumber=''):
    try:
        e=Experiment.objects.get(pk=int(expNumber))
    except:
        return render(request, 'Object_not_found.html', {'token': expNumber, 'type': 'Experiment'})
    if request.method=="POST":
        # add the new config element to the db
        form=ConfigForm(request.POST)
        if form.is_valid():
            c=form.save(commit=False)
            c.exp=e
            c.make_token()
            c.save()
            # add to exp session list
            e.add_sessions(c.sessionToken)
            e.save()
            return redirect('one_session', sessionToken=c.sessionToken)
        else:
            return HttpResponse("Unable to parse config file edit")

    form=ConfigForm(initial={'sessionToken': 'None', 'exp': e})
    return render(request,'new_config.html', {'form': form, 'exp': e})

@login_required
def edit_config(request, sessionToken=''):
    try:
        c=Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'Object_not_found.html', {'token': sessionToken, 'type': 'Session'})
    if request.method=="POST":
        # add the new config element to the db
        form=ConfigForm(request.POST, instance=c)
        if form.is_valid():
            c = form.save()
            # return render(request, 'display_config.html', {'session': c, 'reports':None})
            return redirect('one_session', sessionToken=c.sessionToken)
        else:
            return HttpResponse("Unable to parse config file edit")

    # display form to create config -- to do: if sessionToken!='', include that information in the form; allow copy as well as edit links on config view
    form=ConfigForm(instance=c)
    return render(request,'new_config.html', {'form': form, 'sessionToken': sessionToken})

@login_required
def copy_config(request,sessionToken):
    try:
        s=Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'Object_not_found.html', {'token': sessionToken, 'type': 'Session'})

    # add _c to the name to indicate copy
    new_name=s.name+'_c'
    new_cfg=Session.objects.create_session(new_name,s.exp,s.configFile,request.user.username)

    # increase the session token count in the experiemnt
    new_cfg.exp.add_sessions(new_cfg.sessionToken)
    new_cfg.exp.save()

    # copy is probably going to be called as part of an edit, so jump to the edit form (name can be edited here too)
    return redirect('edit_config', sessionToken=new_cfg.sessionToken)

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


# rewrite --
#
# @login_required
# def make_link_tokens(request, token):
#     sessionToken=token
#     try:
#         exp_name=Session.objects.get(sessionToken=sessionToken).expName
#     except:
#         return render(request, 'session_not_found_error.html', {'token': sessionToken})
#
#     all_sessions=Session.objects.all().filter(expName=exp_name).order_by('creationDate')  # oldest first
#     # Check to see if there is a data report for the token, skip if so
#     sessions=[]
#     skip_sessions=[]
#     for s in all_sessions:
#         data_report = Report.objects.all().filter(sessionToken=s.sessionToken)
#         if not data_report.exists():
#             sessions.append(s)
#         else:
#             skip_sessions.append(s)
#
#     if request.method=="POST":
#         log_list=[]
#         adding_to_existing=False
#         form=TokenForm(request.POST)
#         if form.is_valid():
#             # to do -- create individual session tokens with workerid=names from participantList
#             if form.cleaned_data['priorTokens']>0:
#                 # add sessions to previous token group
#                 log_list.append("Adding to token event %d" % form.cleaned_data['priorTokens'].pk)
#                 tc=form.cleaned_data['priorTokens']
#                 adding_to_existing = True
#                 # tc.groupSessions=tc.groupSessions+' '
#                 # set numTokens to current addition, totalTokens to length of list -- ?
#             else:
#                 log_list.append("Created token event")
#                 tc=form.save(commit=False)
#                 tc.user=request.user
#                 tc.expName=exp_name
#                 tc.create_token()
#                 tc.groupSessions=''
#             log_list.append("Group token %s" % tc.groupToken)
#             #if settings.FORCE_EXTERNAL_APP_LINKS:
#             #    groupURL="https://www.reberlab.org/"+static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken))
#             #else:
#             #    groupURL=request.build_absolute_uri(static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken)))
#             # the list of session tokens gets assembled here
#             session_list=[]
#             for s in sessions:
#                 log_list.append("Found session %s" % s.sessionToken)
#                 session_list.append(s.sessionToken)
#
#             # if add used, include sessions with data
#             if form.cleaned_data['readd_used']:
#                 for s in skip_sessions:
#                     log_list.append("Found session %s" % s.sessionToken)
#                     session_list.append(s.sessionToken)
#
#             # if add all
#             if not form.cleaned_data['add_all']:
#                 session_list = session_list[:form.cleaned_data['numTokens']]
#                 log_list.append("Truncated to %d" % len(session_list))
#             else:
#                 log_list.append("All sessions included")
#
#             # if adding, put new cfgs at front of list
#             if adding_to_existing:
#                 tc.groupSessions=' '.join(session_list)+' '+tc.groupSessions
#             else:
#                 tc.groupSessions=' '.join(session_list)
#             tc.totalTokens=len(tc.groupSessions.split())
#
#             # if restrict to new
#             if form.cleaned_data['restrict_to_new']:
#                 tc.numTokens=len(session_list)
#                 log_list.append("Restricting to %d new tokens" % tc.numTokens)
#             else:
#                 tc.numTokens=tc.totalTokens
#
#             # participant list
#             # create url list -- need definition of app syntax for workerid/name
#             # create workerid tokens
#             # add to Study participant ids?
#
#             tc.save()
#
#             # if AWS credentials, upload HITs
#             #if form.cleaned_data['mturk_key_id']!='' and form.cleaned_data['mturk_secret_key']!='':
#             #    log+=mTurkHITs((form.cleaned_data['mturk_key_id'],form.cleaned_data['mturk_secret_key']),groupURL,tc.numTokens,
#             #                  form.cleaned_data['mturk_title'],form.cleaned_data['mturk_description'],
#             #                  form.cleaned_data['mturk_frame_size'],form.cleaned_data['mturk_amount'])
#             #    log+="Finished mTurkHITs;"
#             # if email address list (and no mturk -- don't mix), send emails
#             #elif form.cleaned_data['emailList']!='':
#             #    log+=emailInvites(form.cleaned_data['emailList'],session_list)
#             #else:
#             log_list.append("Completed")
#
#             # log token creation events for all new links -- new 9/2/2015
#             for s in session_list:
#                 add_token_creation_event(s,form.cleaned_data['studyName'])
#         else:
#             log=['Invalid Form']
#             return render(request, 'link_tokens.html', {'app': 'None', 'groupToken': 'None', 'tokens': [], 'log': log})
#         tokenURL=request.build_absolute_uri(static("%s?group=%s" % (form.cleaned_data['appletName'],tc.groupToken)))
#         # participant list from Study
#         if tc.studyName!=None:
#             studyName=tc.studyName
#             prior_ps=tc.studyName.participants.split()
#         else:
#             studyName=None
#             prior_ps=''
#         # list of data events in tokens should be null
#         session_list=tc.groupSessions.split()
#         session_data=[]
#         num_available=0
#         for s in session_list:
#             num_events=len(Report.objects.all().filter(sessionToken=s))
#             session_data.append((s,num_events))
#             if num_events < 2:
#                 num_available=num_available+1
#
#         return render(request, 'link_tokens.html', {'app': form.cleaned_data['appletName'],
#                                                     'groupToken': tc.groupToken,
#                                                     'groupTokenURL': tokenURL,
#                                                     'study': studyName,
#                                                     'excluded': prior_ps,
#                                                     'tokens': session_data,
#                                                     'status': (tc.numTokens,tc.totalTokens,num_available),
#                                                     'log': log_list})
#
#     previous=TokenGeneration.objects.all().filter(expName=exp_name).order_by('-creationDate')
#     previous_token_links=[]
#     if not previous.exists():
#         form = TokenForm()
#     else:
#         for t in previous:
#             if t.groupToken!=None: # shouldn't happen unless there was a bug and malformed group token event
#                 previous_token_links.append(t)
#         form = TokenForm(initial={'appletName': previous[0].appletName})
#                                   #'mturk_amount': previous[0].mturk_amount,
#                                   #'mturk_frame_size': previous[0].mturk_frame_size,
#                                   #'mturk_title': previous[0].mturk_title,
#                                   #'mturk_description': previous[0].mturk_description})
#         form.fields['priorTokens'].queryset = previous
#     return render(request, 'link_token_form.html', {'form': form, 'exp_name': exp_name, 'sessions': sessions, 'skipped':skip_sessions,
#                                                     'priorLinks': previous_token_links})
# # group token info and status
# # deprecated -- exp view replaces...
# @login_required
# def group_token(request, token):
#     groupToken=token
#     try:
#         g=TokenGeneration.objects.get(groupToken=groupToken)
#     except:
#         return render(request, 'session_not_found_error.html', {'token': groupToken})
#
#     tokenURL=request.build_absolute_uri(static("%s?group=%s" % (g.appletName,g.groupToken)))
#     sessionTokens=g.groupSessions.split()
#
#     # to do -- indicate recycle status
#
#     # study participants
#     Study=g.studyName
#     if Study!=None:
#         studyName=Study
#         prior_ps=Study.participants.split()
#     else:
#         studyName=None
#         prior_ps=[]
#
#     session_data=[]
#     num_available=0
#     for s in sessionTokens:
#         num_events=len(Report.objects.all().filter(sessionToken=s))
#         session_data.append((s,num_events))
#         if num_events < 2:
#             num_available=num_available+1
#
#     return render(request, 'link_tokens.html', {'app': g.appletName,
#                                                 'groupToken': groupToken,
#                                                 'groupTokenURL': tokenURL,
#                                                 'tokens': session_data,
#                                                 'study': studyName,
#                                                 'excluded': prior_ps,
#                                                 'status': (len(sessionTokens),num_available),
#                                                 'log': []})
#


# What calls this rendered list of security reports? -- PJR
def security_list(request):
    # show all security events in the db
    s=Security.objects.all()
    return render(request, 'security_event_list.html', {'event_list':s})

# Potential admin/cleanup views
# 1. Find/correct orphan sessions
# 2. Find/correct orphan experiments
# 3. Participant list formatting change to workerid:session
# 4. Checking for non UTF-8 strings in db?  Is this possible?
# 5. Review/delete the contents of zip_tmp

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from exp.models import Session, Report, ReportForm, Study, StudyForm, Security, ConfigForm, Experiment, ExperimentForm, Participant, ParticipantForm
from filer.models import Filer
from datetime import date, datetime
import time

import json
import operator
from django.templatetags.static import static

from .app_views import *
from .data_views import *

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
def one_study(request, studyNumber=0):
    try:
        s = Study.objects.get(pk=studyNumber)
    except:
        return render(request, 'Object_not_found.html', {'token': studyNumber, 'type': 'Study'})

    e = Experiment.objects.filter(study=s.pk)
    # sort this to group by experimenter
    exp_list=[]
    if e.exists():
        for i in e:
            exp_list.append([i.user,i.pk,i])
        exp_list.sort()
        (users, pkids, exp_list) = zip(*exp_list)
    return render(request, 'one_study.html', {'study': s, 'exp_list': exp_list})


# edit_study -- update for new study fields
@login_required
def edit_study(request, studyNumber=0):
    if studyNumber!=0:
        try:
            s=Study.objects.get(pk=studyNumber)
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
def one_experiment(request, expNumber=0):
    try:
        e = Experiment.objects.get(pk=expNumber)
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
        if i.sessionToken in session_order:
            if session_order[i.sessionToken]<e.numTokens:
                token_order.append((0, d, i))
            else:
                token_order.append((1, d, i))
        else:
            token_order.append((99999, d, i))
    if token_order!=[]:
        token_order.sort(key=operator.itemgetter(0,1))
        (count_list, date_list, session_list)=zip(*token_order)
    else:
        session_list=[]

    study=e.study
    # Check if applet is in the file db
    if Filer.objects.filter(filename=study.appletName).exists():
        applet_url='http://%s/file/show/%s' % (request.get_host(),study.appletName)
    else:
        applet_url=request.build_absolute_uri(static(study.appletName))
    link=e.link_url(applet_url)
    return render(request, 'experiment_info.html', {'exp': e, 'sessions': session_list, 'parent': study, 'link': link})

@login_required()
def edit_experiment(request, expNumber=0, studyNumber=0):
    if expNumber!=0:
        try:
            e=Experiment.objects.get(pk=expNumber)
        except:
            return render(request, 'Object_not_found.html', {'token': expNumber, 'type': 'Experiment'})
    else:
        e=None

    if e:
        parent_study=e.study
    else:
        try:
            parent_study=Study.objects.get(pk=studyNumber)
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
def new_config(request, expNumber=0):
    try:
        e=Experiment.objects.get(pk=expNumber)
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

# What calls this rendered list of security reports? -- PJR
def security_list(request):
    # show all security events in the db
    s=Security.objects.all()
    return render(request, 'security_event_list.html', {'event_list':s})


# Participant table views

# URL redirects -- participant/ (=all) (participants.html)
#  -- participant/<tag> (one_participant.html)
# -- updateparticipants (participant_db_report.html)

@login_required
def participant_table(request):
    # show all the participants with links to edit by form
    # show abbreviated list of data links?
    p = Participant.objects.all()
    return render(request, 'participants.html', {'p':p })

# this shouldn't be called with name==''...
@login_required
def one_participant(request, name=''):
    # show/edit single participant record
    try:
        p=Participant.objects.get(tag=name)
    except:
        return render(request, 'Object_not_found.html', {'token': name, 'type': 'Participant'})

    if request.method=="POST":
        # add the new config element to the db
        form=ParticipantForm(request.POST, instance=p)
        if form.is_valid():
            c = form.save()
            # return render(request, 'display_config.html', {'session': c, 'reports':None})
            return redirect('one_participant', name=p.tag)
        else:
            return HttpResponse("Unable to parse Participant form edit")

    # form collects the participant data from the db
    form=ParticipantForm(instance=p)
    # collect links to all their data records
    data=Report.objects.filter(workerId=p.tag)

    return render(request,'one_participant.html', {'p': p, 'form': form, 'data': data})

# Log all the creations and report - ?
@login_required
def participants_update(request):
    # check data table and find all participants not represented in the participant db and add them
    log=[]
    r=Report.objects.all()
    counts=[0,0,0]
    for i in r:
        if i.workerId!='' and \
                i.workerId[:4].casefold()!='None'.casefold() and \
                i.workerId[:4].casefold()!='NoId'.casefold():
            # this is a real workerId
            try:
                # if this succeeds, the participant is already in the db
                p = Participant.objects.get(tag=i.workerId)
                log.append("Matched: %s" % i.workerId)
                counts[1]=counts[1]+1
            except:
                # create new participant record
                p = Participant.objects.create(tag=i.workerId)
                p.save()
                log.append("Added: %s" % i.workerId)
                counts[2]=counts[2]+1
        else:
            counts[0]=counts[0]+1
    log.sort()
    return render(request,'participant_db_update.html', {'log': log, 'counts': counts})


# Potential admin/cleanup views
# 1. Find/correct orphan sessions
# 2. Find/correct orphan experiments
# 3. Participant list formatting change to workerid:session
# 4. Checking for non UTF-8 strings in db?  Is this possible?
# 5. Review/delete the contents of zip_tmp

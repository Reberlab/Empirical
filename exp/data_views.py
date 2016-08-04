from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

# to allow for reading non-ascii strings from the db without crashing
from django.db import connection

from exp.models import Session, Report, Experiment, Study
from datetime import date
import time

import zipfile, os.path
from django.conf import settings
from django.core.files import File

#url(r'^data/(?P<studyNumber>[0-9a-z]+)$', views.study_data, name='study_data'),
#url(r'^data/exp/(?P<expNumber>[0-9a-z]+)$', views.experiment_data, name='experiement_data'),
#url(r'^data/session/(?P<sessionToken>[0-9a-z]+)$', views.session_data, name='session_data'),
#url(r'^data/session/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9a-z]+)$', views.session_data, name='session_data'),
#url(r'^data/file/exp/(?P<expNumber>[0-9a-z]+)$', views.download_exp_data, name='download_experiement'),
#url(r'^data/file/session/(?P<sessionToken>[0-9a-z]+)$', views.download_session_data, name='download_session'),
#url(r'^data/file/session/(?P<sessionToken>[0-9a-z]+)/(?P<pkid>[0-9a-z]+)$', views.download_session_data,
#    name='download_session'),

@login_required
def session_data(request, sessionToken, pkid=''):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'Object_not_found.html', {'token': sessionToken, 'type': "Session token"})

    if pkid!='':
        data_report = Report.objects.filter(pk=int(pkid))
    else: # assume we should show all the data for the experiment
        data_report = Report.objects.filter(sessionToken=sessionToken)

    return render(request, 'display_data.html', {'session': s, 'reports': data_report})

@login_required
def download_session_data(request, sessionToken, pkid=''):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    report_contents=''
    if pkid!='':
        data_report = Report.objects.filter(sessionToken=sessionToken,pk=int(pkid))
        report_contents=data_report[0].dataLog
    else:
        r = Report.objects.filter(sessionToken=sessionToken)
        for i in r:
            header="Data record: %d\nSessionToken: %s\nUpload date: %s\n" % (i.pkid,i.sessionToken,i.uploadDate)
            report_contents=report_contents+header+i.dataLog+"\n\n"

    if report_contents!='':
        output_filename="%s_data_%s_%s.txt" % (s.exp.name,date.today().strftime("%d%b%Y"),pkid)
        response=HttpResponse(report_contents,content_type='text/plain')
        response['Content-Disposition'] = "attachment; filename=%s" % output_filename
        return response
    return render(request, 'Object_not_found.html', {'token': sessionToken, 'type': "Data records"})

# to do -- use experiment_info.html, edit it to render with and without the data column on the table
#  -- include time to render in output

@login_required
def experiment_data(request, expId):
    try:
        e = Experiment.objects.get(pk=int(expId))
    except:
        return render(request, 'Object_not_found.html', {'token': expId, 'type': "Experiment"})

    s = Session.objects.filter(exp=e)
    reports=[]
    event_types=[]
    for i in s:
        r = Report.objects.filter(sessionKey=i)
        for j in r:
            reports.append([i.sessionToken,j.pk,j.eventType,j.uploadDate,j.dataLog[:256]])
            if j.eventType not in event_types:
                event_types.append(j.eventType)
    event_types.sort()
    return render(request, 'display_exp_data.html', {'exp': e, 'reports': reports, 'parent': e.study, 'events': event_types})

# study_data

@login_required
def study_data(request, studyId=''):
    start = time.time()
    try:
        s = Study.objects.get(pk=int(studyId))
    except:
        return render(request, 'Object_not_found.html', {'token': studyId, 'type': "Study"})

    e = Experiment.objects.filter(study=s.pk)
    count=[]
    for i in e:
        exp_count=0
        sessions = Session.objects.filter(exp=i)
        for j in sessions:
            exp_count=exp_count + Report.objects.filter(sessionKey=j).count()
        count.append(exp_count)
    done = time.time()
    report_string="Time to count data: %.2fs" % (done-start)
    return render(request, 'study_data.html', {'study': s, 'exp_list': zip(e,count), 'log': report_string})


# construct a unique .txt file output name
def unique_txt(fn_list,cfg_name,event_type):
    base=os.path.splitext(cfg_name)[0]
    fn="%s_%s.txt" % (base,event_type)
    count=0
    while (fn in fn_list):
        count=count+1
        fn="%s_%s_%d.txt" % (base,event_type,count)
    return fn

# bulk data download for an entire experiment -- to do, update for new exp structure
@login_required
def download_exp_data(request, expId, reportType=''):
    try:
        # s = Session.objects.get(sessionToken=sessionToken)
        e = Experiment.objects.get(pk=int(expId))
    except:
        return render(request, 'Object_not_found.html', {'token': expId, 'type': "Experiment"})

    count=0 # for duplicate filenames
    fn="%s_data_%s.zip" % (e.name,date.today().strftime("%d%b%Y"))
    output_filename=os.path.join(settings.MEDIA_ROOT, settings.ZIP_TMP, fn)
    while os.path.exists(output_filename) and count<100:
        count=count+1
        fn="%s_data_%s_%d.zip" % (slugify(e.name),date.today().strftime("%d%b%Y"),count)
        output_filename=os.path.join(settings.MEDIA_ROOT, settings.ZIP_TMP, fn)
    if count==100:
        return HttpResponse('Error creating output file')

    output_zip=zipfile.ZipFile(output_filename, 'w')
    fn_list=[] # for tracking duplicate filenames in the output zip
    s = Session.objects.filter(exp=e)
    for i in s:
        r = Report.objects.filter(sessionKey=i)
        for j in r:
            # reports should match type if set, contents length >0
            if (reportType=='' or j.eventType==reportType) and len(j.dataLog.strip())>0:
                    fn=unique_txt(fn_list,e.name,j.eventType)
                    output_zip.writestr(fn,j.dataLog.encode("ascii",'ignore'))
                    fn_list.append(fn)

    output_zip.close()
    f=open(output_filename,'rb')
    response = HttpResponse(File(f),content_type='application/zip')
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(output_filename)
    response['Content-Length'] = os.path.getsize(output_filename)
    return response

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# to allow for reading non-ascii strings from the db without crashing
from django.db import connection

from exp.models import Session, Report, Experiment_desc
from datetime import date, datetime

import zipfile, os.path
from django.conf import settings
from django.core.files import File

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

    # patching the db read to avoid crashing on non-ascii characters
    #connection.cursor()
    #connection.connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")

    E=Experiment_desc(r.expName)
    output_zip=zipfile.ZipFile(output_filename, 'w')
    fn_list=[] # for tracking duplicate filenames in the output zip
    for s in E.cfg_list:
        # s[0]=name, s[1]=sessionToken, s[2]=list of report objects
        report_list=Report.objects.all().filter(sessionToken=s[1])
        for r in report_list:
            if len(r.dataLog.strip())>0: # only save events with some data -- the empty ones should be 'start' reports
                fn=unique_txt(fn_list,s[0],r.eventType)
                output_zip.writestr(fn,r.dataLog.encode("ascii",'ignore'))
                fn_list.append(fn)

    output_zip.close()
    f=open(output_filename,'rb')
    response = HttpResponse(File(f),content_type='application/zip')
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(output_filename)
    response['Content-Length'] = os.path.getsize(output_filename)
    return response
    # filter by keywords like partial/complete?
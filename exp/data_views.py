from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

# to allow for reading non-ascii strings from the db without crashing
from django.db import connection

from exp.models import Session, Report, Experiment, Download
from datetime import date

import zipfile, os.path
from django.conf import settings
from django.core.files import File

from exp.app_views import xml_string
import xml.etree.ElementTree as ET
xml_namespace= {'Empirical': 'https://www.reberlab.org/'}


def encode_datalog(r):
    header="RecordId: %d\nSessionToken: %s\nUploadDate: %s\n" % (r.pk, r.sessionToken, r.uploadDate)
    if "<root xmlns:Empirical=" in r.dataLog:
        # parse XML, add header information, return
        d = ET.fromstring(r.dataLog)
        ET.register_namespace("Empirical", 'https://www.reberlab.org/')
        h = ET.Element("Empirical:recorddata")
        h.text = header
        d.append(h)
        return(ET.tostring(d))
    data_xml={}
    data_xml['Empirical:recorddata'] = header
    data_xml['Empirical:datalog'] = r.dataLog.encode('ascii','ignore')
    return(xml_string(data_xml))

# Displays a single record on a web page
@login_required
def session_data(request, sessionToken, pkid=0):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'Object_not_found.html', {'token': sessionToken, 'type': "Session token"})

    if pkid!=0:
        data_report = Report.objects.filter(pk=pkid)
    else: # assume we should show all the data for the experiment
        data_report = Report.objects.filter(sessionToken=sessionToken)

    return render(request, 'display_data.html', {'session': s, 'reports': data_report})

# Downloads one or more records from a session reference
@login_required
def download_session_data(request, sessionToken='', pkid=0):
    try:
        s = Session.objects.get(sessionToken=sessionToken)
    except:
        return render(request, 'session_not_found_error.html', {'token': sessionToken})

    report_contents=''
    if pkid!=0: # download a single datafile, XML wrapped
        data_report = Report.objects.filter(sessionToken=sessionToken,pk=pkid)
        report_contents=encode_datalog(data_report[0])
    else: # download all the data associated with a session/cfg, not XML wrapped
        r = Report.objects.filter(sessionToken=sessionToken)
        for i in r:
            header="Data record: %d\nSessionToken: %s\nUpload date: %s\n" % (i.pkid,i.sessionToken,i.uploadDate)
            report_contents=report_contents+header+i.dataLog+"\n\n"

    if report_contents!='':
        output_filename="%s_data_%s_%d.txt" % (s.exp.name,date.today().strftime("%d%b%Y"),pkid)
        response=HttpResponse(report_contents,content_type='text/plain')
        response['Content-Disposition'] = "attachment; filename=%s" % output_filename
        return response
    return render(request, 'Object_not_found.html', {'token': sessionToken, 'type': "Data records"})

# Displays a list of records from an experiment, web page
@login_required
def experiment_data(request, expNumber):
    try:
        e = Experiment.objects.get(pk=expNumber)
    except:
        return render(request, 'Object_not_found.html', {'token': expNumber, 'type': "Experiment"})

    s = Session.objects.filter(exp=e)
    event_types=[]
    log=""
    reports=[]
    r = Report.objects.filter(sessionKey__in=s) # a "Q-form" to get all the reports for all sessions keys
    for j in list(r.order_by('-uploadDate')): # sort into reverse date order
        log=log+(" added %d; " % j.pk)
        reports.append([j.sessionToken,j.pk,j.eventType,j.appNameVer(),j.workerId,j.uploadDate,j.dataLog[:256]])
        if j.eventType not in event_types:
            event_types.append(j.eventType)
    event_types.sort()
    # list download objects
    d=Download.objects.filter(experiment=e)

    return render(request, 'display_exp_data.html', {'exp': e, 'reports': reports,
                                                     'parent': e.parent_study, 'events': event_types,
                                                     'downloads': d, 'log': log})

# construct a unique .txt file output name
def unique_txt(fn_list,cfg_name,event_type):
    base=os.path.splitext(cfg_name)[0]
    fn="%s_%s.txt" % (base,event_type)
    count=0
    while (fn in fn_list):
        count=count+1
        fn="%s_%s_%d.txt" % (base,event_type,count)
    return fn

# Bulk data download for an entire experiment
# Todo: insert XML formatting for record information (if XML), add header if not XML
#  Make filenames not repeat for download since

@login_required
def download_exp_data(request, expNumber, reportType='', since=0):
    try:
        # s = Session.objects.get(sessionToken=sessionToken)
        e = Experiment.objects.get(pk=expNumber)
    except:
        return render(request, 'Object_not_found.html', {'token': expNumber, 'type': "Experiment"})

    # if since!=0, get the download object we are working from
    if since>0:
        try:
            prior_download=Download.objects.get(pk=since)
        except:
            return render(request, 'Object_not_found.html', {'token': since, 'type': "Download"})

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
    #fn_list=[] # for tracking duplicate filenames in the output zip
    count=0
    s = Session.objects.filter(exp=e)
    basename=slugify(e.name)
    for i in s:
        r = Report.objects.filter(sessionKey=i)
        # if since is set, check dates
        for j in r:
            # reports should match type if set, contents length >0
            if (reportType=='' or j.eventType==reportType) and len(j.dataLog.strip())>0:
                if since==0 or j.uploadDate>prior_download.downloadDate:
                    #fn=unique_txt(fn_list,e.name,j.eventType)
                    fn="%s_%s_%d.txt" % (basename,j.eventType,j.pk)
                    output_zip.writestr(fn,encode_datalog(j))  #dataLog.encode("ascii",'ignore'))
                    #fn_list.append(fn)
                    count=count+1

    output_zip.close()

    # Create download object
    if reportType=='':
        reportType='All'
    if since==0:
        since_str='All'
    else:
        since_str=prior_download.downloadDate.ctime()
    d=Download.objects.create(experiment=e,event_type=reportType,num_records=count,filename=os.path.basename(output_filename),downloadSince=since_str)

    f=open(output_filename,'rb')
    response = HttpResponse(File(f),content_type='application/zip')
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(output_filename)
    response['Content-Length'] = os.path.getsize(output_filename)
    return response

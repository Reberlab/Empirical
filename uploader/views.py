from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from uploader.models import ZipUpload, ZipUploadForm, ExpImage, UploadEvent, UploadEventForm
from exp.models import Session

# for unpacking archives
from django.conf import settings
from django.contrib.auth.decorators import login_required
import zipfile, os.path

def is_image_file(fn):
    # Just checking by filename extension
    ext=os.path.splitext(fn)[1]
    if ext in ['.jpg','.png','.gif','.ppm', '.GIF', '.JPG', '.PNG', '.PPM']:
        return True
    return False

# If request.method == POST, then this is being called with a filled form to be processed
#  Otherwise, post the form to be filled in

# to do: fix expName connection/syntax
#  remove 'copies' in upload and upload review
#  create Experiment object for new .zip uploads containing non-image files

@login_required
def index(request):
    if request.method=="POST":
        zip_form = ZipUploadForm(request.POST, request.FILES)
        if zip_form.is_valid():
            original_filename=os.path.splitext(os.path.basename(request.FILES['zip'].name))[0]
            z=zip_form.save(commit=False)
            z.group=original_filename
            z.upload_user=request.user
            z.save()
            # pull the exp name, list of files and file types, render via uploader_review
            # and form to modify...
            # parse out filenames into list
            zf = zipfile.ZipFile(z.zip.path)    # this needs fault tolerance -- if not .zip treat as cfg, or fail gracefully
            file_list = zf.infolist()
            cfgList=[]
            imgList=[]
            for f in file_list:
                if is_image_file(f.filename):
                    imgList.append(f.filename)
                else:
                    cfgList.append(f.filename)
            confirmForm=UploadEventForm(initial={'sourceFile':z.pk, 'expName':z.group, 'repetitions':1}) # fill in default values
            return render(request, 'uploader_review.html', {'source': z.pk, 'expName':z.group, 'cfgList':cfgList, 'imgList':imgList, 'form':confirmForm} )

    upload_form=ZipUploadForm()
    file_list=ZipUpload.objects.all().order_by('-upload_date')
    image_list=ExpImage.objects.all()
    # group image_list by the .group tags
    image_groups={}
    for i in image_list:
        if i.group in image_groups.keys():
            image_groups[i.group][2].append(i.filename)
        else:
            image_groups[i.group]=[i.upload_user, i.upload_date, [i.filename]]
    return render(request, 'uploader_index.html',{'form':upload_form, 'zip_list':file_list, 'image_groups':image_groups, 'user':request.user})

@login_required
def unpack_review(request):
    if request.method=="POST":
        form = UploadEventForm(request.POST)
        if form.is_valid():
            zip=form.cleaned_data['sourceFile']
            expName=form.cleaned_data['expName']
            reps=form.cleaned_data['repetitions']

            # set up a log for unpacking actions, unpack the zip file and store
            unpack_log=[]
            p = get_object_or_404(ZipUpload, pk=zip.pk)
            try:
                fn = p.zip.path
            except:
                unpack_log.append("No zipfile %d" % zip.pk)
                return render(request, 'uploader_unpack.html', {'log': unpack_log, 'user':request.user})

            # Use a template to construct the report
            unpack_log.append("Found zipfile %d, %s" % (zip.pk,fn))
            zf = zipfile.ZipFile(fn)
            file_list = zf.infolist()
            for f in file_list:
                unpack_log.append("--- File: %s" % f.filename)

            output_dir=os.path.join(os.path.dirname(settings.MEDIA_ROOT),p.group)

            experiment_name=p.group
            if expName!='':  # override if new name passed in
                experiment_name=expName

            unpack_log.append("Added to experiment: %s" % experiment_name)
            if reps>1:
                unpack_log.append("Adding %d repetitions" % reps)

            for f in file_list:
                if is_image_file(f.filename): # unpack and store in MEDIA directory (/images)
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir)
                        unpack_log.append("Created output directory %s" % output_dir)
                    if not os.path.exists(os.path.join(output_dir,f.filename)):
                        zf.extract(f,output_dir)
                        unpack_log.append("Extracting image file %s to %s" % (f.filename,output_dir))
                        img = ExpImage.objects.create(filename=f.filename,group=experiment_name,upload_user=request.user)
                    else:
                        unpack_log.append("Not extracting image file %s, already exists" % f.filename)
                else: # non-image files are assumed to be config files, extract to memory and store in session db
                    fp = zf.open(f.filename)
                    raw_cfg=fp.read()
                    cfg=raw_cfg.encode('utf-8','ignore') # to avoid getting db breaking characters stored by accident
                    fp.close()
                    for i in range(reps):
                        e = Session.objects.create_session(name=f.filename,configFile=cfg,expName=experiment_name)
                        unpack_log.append("Added config file %s to experiment %s" % (f.filename,experiment_name))
            # Display unpacking log
            return render(request, 'uploader_unpack.html', {'log': unpack_log, 'user':request.user})

    return render(request, 'uploader_error')

def uploader_error(request):
    return render(request, 'uploader_error.html')







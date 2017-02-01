from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.text import slugify

from filer.models import Filer, EncryptKey, FileUploadForm, ZipUpload, ZipUploadForm, ImageUploadForm, ExpImage
#from uploader.models import ZipUpload, ZipUploadForm, ExpImage, UploadEvent, UploadEventForm
from exp.models import Study, Experiment, Session

# for unpacking archives
import zipfile, os.path, glob


# show the list of available files in the db
@login_required
def filer_index(request):
    # database file list
    f=Filer.objects.all()

    # media directories
    media_list = glob.glob(os.path.join(os.path.dirname(settings.MEDIA_ROOT), "*"))

    dir_list=[]
    zip_list=[]
    for i in media_list:
        if os.path.isdir(i):
            if os.path.split(i)[-1]=='zip_tmp':
                # ziptmp contents
                zip_list=glob.glob(os.path.join(i,"*"))
            else:
                image_list=[os.path.basename(fn) for fn in glob.glob(os.path.join(i,"*"))]
                dir_list.append((os.path.basename(i),image_list))

    return render(request, 'filer_index.html', {'file_list': f, 'media': dir_list, 'tmp': zip_list})

# upload file to db
@login_required
def filer_add(request):
    if request.method=="POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # add username
            f=form.save(commit=False)
            f.upload_user=request.user
            f.save()
            return
        else:
            return

    upload_form=FileUploadForm()
    return render(request, 'filer_upload.html', {'form': upload_form})

# create encryption key, add
@login_required
def filer_encrypt(request):
    return render(request, 'filer_index.html')

# return the raw file via http
@login_required
def filer_serve(request):
    return render(request, 'filer_index.html')

# rename, delete, copy?
@login_required
def filer_manage(request):
    return render(request, 'filer_index.html')

@login_required
def filer_ziptmp(request):
    return render(request, 'filer_cleanup.html')

def is_image_file(fn):
    # Just checking by filename extension
    ext=os.path.splitext(fn)[1]
    if ext in ['.jpg','.png','.gif','.ppm', '.GIF', '.JPG', '.PNG', '.PPM']:
        return True
    return False

#class ImageUpload(forms.Form):
#    zip=forms.FileField() #upload_to=settings.ZIP_TMP
#    image_dir = forms.CharField(max_length=100)
#    image_dir_choice = forms.ChoiceField()

@login_required
def upload_images(request):
    if request.method=="POST":
        # unpack & upload
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            original_filename=os.path.splitext(os.path.basename(request.FILES['zip'].name))[0]
            z=form.save(commit=False)
            z.group=original_filename
            z.upload_user=request.user
            z.save()

            try:
                zf = zipfile.ZipFile(z.zip.path)  # this needs fault tolerance -- if not .zip treat as cfg, or fail gracefully
            except:
                return HttpResponse("Uploaded file not .zip archive, %s, %s" % (original_filename, request.FILES['zip'].name))

            file_list = zf.infolist()
            if form.cleaned_data['image_dir']=='':
                if form.cleaned_data['image_dir_choice']!='None':
                    output_dir=form.cleaned_data['image_dir_choice']
                return HttpResponse("Error: No directory specified to upload to.")
            else:
                output_dir=form.cleaned_data['image_dir']

            unpack_log=[]
            # make output_dir if necessary
            output_dir=os.path.join(os.path.dirname(settings.MEDIA_ROOT),output_dir)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
                unpack_log.append("Created output directory %s" % output_dir)
            else:
                unpack_log.append("Directory %s exists, not created" % output_dir)

            # uncompress image files and store if they don't exist
            for f in file_list: # note -- no checking on image file type, this will also upload arbitratry files
                fn = os.path.basename(f.filename)
                if fn == '' or fn[0] == '_' or fn[0] == '.' or fn[-1] == '/':
                    unpack_log.append("Not extracting file %s" % f.filename)
                else:
                    output_file = os.path.join(output_dir, fn)
                    if os.path.exists(output_file):
                        unpack_log.append("Not extracting %s, exists" % f.filename)
                    else :
                        # zf.extract(f, output_dir)
                        unpack_log.append("Extracting image file %s to %s" % (fn, output_dir))
                        file_contents = zf.read(f)
                        fp = open(output_file, "wb")
                        fp.write(file_contents)
                        fp.close()

            return render(request,'upload_report.html', {'log': unpack_log, 'exp': None})
        else:
            return HttpResponse("Invalid form, %s" % form.errors)

    # render form
    dirs = glob.glob(os.path.join(os.path.dirname(settings.MEDIA_ROOT), "*"))
    dir_choices=[('None', '------------')]
    for i,fn in enumerate(dirs):
        if os.path.isdir(fn) and os.path.basename(fn)!='zip_tmp':
            dir_choices.append((os.path.basename(fn),os.path.basename(fn)))

    form = ImageUploadForm()
    form.fields['image_dir_choice'].widget = forms.Select(choices=dir_choices)
    return render(request,"upload_images.html", {'form': form, 'dirs': dirs, 'ch':dir_choices})

# initial form to set study that cfgs will be associated with

class SelectStudy(forms.Form):
    studyNum=forms.ModelChoiceField(queryset=Study.objects.all(),label='Associated Study',required=True)

@login_required
def prep_upload(request):
    if request.method=="POST":
        upload_form = SelectStudy(request.POST)
        if upload_form.is_valid():
            # get experiment list to select from for uploading cfgs
            s = upload_form.cleaned_data['studyNum']
            return redirect('upload_sessions', studyNumber = s.pk)

        return HttpResponse("Bad Study Selection Form")

    form = SelectStudy()
    return render(request, 'upload_select_study.html', {'form': form})

@login_required
def upload_zip(request, studyNumber='', expNumber=''):

    if request.method=="POST":
        # pass study number as hidden form field

        zip_form = ZipUploadForm(request.POST, request.FILES)
        if zip_form.is_valid():
            original_filename=os.path.splitext(os.path.basename(request.FILES['zip'].name))[0]
            z=zip_form.save(commit=False)
            z.group=original_filename
            z.upload_user=request.user
            z.save()

            unpack_log=[]
            try:
                zf = zipfile.ZipFile(z.zip.path)    # this needs fault tolerance -- if not .zip treat as cfg, or fail gracefully
            except:
                return HttpResponse("Uploaded file not .zip archive, %s, %s" % (original_filename, z.zip.path))

            file_list = zf.infolist()
            s=zip_form.cleaned_data['study']

            # output_dir is for images, either it is selected, entered or derived from study
            if zip_form.cleaned_data['image_dir']=='':
                if zip_form.cleaned_data['image_dir_choice']!='None':
                    output_dir=zip_form.cleaned_data['image_dir_choice']
                else:
                    output_dir = slugify(s.name)
            else:
                output_dir=zip_form.cleaned_data['image_dir']

            unpack_log=[]
            # make output_dir if necessary
            output_dir=os.path.join(os.path.dirname(settings.MEDIA_ROOT),output_dir)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
                unpack_log.append("Created output directory for images %s" % output_dir)

            if zip_form.cleaned_data['exp']==None:
                # create experiment object
                e = Experiment.objects.create(name=zip_form.cleaned_data['exp_name'],
                                              study=s,
                                              recycle=zip_form.cleaned_data['exp_recycle'],
                                              unique_id=zip_form.cleaned_data['exp_unique_id'],
                                              user=request.user.username,
                                              numTokens=0,
                                              totalTokens=0)
                e.create_token()
                e.save()
                unpack_log.append("Created Experiment %s" % e.name)
            else:
                e=zip_form.cleaned_data['exp']
                unpack_log.append("Adding to Experiment %s" % e.name)

            session_list=''
            for f in file_list:
                fn = os.path.basename(f.filename)
                if not fn or fn[0] == '_' or fn[0] == '.':
                    continue # skips directories and files that start with characters to ignore

                if is_image_file(f.filename):
                    if not os.path.exists(os.path.join(output_dir, fn)):
                        zf.extract(f, output_dir)
                        unpack_log.append("Extracting image file %s to %s" % (f.filename, output_dir))
                else:
                    # add session object
                    fp = zf.open(f.filename)
                    raw_cfg = fp.read()
                    cfg = raw_cfg.encode('utf-8','ignore')  # to avoid getting db breaking characters stored by accident
                    fp.close()
                    c = Session.objects.create_session(name=fn, #f.filename,
                                                       exp=e,
                                                       configFile=cfg,
                                                       user=request.user.username)
                    if session_list=='':
                        session_list=c.sessionToken
                    else:
                        session_list+=' '+c.sessionToken
                    unpack_log.append("Added config file %s as %s" % (f.filename, c.name))
            e.add_sessions(session_list, zip_form.cleaned_data['exp_restrict'])
            e.save()
            unpack_log.append("Added session list [%s] to experiment" % session_list)
            return render(request,'upload_report.html', {'log': unpack_log, 'exp':e})
        else:
            return HttpResponse("Invalid form")
    try:
        s=Study.objects.get(pk=int(studyNumber))
    except:
        return HttpResponse("Bad Study Number")

    e=None
    if expNumber!='':
        try:
            e=Experiment.objects.get(pk=int(expNumber))
        except:
            e=None

    # populate the image_dir_choice for selection of directory to place images

    if e==None:
        upload_form=ZipUploadForm(initial={'study': s})
        upload_form.fields['exp'].queryset = Experiment.objects.filter(study=s)
    else:
        upload_form=ZipUploadForm(initial={'study': s, 'exp': e})

    # for (optional) image uploading
    dirs = glob.glob(os.path.join(os.path.dirname(settings.MEDIA_ROOT), "*"))
    dir_choices=[('None', '------------')]
    for i,fn in enumerate(dirs):
        if os.path.isdir(fn) and os.path.basename(fn)!='zip_tmp':
            dir_choices.append((os.path.basename(fn),os.path.basename(fn)))
    upload_form.fields['image_dir_choice'].widget = forms.Select(choices=dir_choices)


    return render(request, 'sessions_upload.html', {'form': upload_form, 'study': s })


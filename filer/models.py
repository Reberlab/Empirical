from django.db import models
from django.forms import ModelForm
from django import forms
from django.conf import settings

from exp.models import Study, Experiment

# Images and/or cfg files are uploaded as .zip files
# These will be put in the MEDIA_ROOT/zip_tmp folder, then unzipped and added to the db
# Unzipping will create a folder with the name of the zip file, all path information stripped from the archive
# and named as zip/basename on extraction
# Image files will be directly addressable by the pathname (via staticfiles)

# Filer model is for handling upload of stimulus-files and js app files
class Filer(models.Model):
    upload_date=models.DateTimeField(auto_now_add=True)
    upload_user=models.CharField(max_length=100)
    filename=models.CharField(max_length=255)
    contents=models.BinaryField(blank=True)

class FileUploadForm(ModelForm):
    class Meta:
        model=Filer
        fields=['filename']

class EncryptKey(models.Model):
    creationDate=models.DateTimeField(auto_now_add=True)
    key=models.CharField(max_length=2048)

    # method for converting a passphrase into an encryption key here?


# Zip files can hold cfgs, stimulus-files or a mix of file types
class ZipUpload(models.Model):
    zip=models.FileField(upload_to=settings.ZIP_TMP)
    #group=models.CharField(max_length=100)
    upload_date=models.DateTimeField(auto_now_add=True)
    upload_user=models.CharField(max_length=100)
    study=models.ForeignKey('exp.Study',blank=True,null=True)
    exp=models.ForeignKey('exp.Experiment',blank=True,null=True)
    exp_restrict=models.BooleanField(default=False)
    exp_name=models.CharField(max_length=100,blank=True)
    exp_recycle=models.BooleanField(default=True)
    exp_unique_id=models.BooleanField(default=True)
    image_dir=models.CharField(max_length=100,blank=True)
    image_dir_choice=models.CharField(max_length=100,blank=True)

    def __unicode__(self):
        return self.zip.name


class ZipUploadForm(ModelForm):
    class Meta:
        model=ZipUpload
        fields=['zip', 'study', 'exp', 'exp_restrict', 'exp_name', 'exp_recycle', 'exp_unique_id',
                'image_dir', 'image_dir_choice']
        labels= {'zip': 'Zip file to upload',
                 'exp': 'Experiment to add to',
                 'exp_restrict': 'Restrict experiment to just new cfgs',
                 'exp_name': 'New Experiment name',
                 'exp_recycle': 'Recycle (new)',
                 'exp_unique_id': 'Require unique id (new)',
                 'image_dir_choice': 'Choose directory for images',
                 'image_dir': 'Enter image directory name'}
        widgets = {'study': forms.HiddenInput()}

class ImageUploadForm(ModelForm):
    class Meta:
        model=ZipUpload
        fields=['zip', 'image_dir_choice', 'image_dir']
        labels= {'zip': 'Zip file to upload',
                 'image_dir_choice': 'Choose directory for images',
                 'image_dir': 'Enter image directory name'}


class ExpImage(models.Model):
    filename=models.CharField(max_length=100)
    group=models.CharField(max_length=100)
    upload_date=models.DateTimeField(auto_now_add=True)
    upload_user=models.CharField(max_length=100)

    def __unicode__(self):
        return self.filename






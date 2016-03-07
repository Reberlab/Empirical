from django.db import models
from django import forms
from django.forms import ModelForm
from django.conf import settings

# Create your models here.
class ZipUpload(models.Model):
    zip=models.FileField(upload_to=settings.ZIP_TMP)
    group=models.CharField(max_length=100)
    upload_date=models.DateTimeField(auto_now_add=True)
    upload_user=models.CharField(max_length=100)

    def __unicode__(self):
        return self.zip.name


class ZipUploadForm(ModelForm):
    class Meta:
        model=ZipUpload
        fields=['zip']


class ExpImage(models.Model):
    filename=models.CharField(max_length=100)
    group=models.CharField(max_length=100)
    upload_date=models.DateTimeField(auto_now_add=True)
    upload_user=models.CharField(max_length=100)

    def __unicode__(self):
        return self.filename

class UploadEvent(models.Model):
    sourceFile=models.ForeignKey('ZipUpload')  # pointer to ZipUpload value
    expName=models.CharField(max_length=100)
    repetitions=models.IntegerField() # for repeating configfiles

class UploadEventForm(ModelForm):
    class Meta:
        model=UploadEvent
        fields=['sourceFile', 'expName','repetitions']
        widgets = {'sourceFile': forms.HiddenInput()}


# Images and/or cfg files are uploaded as .zip files
# These will be put in the MEDIA_ROOT/zip_tmp folder, then unzipped and added to the db
# Unzipping will create a folder with the name of the zip file, all path information stripped from the archive
# and named as zip/basename on extraction
# Image files will be directly addressable by the pathname (via staticfiles)

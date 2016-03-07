from django.db import models
from django.forms import ModelForm

# Create your models here.
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

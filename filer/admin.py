from django.contrib import admin

# Register your models here.

from .models import ZipUpload, ExpImage, Filer

admin.site.register(ZipUpload)
admin.site.register(ExpImage)
admin.site.register(Filer)
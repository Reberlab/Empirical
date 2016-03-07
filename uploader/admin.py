from django.contrib import admin

# Register your models here.
from .models import ZipUpload, ExpImage

admin.site.register(ZipUpload)
admin.site.register(ExpImage)


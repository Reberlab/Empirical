from django.contrib import admin

# Register your models here.

from .models import Session, Study, Experiment, Security, Download

admin.site.register(Session)
admin.site.register(Study)
admin.site.register(Experiment)
admin.site.register(Security)
admin.site.register(Download)

# Removed from administration to avoid the ability to edit data via the admin site
# admin.site.register(Report)

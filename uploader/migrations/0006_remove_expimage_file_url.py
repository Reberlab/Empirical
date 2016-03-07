# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0005_auto_20150727_1142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expimage',
            name='file_url',
        ),
    ]

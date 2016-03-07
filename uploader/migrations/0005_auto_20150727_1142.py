# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0004_auto_20150727_1024'),
    ]

    operations = [
        migrations.RenameField(
            model_name='zipupload',
            old_name='filename',
            new_name='zip',
        ),
    ]

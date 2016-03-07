# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0006_remove_expimage_file_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='expimage',
            name='upload_user',
            field=models.CharField(default='admin', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='zipupload',
            name='upload_user',
            field=models.CharField(default='admin', max_length=100),
            preserve_default=False,
        ),
    ]

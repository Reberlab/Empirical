# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expimage',
            name='img_filename',
        ),
        migrations.AddField(
            model_name='expimage',
            name='location',
            field=models.FilePathField(default='/tmp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expimage',
            name='name',
            field=models.CharField(default='none', max_length=100),
            preserve_default=False,
        ),
    ]

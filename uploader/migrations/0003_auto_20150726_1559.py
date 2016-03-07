# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0002_auto_20150726_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expimage',
            name='location',
        ),
        migrations.RemoveField(
            model_name='expimage',
            name='name',
        ),
        migrations.AddField(
            model_name='expimage',
            name='file_url',
            field=models.CharField(default='none', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expimage',
            name='filename',
            field=models.CharField(default='none', max_length=100),
            preserve_default=False,
        ),
    ]

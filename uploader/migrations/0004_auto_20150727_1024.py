# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0003_auto_20150726_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='expimage',
            name='group',
            field=models.CharField(default='none', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='zipupload',
            name='group',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]

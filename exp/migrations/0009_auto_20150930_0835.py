# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0008_tokengeneration_studyname'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokengeneration',
            name='groupSessions',
            field=models.TextField(default=' '),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tokengeneration',
            name='groupToken',
            field=models.CharField(default='none', max_length=100),
            preserve_default=False,
        ),
    ]

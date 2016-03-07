# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0004_tokengeneration_numtokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokengeneration',
            name='mturk_amount',
            field=models.CharField(default=5.0, max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='tokengeneration',
            name='mturk_description',
            field=models.CharField(max_length=1000, blank=True),
        ),
        migrations.AddField(
            model_name='tokengeneration',
            name='mturk_frame_size',
            field=models.CharField(default=800, max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='tokengeneration',
            name='mturk_title',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]

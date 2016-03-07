# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0009_auto_20150930_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='participants',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0007_auto_20150902_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokengeneration',
            name='studyName',
            field=models.ForeignKey(blank=True, to='exp.Study', null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0005_auto_20150821_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokengeneration',
            name='mturk_amount',
            field=models.DecimalField(default=5.0, max_digits=4, decimal_places=2, blank=True),
        ),
    ]

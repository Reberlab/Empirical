# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0003_tokengeneration'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokengeneration',
            name='numTokens',
            field=models.IntegerField(default=10, validators=[django.core.validators.MaxValueValidator(200), django.core.validators.MinValueValidator(1)]),
        ),
    ]

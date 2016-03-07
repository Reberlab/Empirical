# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0002_report_eventtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenGeneration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=100)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('expName', models.CharField(max_length=100)),
                ('appletName', models.CharField(max_length=100)),
            ],
        ),
    ]

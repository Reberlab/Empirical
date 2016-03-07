# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0010_study_participants'),
    ]

    operations = [
        migrations.CreateModel(
            name='Security',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sessionToken', models.CharField(max_length=100)),
                ('count', models.IntegerField(default=0)),
                ('locked', models.BooleanField(default=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('securityLog', models.TextField()),
            ],
        ),
    ]

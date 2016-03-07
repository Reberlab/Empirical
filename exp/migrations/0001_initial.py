# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sessionToken', models.CharField(max_length=100)),
                ('uploadDate', models.DateTimeField(auto_now_add=True)),
                ('dataLog', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sessionToken', models.CharField(max_length=100)),
                ('receiptToken', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('expName', models.CharField(max_length=100)),
                ('configFile', models.TextField()),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='report',
            name='sessionKey',
            field=models.ForeignKey(to='exp.Session'),
        ),
    ]

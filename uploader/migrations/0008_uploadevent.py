# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0007_auto_20150813_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expName', models.CharField(max_length=100)),
                ('repetitions', models.IntegerField()),
                ('sourceFile', models.ForeignKey(to='uploader.ZipUpload')),
            ],
        ),
    ]

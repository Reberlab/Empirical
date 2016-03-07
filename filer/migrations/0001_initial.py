# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EncryptKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('key', models.CharField(max_length=2048)),
            ],
        ),
        migrations.CreateModel(
            name='Filer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('upload_user', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=255)),
                ('contents', models.BinaryField(blank=True)),
            ],
        ),
    ]

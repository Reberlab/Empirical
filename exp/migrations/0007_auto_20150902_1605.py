# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0006_auto_20150824_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=100)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('consentJSON', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='session',
            name='receiptToken',
        ),
    ]

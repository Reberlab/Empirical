# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0011_security'),
    ]

    operations = [
        migrations.RenameField(
            model_name='security',
            old_name='count',
            new_name='hit_count',
        ),
    ]

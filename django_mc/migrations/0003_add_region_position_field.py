# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_mc', '0002_add_layoutregioncomponent_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='region',
            options={'ordering': ('position',), 'verbose_name': 'Region', 'verbose_name_plural': 'Regions'},
        ),
        migrations.AddField(
            model_name='region',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.MC_COMPONENT_BASE_MODEL),
        ('django_mc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayoutRegionComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=0)),
                ('component', models.ForeignKey(related_name='+', to=settings.MC_COMPONENT_BASE_MODEL)),
                ('provider', models.ForeignKey(related_name='region_components', to=settings.MC_LAYOUT_MODEL)),
                ('region', models.ForeignKey(related_name='+', to='django_mc.Region')),
            ],
            options={
                'db_table': 'django_mc_layout_regioncomponent',
                'db_tablespace': '',
            },
        ),
    ]

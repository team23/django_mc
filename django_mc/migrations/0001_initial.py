# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_mc.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.MC_LAYOUT_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_poly_ct', models.ForeignKey(related_name='+', editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Component Base',
                'swappable': 'MC_COMPONENT_BASE_MODEL',
                'verbose_name_plural': 'Component Bases',
            },
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('parent', models.ForeignKey(blank=True, to='self', help_text='Select a layout which shall be extended by this layout according to region extend rules.', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Layout',
                'swappable': 'MC_LAYOUT_MODEL',
                'verbose_name_plural': 'Layouts',
            },
            bases=(django_mc.mixins.TemplateHintProvider, models.Model),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('component_extend_rule', models.CharField(help_text='Define how page components that is added to this region change the layout components.', max_length=16, choices=[(b'combine', 'Add to existing layout components'), (b'overwrite', 'Replace existing layout components')])),
                ('available_components', models.ManyToManyField(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
            },
            bases=(django_mc.mixins.TemplateHintProvider, models.Model),
        ),
    ]

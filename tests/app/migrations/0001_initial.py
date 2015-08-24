# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtailnews.models
import taggit.managers
import modelcluster.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsIndex',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, parent_link=True, serialize=False, auto_created=True, to='wagtailcore.Page')),
            ],
            bases=(wagtailnews.models.NewsIndexMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='NewsIndexTag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('content_object', modelcluster.fields.ParentalKey(related_name='tagged_items', to='app.NewsIndex')),
                ('tag', models.ForeignKey(related_name='app_newsindextag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Published date')),
                ('title', models.CharField(max_length=32)),
                ('newsindex', models.ForeignKey(to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='NewsItemTag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('content_object', modelcluster.fields.ParentalKey(related_name='tagged_items', to='app.NewsItem')),
                ('tag', models.ForeignKey(related_name='app_newsitemtag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='newsitem',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', blank=True, to='taggit.Tag', through='app.NewsItemTag', verbose_name='Tags'),
        ),
    ]

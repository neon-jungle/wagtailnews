# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import wagtailnews.models
import modelcluster.fields
from django.conf import settings
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsIndex',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, to='wagtailcore.Page', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=(wagtailnews.models.NewsIndexMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='NewsIndexTag',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('content_object', modelcluster.fields.ParentalKey(to='app.NewsIndex', related_name='tagged_items')),
                ('tag', models.ForeignKey(to='taggit.Tag', related_name='app_newsindextag_items')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date', models.DateTimeField(verbose_name='Published date', default=django.utils.timezone.now)),
                ('live', models.BooleanField(editable=False, verbose_name='Live', default=True)),
                ('has_unpublished_changes', models.BooleanField(editable=False, verbose_name='Has unpublished changes', default=False)),
                ('title', models.CharField(max_length=32)),
                ('newsindex', models.ForeignKey(to='wagtailcore.Page')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='NewsItemRevision',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(verbose_name='Created at')),
                ('content_json', models.TextField(verbose_name='Content JSON')),
                ('newsitem', models.ForeignKey(to='app.NewsItem', related_name='revisions')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'news item revision',
            },
        ),
        migrations.CreateModel(
            name='NewsItemTag',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('content_object', modelcluster.fields.ParentalKey(to='app.NewsItem', related_name='tagged_items')),
                ('tag', models.ForeignKey(to='taggit.Tag', related_name='app_newsitemtag_items')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='newsitem',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(to='taggit.Tag', verbose_name='Tags', help_text='A comma-separated list of tags.', through='app.NewsItemTag', blank=True),
        ),
    ]

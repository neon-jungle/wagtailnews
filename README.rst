===========
wagtailnews
===========

A plugin for Wagtail that provides news / blogging functionality.

Installing
==========

Install using pip::

    pip install wagtailnews

It works with Wagtail 0.7 and upwards.

Using
=====

.. topic:: Models

    Create news models for your application that inherit from the relevant ``wagtailnews`` models:

    .. code:: python

        from django.db import models

        from wagtail.wagtailadmin.edit_handlers import FieldPanel
        from wagtail.wagtailcore.fields import RichTextField
        from wagtail.wagtailcore.models import Page

        from wagtailnews.models import NewsIndexMixin, AbstractNewsItem, AbstractNewsItemRevision
        from wagtailnews.decorators import newsindex


        # The decorator registers this model as a news index
        @newsindex
        class NewsIndex(NewsIndexMixin, Page):
            # Add extra fields here, as in a normal Wagtail Page class, if required
            newsitem_model = 'NewsItem'


        class NewsItem(AbstractNewsItem):
            # NewsItem is a normal Django model, *not* a Wagtail Page.
            # Add any fields required for your page.
            # It already has ``date`` field, and a link to its parent ``NewsIndex`` Page
            title = models.CharField(max_length=255)
            body = RichTextField()

            panels = [
                FieldPanel('title', classname='full title'),
                FieldPanel('body', classname='full'),
            ] + AbstractNewsItem.panels

            def __unicode__(self):
                return self.title


        class NewsItemRevision(AbstractNewsItemRevision):
            newsitem = models.ForeignKey(NewsItem, related_name='revisions')

.. topic:: Templates

    NewsIndex

    .. code:: django

        <h1>{{ page.title }}</h1>
        {% for item in newsitem_list %}
        <a href={{ item.url }}>{{ item }}</a>
        {% endfor %}

    NewsItem

    .. code:: django

        <h1>{{ newsitem.title }}</h1>
        {{ newsitem.body|richtext }}
        <a href={% pageurl page %}>Go back</a>

    In the NewsItem context 'page' is a reference to the NewsIndex.

.. topic:: Settings

    To change the paginator used by wagtailnews override the ``WAGTAILNEWS_PAGINATOR`` setting

===========
wagtailnews
===========

A plugin for Wagtail that provides news / blogging functionality.

Installing
==========

Install using pip::

    pip install wagtailnews

It works with Wagtail 5.2 and upwards. For older versions of Wagtail see past releases.


Quick start
===========

Create news models for your application that inherit from the relevant ``wagtailnews`` models:

.. code:: python

    from django.db import models

    from wagtail.admin.panels import FieldPanel
    from wagtail.fields import RichTextField
    from wagtail.models import Page

    from wagtailnews.models import NewsIndexMixin, AbstractNewsItem, AbstractNewsItemRevision
    from wagtailnews.decorators import newsindex


    # The decorator registers this model as a news index
    @newsindex
    class NewsIndex(NewsIndexMixin, Page):
        # Add extra fields here, as in a normal Wagtail Page class, if required
        newsitem_model = 'NewsItem'

        featured_news_item = models.ForeignKey(
            'NewsItem',
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='+',
        )

        content_panels = Page.content_panels + [
            FieldPanel('featured_news_item'), # This will set up a chooser for selecting a news item
        ]


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

        def __str__(self):
            return self.title


    class NewsItemRevision(AbstractNewsItemRevision):
        newsitem = models.ForeignKey(NewsItem, related_name='revisions', on_delete=models.CASCADE)


Old docs
========

`The docs for Wagtail news <http://wagtail-news.readthedocs.org>`_ are severely out of date, but may still be useful for reference.

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

Create news models for your application that inherit from the relevant ``wagtailnews`` models:

.. code:: python

    from django.db import models

    from wagtail.wagtailadmin.edit_handlers import FieldPanel
    from wagtail.wagtailcore.fields import RichTextField
    from wagtail.wagtailcore.models import Page

    from wagtailnews.models import NewsIndexMixin, AbstractNewsItem
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

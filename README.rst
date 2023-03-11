===========
wagtailnews
===========

A plugin for Wagtail that provides a simple news functionality.

Installing
==========

Install using pip::

    pip install wagtailnews

``wagtailnews`` 2.x is compatible with Wagtail 2.15 or 2.16,
Django 3.0 and higher,
and Python 3.6 and higher.

For older version of Wagtail or Django, see past releases

For wagtail 3 and 4 check wagtailnews 3 and higher.

Documentation
=============

`Documentation for Wagtail news <http://wagtail-news.readthedocs.org>`_ can be found on Read The Docs

Quick start
===========

Install ``wagtailnews`` using pip::

   pip install wagtailnews

Step 2
______

Add ``wagtailnews`` to your ``INSTALLED_APPS`` in settings:

.. code-block:: python

  INSTALLED_APPS += [
      'wagtailnews',
  ]

Create news models for your application that inherit from the relevant ``wagtailnews`` models:

.. code:: python

    from django.db import models

    from wagtail.admin.edit_handlers import FieldPanel
    from wagtail.core.fields import RichTextField
    from wagtail.core.models import Page

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

        def __str__(self):
            return self.title


    class NewsItemRevision(AbstractNewsItemRevision):
        newsitem = models.ForeignKey(NewsItem, related_name='revisions', on_delete=models.CASCADE)

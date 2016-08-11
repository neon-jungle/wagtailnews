.. _rss:

========
RSS Feed
========

``wagtailnews`` supports RSS feeds!

Custom RSS feed fields
______________________

``wagtailnews`` support of RSS feeds comes from Django's syndication feed framework. Wagtail News provides a basic implementation, but you will need to customise it to suit your news models. For example, to add a custom ``<description>`` for your news items:

.. code-block:: python

  from wagtailnews.feeds import LatestEntriesFeed

  class MyNewsFeed(LatestEntriesFeed):
      def item_description(self, item):
          return item.description

Your custom ``Feed`` class can then be added to your news index by setting the ``feed_class`` attribute:

.. code-block:: python

  @newsindex
  class NewsIndex(NewsIndexMixin, Page):
      feed_class = MyNewsFeed


Find out more about :class:`~django.contrib.syndication.views.Feed` classes in the Django docs: :doc:`django:ref/contrib/syndication`.


Linking to RSS feed
___________________

A link to the RSS feed can be created in a template like this:

.. code-block:: html+django

  {% load wagtailroutablepage_tags %}
  <a href="{% routablepageurl page "feed" %}">RSS</a>

The Wagtail docs have more information on the :func:`~wagtail.contrib.wagtailroutablepage.templatetags.wagtailroutablepage_tags.routablepageurl` template tag.

.. _installing:

========
RSS Feed
========

``wagtailnews`` supports RSS feeds!

Custom RSS feed fields
______________________

``wagtailnews`` support of RSS feeds comes from Django's syndication feed framework. This means custom RSS feed fields can be created using **Feed** classes.Below is an example of a feed with a custom description field.

Here is the creation of the **Feed** class:

.. code-block:: python

  from wagtailnews.feeds import LatestEnteriesFeed


  class LatestEnteriesDescriptionFeed(LatestEnteriesFeed):
      def item_description(self, item):
          return item.description()

The **Feed** class can then be added to the index:

.. code-block:: python

  @newsindex
  class NewsIndex(NewsIndexMixin, Page):
      feed_class = feeds.LatestEnteriesDescriptionFeed


Find out more about **Feed** classes in the django docs: https://docs.djangoproject.com/en/1.10/ref/contrib/syndication/


Linking to RSS feed
___________________

Creating a link to the RSS feed requires using wagtails' ``RoutablePageMixin`` and the feed route.
Make sure the ``RoutablePageMixin`` is added to the installed apps:

.. code-block:: python

  INSTALLED_APPS = [
    'yourproject',
    'wagtailnews',
    'wagtail.contrib.wagtailroutablepage',
  ]

Then in the template a link to the RSS feed can be created like this:

.. code-block:: python

  {% load wagtailroutablepage_tags %}

  <a href="{% routablepageurl page "feed" %}">RSS</a>

You can find out more about the ``RoutablePageMixin`` in the wagtail docs: http://docs.wagtail.io/en/latest/reference/contrib/routablepage.html

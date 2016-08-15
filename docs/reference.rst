.. _reference:

=========
Reference
=========

.. module:: wagtailnews.decorators

.. autofunction:: newsindex

    Register a :class:`~wagtailnews.models.NewsIndexMixin` page.
    News indexes need to be registered before news items can be managed through the admin.

    .. code-block:: python

        @newsindex
        class NewsIndex(NewsIndexMixin, Page):
            newsitem_model = NewsItem

.. module:: wagtailnews.models

News items
==========

.. class:: AbstractNewsItem

Fields
------

.. attribute:: AbstractNewsItem.date

    A :class:`~django.db.models.DateTimeField` that records the published date of this news item.
    It is automatically set when the news item is created.
    You can add it to the :attr:`AbstractNewsItem.panels` list if you want editors to be able to customise the date.
    If set in the future, the post will not appear on the front end.

.. attribute:: AbstractNewsItem.live

    A :class:`~django.db.models.BooleanField` that indicates if this news item is live.
    A live news item might have unpublished drafts.

Attributes
----------

.. attribute:: AbstractNewsItem.template

    The template to use for this news item.
    Defaults to ``app_label/model_name.html``.

Methods
-------

.. automethod:: AbstractNewsItem.get_nice_url

    Make a slug to put in the URL.
    News items are fetched using their ID, which is also embedded in the URL,
    this slug just makes the URLs nicer.
    The slug does not need to be unique.
    By default, it is generated from ``slugify(str(self))``.


.. automethod:: AbstractNewsItem.get_template

    Get the template for this news item.
    See also :attr:`AbstractNewsItem.template`.

.. automethod:: AbstractNewsItem.get_context

    Build a context dictionary for the template.
    The default implementation gets the context from the news index,
    and adds the news item as ``newsitem``.

.. automethod:: AbstractNewsItem.url_suffix

    Return the URL of this news item relative to the news index.

    .. code-block:: python

        >>> newsitem.url_suffix()
        '2016/08/11/1234-my-news-item/'

    See also :meth:`AbstractNewsItem.get_nice_url`.

.. automethod:: AbstractNewsItem.url

    Return the URL of this news item, using the news indexes :attr:`~wagtail.wagtailcore.models.Page.url` attribute.

.. automethod:: AbstractNewsItem.full_url

    Return the URL of this news item, using the news indexes :attr:`~wagtail.wagtailcore.models.Page.full_url` attribute.

News index
==========

.. class:: NewsIndexMixin

Attributes
----------

.. attribute:: NewsIndexMixin.newsitem_model

    The news item model to use for this news index.
    The news item model must be a subclass of :class:`AbstractNewsItem`.
    This can either be the name of the model as a string,
    such as 'NewsItem' or 'myapp.NewsItem',
    or the actual news item class.

.. attribute:: NewsIndexMixin.feed_class

    The :class:`~django.contrib.syndication.views.Feed` class to use to create the RSS feed.
    See :ref:`rss` for more details.

.. attribute:: NewsIndexMixin.subpage_types

    Defaults to an empty list.
    News indexes with subpages are not supported.

Methods
-------

.. automethod:: NewsIndexMixin.get_newsitem_model

    Get the news item model for this news index.
    See :attr:`NewsIndexMixin.newsitem_model`.

Routes
------

The functionality of news indexes come from Wagtail's :ref:`wagtail:routable_page_mixin`.
The following routes are defined:

``index``
    The root url which shows all news items.

    .. code-block:: python

        >>> newsindex.reverse_subpage('index')
        ''

``year``
    Displays all news items from a year.

    .. code-block:: python

        >>> newsindex.reverse_subpage('year', kwargs={'year': '2016'})
        '2016/'

``month``
    Displays all news items from a month.

    .. code-block:: python

        >>> newsindex.reverse_subpage('month', kwargs={'year': '2016', 'month': '08'})
        '2016/08/'

``day``
    Displays all news items from a day.

    .. code-block:: python

        >>> newsindex.reverse_subpage('day', kwargs={'year': '2016', 'month': '08', 'day': '15'})
        '2016/08/15/'

``post``
    Shows a single news item.

    .. code-block:: python

        >>> newsindex.reverse_subpage('post', kwargs={
        ...     'year': '2016', 'month': '08', 'day': '15',
        ...     'pk': newsitem.pk, 'slug': newsitem.get_nice_url()})
        '2016/08/15/1234-my-news-item/'

    See also :meth:`AbstractNewsItem.get_nice_url`
    and :meth:`AbstractNewsItem.url_suffix`.

``feed``
    Show the RSS feed.

    .. code-block:: python

        >>> newsindex.reverse_subpage('rss')
        'rss/'

    See also :ref:`rss`.


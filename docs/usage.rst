.. _usage:

=====
Usage
=====

To start using Wagtail News, you have to define a news index model, and a news item model.

The news item model stores each news post that you make.
The news item model is a regular Django model
that inherits from :class:`~wagtailnews.models.AbstractNewsItem`.
Add any fields that you want to this model:

.. code-block:: python

    from wagtailnews.models import AbstractNewsItem, AbstractNewsItemRevision
    from wagtail.core.fields import RichTextField

    class NewsItem(AbstractNewsItem):
        title = models.CharField(max_length=100)
        body = RichTextField()

        panels = [
            FieldPanel('title'),
            FieldPanel('body'),
        ]

        def __str__(self):
            return self.title

    # This table is used to store revisions of the news items.
    class NewsItemRevision(AbstractNewsItemRevision):
        # This is the only field you need to define on this model.
        # It must be a foreign key to your NewsItem model,
        # be named 'newsitem', and have a related_name='revisions'
        newsitem = models.ForeignKey(NewsItem, related_name='revisions', on_delete=models.CASCADE)

The panels can be customised using the ``panels`` attribute,
or a completely custom edit handler can be used by setting the ``edit_handler`` attribute.
See :ref:`the Wagtail docs <wagtail:customising_the_tabbed_interface>` for more information.

The news index model is a subclass of the Wagtail Page model.
This page defines where your news page appears on your site.
You can define any extra fields you need on this page.
This page needs to inherit from :class:`~wagtailnews.models.NewsItemMixin`,
and be registered using the :func:`wagtailnews.decorators.newsindex` decorator.
The ``newsitem_model`` attribute defines which news item model to use for this news index.

.. code-block:: python

    from wagtail.core.models import Page
    from wagtailnews.decorators import newsindex
    from wagtailnews.models import NewsIndexMixin

    @newsindex
    class NewsIndex(NewsIndexMixin, Page):
        newsitem_model = 'NewsItem'

Make and run migrations, and everything should be waiting for you in the Wagtail admin!
First, create a new ``NewsIndex`` page somewhere in your page tree.
Then, click the "News" link in the side bar.
From here, you can create and manage news items for this news index.

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel, ObjectList, PageChooserPanel, TabbedInterface)
from wagtail.core.models import Page
from wagtail.search import index

from wagtailnews.decorators import newsindex
from wagtailnews.edit_handlers import NewsChooserPanel
from wagtailnews.models import (
    AbstractNewsItem, AbstractNewsItemRevision, NewsIndexMixin)

from . import feeds


class NewsIndexTag(TaggedItemBase):
    content_object = ParentalKey('NewsIndex', related_name='tagged_items')


class NewsItemTag(TaggedItemBase):
    content_object = ParentalKey('NewsItem', related_name='tagged_items')


@newsindex
class NewsIndex(NewsIndexMixin, Page):
    feed_class = feeds.LatestEntriesTestFeed
    newsitem_model = 'NewsItem'
    featured_newsitem = models.ForeignKey(
        'NewsItem', blank=True, null=True, on_delete=models.SET_NULL,
        related_name='+')

    content_panels = Page.content_panels + [
        NewsChooserPanel('featured_newsitem'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(NewsIndex, self).get_context(request, *args, **kwargs)
        context.update({'extra': 'foo'})
        return context


@python_2_unicode_compatible
class NewsItem(AbstractNewsItem):
    title = models.CharField(max_length=32)
    page = models.ForeignKey(
        'wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+')

    tags = ClusterTaggableManager(through=NewsItemTag, blank=True)

    panels = [
        FieldPanel('title'),
        PageChooserPanel('page'),
        FieldPanel('tags'),
        FieldPanel('date'),
    ]

    search_fields = AbstractNewsItem.search_fields + [
        index.SearchField('title'),
    ]

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        context = super(NewsItem, self).get_context(request, *args, **kwargs)
        context['foo'] = 'bar'
        return context

    def get_description(self):
        return "This post was published on {0}, with a title of {1}".format(self.date, self.title)


class NewsItemRevision(AbstractNewsItemRevision):
    newsitem = models.ForeignKey(
        NewsItem, related_name='revisions', on_delete=models.CASCADE)


@newsindex
class SecondaryNewsIndex(NewsIndexMixin, Page):
    newsitem_model = 'SecondaryNewsItem'

    def get_admin_display_title(self):
        return 'Title for admin - ' + self.title

    template = 'app/secondaryindex.jade'


class SecondaryNewsItem(AbstractNewsItem):
    title = models.CharField(max_length=32)

    edit_handler = TabbedInterface([
        ObjectList([FieldPanel('title')], heading='Tab the first'),
        ObjectList([FieldPanel('date')], heading='Tab the second'),
    ])


class SecondaryNewsItemRevision(AbstractNewsItemRevision):
    newsitem = models.ForeignKey(
        SecondaryNewsItem, related_name='revisions', on_delete=models.CASCADE)

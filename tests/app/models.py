from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsnippets.models import register_snippet

from wagtailnews.decorators import newsindex
from wagtailnews.edit_handlers import NewsChooserPanel
from wagtailnews.models import (
    AbstractNewsItem, AbstractNewsItemRevision, NewsIndexMixin)


class NewsIndexTag(TaggedItemBase):
    content_object = ParentalKey('NewsIndex', related_name='tagged_items')


class NewsItemTag(TaggedItemBase):
    content_object = ParentalKey('NewsItem', related_name='tagged_items')


@newsindex
class NewsIndex(NewsIndexMixin, Page):
    newsitem_model = 'NewsItem'
    featured_newsitem = models.ForeignKey(
        'NewsItem', null=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
        NewsChooserPanel('featured_newsitem'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(NewsIndex, self).get_context(request, *args, **kwargs)
        context.update({'extra': 'foo'})
        return context


@register_snippet
@python_2_unicode_compatible
class NewsItem(AbstractNewsItem):
    title = models.CharField(max_length=32)
    page = models.ForeignKey('wagtailcore.Page', related_name='+', null=True,
                             blank=True)

    tags = ClusterTaggableManager(through=NewsItemTag, blank=True)

    panels = [
        FieldPanel('title'),
        PageChooserPanel('page'),
        FieldPanel('tags'),
        FieldPanel('date'),
    ]

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        context = super(NewsItem, self).get_context(request, *args, **kwargs)
        context['foo'] = 'bar'
        return context


class NewsItemRevision(AbstractNewsItemRevision):
    newsitem = models.ForeignKey(NewsItem, related_name='revisions')


@newsindex
class SecondaryNewsIndex(NewsIndexMixin, Page):
    newsitem_model = 'SecondaryNewsItem'


class SecondaryNewsItem(AbstractNewsItem):
    pass


class SecondaryNewsItemRevision(AbstractNewsItemRevision):
    newsitem = models.ForeignKey(SecondaryNewsItem, related_name='revisions')

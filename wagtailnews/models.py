from __future__ import absolute_import, unicode_literals

from six import text_type, string_types

from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.wagtailsearch import indexed


NEWSINDEX_MODEL_CLASSES = []
_NEWSINDEX_CONTENT_TYPES = []


def get_newsindex_content_types():
    global _NEWSINDEX_CONTENT_TYPES
    if len(_NEWSINDEX_CONTENT_TYPES) != len(NEWSINDEX_MODEL_CLASSES):
        _NEWSINDEX_CONTENT_TYPES = [
            ContentType.objects.get_for_model(cls)
            for cls in NEWSINDEX_MODEL_CLASSES]
    return _NEWSINDEX_CONTENT_TYPES


class NewsIndexMixin(RoutablePageMixin):

    class Meta:
        pass

    newsitem_model = None
    subpage_types = []

    subpage_urls = (
        url(r'^$', 'v_index', name='index'),
        url(r'^(?P<year>\d{4})/$', 'v_year', name='year'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'v_month', name='month'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'v_day', name='day'),
        url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)-(?P<slug>.*)/$', 'v_post', name='post'),
    )

    v_index = lambda s, r: frontend.news_index(r, s)
    v_year = lambda s, r, **k: frontend.news_year(r, s, **k)
    v_month = lambda s, r, **k: frontend.news_month(r, s, **k)
    v_day = lambda s, r, **k: frontend.news_day(r, s, **k)
    v_post = lambda s, r, **k: frontend.newsitem_detail(r, s, **k)

    def get_newsitem_model(cls):
        if isinstance(cls.newsitem_model, models.Model):
            return cls.newsitem_model
        elif isinstance(cls.newsitem_model, string_types):
            return resolve_model_string(cls.newsitem_model, cls._meta.app_label)
        else:
            raise ValueError('Can not resolve {0}.newsitem_model in to a model: {1!r}'.format(
                cls.__name__, cls.newsitem_model))


class AbstractNewsItem(models.Model):

    newsindex = models.ForeignKey(Page)
    date = models.DateTimeField('Published date', default=timezone.now)

    panels = [
        FieldPanel('date'),
    ]

    search_fields = (indexed.FilterField('date'),)

    class Meta:
        ordering = ('-date',)
        abstract = True

    def get_nice_url(self):
        return slugify(text_type(self))

    def get_template(self, request):
        try:
            return self.template
        except AttributeError:
            return '{0}/{1}.html'.format(self._meta.app_label, self._meta.model_name)

    def url(self):
        newsindex = self.newsindex.specific
        ldate = timezone.localtime(self.date)
        print 'newsindex.url:', newsindex.url
        try:
            url = newsindex.url + newsindex.reverse_subpage('post', kwargs={
                'year': ldate.year, 'month': ldate.month, 'day': ldate.day,
                'pk': self.pk, 'slug': self.get_nice_url()})
        except Exception as e:
            print e
            raise
        print 'url:', url
        return url


# Need to import this down here to prevent circular imports :(
from .views import frontend

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.six import text_type
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.utils import resolve_model_string
from wagtail.wagtailsearch import index

from . import feeds
from .utils.views import ModelViewProxy

frontend = ModelViewProxy('wagtailnews.views.frontend')

NEWSINDEX_MODEL_CLASSES = []


class NewsIndexMixin(RoutablePageMixin):

    class Meta:
        pass

    feed_class = feeds.LatestEntriesFeed
    newsitem_model = None
    subpage_types = []

    @route(r'^$', name='index')
    def v_index(s, r):
        return frontend.news_index(s, r)

    @route(r'^(?P<year>\d{4})/$', name='year')
    def v_year(s, r, **k):
        return frontend.news_year(s, r, **k)

    @route(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', name='month')
    def v_month(s, r, **k):
        return frontend.news_month(s, r, **k)

    @route(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', name='day')
    def v_day(s, r, **k):
        return frontend.news_day(s, r, **k)

    @route(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)-(?P<slug>.*)/$', name='post')
    def v_post(s, r, **k):
        return frontend.newsitem_detail(s, r, **k)

    @route(r'^rss/$', name='feed')
    def newsfeed(self, request):
        return self.feed_class(self)(request)

    @classmethod
    def get_newsitem_model(cls):
        return resolve_model_string(cls.newsitem_model, cls._meta.app_label)


class AbstractNewsItemRevision(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Created at'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True)
    content_json = models.TextField(verbose_name=_('Content JSON'))

    objects = models.Manager()

    def save(self, *args, **kwargs):
        # Set default value for created_at to now
        # We cannot use auto_now_add as that will override
        # any value that is set before saving
        if self.created_at is None:
            self.created_at = timezone.now()

        super(AbstractNewsItemRevision, self).save(*args, **kwargs)

    def as_newsitem(self):
        obj = type(self.newsitem).from_json(self.content_json)

        # Override the possibly-outdated tree parameter fields from this
        # revision object with up-to-date values
        obj.pk = self.newsitem.pk

        # also copy over other properties which are meaningful for the newsitem as a whole, not a
        # specific revision of it
        obj.live = self.newsitem.live
        obj.has_unpublished_changes = self.newsitem.has_unpublished_changes

        return obj

    def is_latest_revision(self):
        if self.id is None:
            # special case: a revision without an ID is presumed to be newly-created and is thus
            # newer than any revision that might exist in the database
            return True
        latest_revision = type(self).objects.filter(newsitem_id=self.newsitem_id).order_by('-created_at', '-id').first()
        return (latest_revision == self)

    def publish(self):
        newsitem = self.as_newsitem()
        newsitem.live = True
        # at this point, the newsitem has unpublished changes iff there are newer revisions than this one
        newsitem.has_unpublished_changes = not self.is_latest_revision()

        newsitem.save()

    def __str__(self):
        return '"{}" at {}'.format(self.newsitem, self.created_at)

    class Meta:
        verbose_name = _('news item revision')
        abstract = True


class NewsItemQuerySet(models.QuerySet):
    def live(self):
        return self.filter(live=True)


class AbstractNewsItem(index.Indexed, ClusterableModel):

    newsindex = models.ForeignKey(Page)
    date = models.DateTimeField('Published date', default=timezone.now)

    live = models.BooleanField(
        verbose_name=_('Live'), default=True, editable=False)
    has_unpublished_changes = models.BooleanField(
        verbose_name=_('Has unpublished changes'),
        default=False, editable=False)

    panels = [
        FieldPanel('date'),
    ]

    search_fields = [
        index.FilterField('date'),
        index.FilterField('newsindex_id'),
        index.FilterField('live'),
    ]

    class Meta:
        ordering = ('-date',)
        abstract = True

    objects = NewsItemQuerySet.as_manager()

    def get_nice_url(self):
        return slugify(text_type(self))

    def get_template(self, request):
        try:
            return self.template
        except AttributeError:
            return '{0}/{1}.html'.format(self._meta.app_label, self._meta.model_name)

    def get_context(self, request, *args, **kwargs):
        context = self.newsindex.specific.get_context(request, *args, **kwargs)
        context.update({
            'newsitem': self
        })
        return context

    def url_suffix(self):
        newsindex = self.newsindex.specific
        ldate = timezone.localtime(self.date)
        return newsindex.reverse_subpage('post', kwargs={
            'year': ldate.year, 'month': ldate.month, 'day': ldate.day,
            'pk': self.pk, 'slug': self.get_nice_url()})

    def url(self):
        return self.newsindex.specific.url + self.url_suffix()

    def full_url(self):
        return self.newsindex.specific.full_url + self.url_suffix()

    def save_revision(self, user=None, changed=True):
        # Create revision
        revision = self.revisions.create(content_json=self.to_json(), user=user)

        if changed:
            self.has_unpublished_changes = True
            self.save(update_fields=['has_unpublished_changes'])

        return revision

    def get_latest_revision(self):
        return self.revisions.order_by('-created_at', '-id').first()

    def get_latest_revision_as_newsitem(self):
        latest_revision = self.get_latest_revision()

        if latest_revision:
            return latest_revision.as_newsitem()
        else:
            return self

    def unpublish(self, commit=True):
        if self.live:
            self.live = False
            self.has_unpublished_changes = True

            if commit:
                self.save(update_fields=['live', 'has_unpublished_changes'])

    @property
    def status_string(self):
        if not self.live:
            return _("draft")
        else:
            if self.has_unpublished_changes:
                return _("live + draft")
            else:
                return _("live")

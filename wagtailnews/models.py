import datetime
import os
import warnings
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page
from wagtail.core.utils import resolve_model_string
from wagtail.search import index

from . import feeds
from .conf import paginate
from .deprecation import DeprecatedCallableStr

NEWSINDEX_MODEL_CLASSES = []


def get_date_or_404(year, month, day):
    """Try to make a date from the given inputs, raising Http404 on error"""
    try:
        return datetime.date(int(year), int(month), int(day))
    except ValueError:
        raise Http404


class NewsIndexMixin(RoutablePageMixin):

    class Meta:
        pass

    feed_class = feeds.LatestEntriesFeed
    newsitem_model = None
    subpage_types = []

    def get_newsitems(self):
        """Get all the news items for this news index"""
        return self.get_newsitem_model().objects.filter(newsindex=self)

    def get_newsitems_for_display(self):
        """
        Get the news items that should be shown on for this news index, before
        filtering and pagination.
        """
        return self.get_newsitems().live().filter(date__lte=timezone.now())

    def get_template(self, request, view='all', **kwargs):
        template = super(NewsIndexMixin, self).get_template(
            request, view=view, **kwargs)

        base, ext = os.path.splitext(template)

        # Will make something like:
        # ["news/news_index_month.html", "news/news_index.html"]
        return ['{}_{}{}'.format(base, view, ext), template]

    def get_context(self, request, view, **kwargs):
        context = super(NewsIndexMixin, self).get_context(request, **kwargs)
        context.update({'newsitem_view': view})
        return context

    def paginate_newsitems(self, request, newsitem_list):
        paginator, page = paginate(request, newsitem_list)
        return {
            'paginator': paginator,
            'newsitem_page': page,
            'newsitem_list': page.object_list,
        }

    def respond(self, request, view, newsitems, extra_context={}):
        """A helper that takes some news items and returns an HttpResponse"""
        context = self.get_context(request, view=view)
        context.update(self.paginate_newsitems(request, newsitems))
        context.update(extra_context)
        template = self.get_template(request, view=view)
        return TemplateResponse(request, template, context)

    @route(r'^$', name='index')
    def v_index(self, request):
        return self.respond(request, 'all', self.get_newsitems_for_display())

    @route(r'^(?P<year>\d{4})/$', name='year')
    def v_year(self, request, year):
        date = get_date_or_404(year, 1, 1)
        newsitems = self.get_newsitems_for_display().filter(date__year=year)
        return self.respond(request, 'year', newsitems, {'date': date})

    @route(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', name='month')
    def v_month(self, request, year, month):
        date = get_date_or_404(year, month, 1)
        newsitems = self.get_newsitems_for_display().filter(
            date__year=year, date__month=month)
        return self.respond(request, 'month', newsitems, {'date': date})

    @route(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', name='day')
    def v_day(self, request, year, month, day):
        date = get_date_or_404(year, month, day)
        newsitems = self.get_newsitems_for_display().filter(
            date__year=year, date__month=month, date__day=day)
        return self.respond(request, 'day', newsitems, {'date': date})

    @route(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)-(?P<slug>.*)/$', name='post')
    def v_post(self, request, year, month, day, pk, slug):
        newsitem = get_object_or_404(self.get_newsitems_for_display(), pk=pk)

        # Check the URL date and slug are still correct
        newsitem_url = newsitem.url
        newsitem_path = urlparse(newsitem_url, allow_fragments=True).path
        if urlquote(request.path) != newsitem_path:
            return HttpResponsePermanentRedirect(newsitem_url)

        # Get the newsitem to serve itself
        return newsitem.serve(request)

    @route(r'^rss/$', name='feed')
    def newsfeed(self, request):
        return self.feed_class(self)(request)

    @classmethod
    def get_newsitem_model(cls):
        return resolve_model_string(cls.newsitem_model, cls._meta.app_label)


class AbstractNewsItemRevision(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Created at'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'),
        null=True, blank=True, on_delete=models.SET_NULL)
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

    newsindex = models.ForeignKey(Page, on_delete=models.CASCADE)
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
        warnings.warn(
            'AbstractNewsItem.get_nice_url() has been renamed to AbstractNewsItem.get_slug()',
            DeprecationWarning,
            stacklevel=2)
        return self.get_slug()

    def get_slug(self):
        allow_unicode = getattr(settings, 'WAGTAIL_ALLOW_UNICODE_SLUGS', True)
        return slugify(str(self), allow_unicode=allow_unicode)

    def get_template(self, request):
        try:
            return self.template
        except AttributeError:
            return '{0}/{1}.html'.format(self._meta.app_label, self._meta.model_name)

    def get_context(self, request, *args, **kwargs):
        context = self.newsindex.specific.get_context(request, view='newsitem', *args, **kwargs)
        context['newsitem'] = self
        return context

    def serve(self, request):
        template = self.get_template(request)
        context = self.get_context(request)
        return TemplateResponse(request, template, context)

    def url_suffix(self):
        newsindex = self.newsindex.specific
        ldate = timezone.localtime(self.date)
        return newsindex.reverse_subpage('post', kwargs={
            'year': ldate.year, 'month': ldate.month, 'day': ldate.day,
            'pk': self.pk, 'slug': self.get_slug()})

    @property
    def url(self):
        return DeprecatedCallableStr(
            self.newsindex.specific.url + self.url_suffix(),
            warning="NewsItem.url is now a property, not a method.",
            warning_cls=DeprecationWarning)

    @property
    def full_url(self):
        return DeprecatedCallableStr(
            self.newsindex.specific.full_url + self.url_suffix(),
            warning="NewsItem.full_url is now a property, not a method.",
            warning_cls=DeprecationWarning)

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

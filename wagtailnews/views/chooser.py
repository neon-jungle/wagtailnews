import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.backends import get_search_backend

from ..models import NEWSINDEX_MODEL_CLASSES, NewsIndexMixin
from ..permissions import (
    perms_for_template, user_can_edit_news, user_can_edit_newsitem)

LOGGER = logging.getLogger(__name__)


def choose(request):
    user = request.user
    if not user_can_edit_news(user):
        raise PermissionDenied

    allowed_news_types = [
        NewsIndex for NewsIndex in NEWSINDEX_MODEL_CLASSES
        if user_can_edit_newsitem(user, NewsIndex.get_newsitem_model())]

    allowed_cts = ContentType.objects.get_for_models(*allowed_news_types)\
        .values()
    newsindex_list = Page.objects.filter(content_type__in=allowed_cts)
    newsindex_count = newsindex_list.count()

    try:
        query = request.GET['q']
        backend = get_search_backend()

        LOGGER.debug("Searching for '%s'", query)


        # FIXME: this is crap, need to construct a single query for all types
        # to search by relevance however that's not currently possible in
        # a backend agnostic way :(
        newsitem_list = []
        for news_type in allowed_news_types:
            newsitem_list += \
                list(backend.search(query, news_type.get_newsitem_model()))

        return render(request, 'wagtailnews/index.html', {
            'newsitem_list': newsitem_list,
        })

    except KeyError:
        pass

    if newsindex_count == 1:
        newsindex = newsindex_list.first()
        return redirect('wagtailnews_index', pk=newsindex.pk)

    return render(request, 'wagtailnews/choose.html', {
        'has_news': newsindex_count != 0,
        'newsindex_list': ((newsindex, newsindex.content_type.model_class()._meta.verbose_name)
                           for newsindex in newsindex_list)
    })


def index(request, pk):
    newsindex = get_object_or_404(
        Page.objects.specific().type(NewsIndexMixin), pk=pk)
    NewsItem = newsindex.get_newsitem_model()

    if not user_can_edit_newsitem(request.user, NewsItem):
        raise PermissionDenied()

    newsitem_list = NewsItem.objects.filter(newsindex=newsindex)

    try:
        query = request.GET['q']
        backend = get_search_backend()

        LOGGER.debug("Searching for '%s'", query)

        newsitem_list = backend.search(query, newsitem_list)

    except KeyError:
        pass

    return render(request, 'wagtailnews/index.html', {
        'newsindex': newsindex,
        'newsitem_list': newsitem_list,
        'newsitem_perms': perms_for_template(request, NewsItem),
    })

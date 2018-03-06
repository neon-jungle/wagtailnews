import json
import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from wagtail.admin.forms import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.utils.pagination import paginate

from ..models import NEWSINDEX_MODEL_CLASSES, AbstractNewsItem, NewsIndexMixin
from ..permissions import (
    perms_for_template, user_can_edit_news, user_can_edit_newsitem)

LOGGER = logging.getLogger(__name__)


def get_allowed_news_types(user):
    """Get a list of all NewsIndex models that the user can edit"""
    return [
        NewsIndex for NewsIndex in NEWSINDEX_MODEL_CLASSES
        if user_can_edit_newsitem(user, NewsIndex.get_newsitem_model())]


def choose(request):
    if not user_can_edit_news(request.user):
        raise PermissionDenied

    allowed_news_types = get_allowed_news_types(request.user)

    allowed_cts = ContentType.objects.get_for_models(*allowed_news_types)\
        .values()
    newsindex_list = Page.objects.filter(content_type__in=allowed_cts).specific()
    newsindex_count = newsindex_list.count()

    if newsindex_count == 1:
        newsindex = newsindex_list.first()
        return redirect('wagtailnews:index', pk=newsindex.pk)

    return render(request, 'wagtailnews/choose.html', {
        'has_news': newsindex_count != 0,
        'newsindex_list': ((newsindex, newsindex.content_type.model_class()._meta.verbose_name)
                           for newsindex in newsindex_list)
    })


def _search_newsitems(request, newsitem_models, query):
    backend = get_search_backend()

    for NewsItem in newsitem_models:
        results = backend.search(query, NewsItem)[:10]
        if results:
            yield (
                NewsItem._meta.verbose_name_plural,
                perms_for_template(request, NewsItem),
                results)


def search(request):
    if not user_can_edit_news(request.user):
        raise PermissionDenied

    allowed_news_types = get_allowed_news_types(request.user)

    query = request.GET.get('q', '')

    # FIXME: this is crap, need to construct a single query for all types
    # to search by relevance however that's not currently possible in
    # a backend agnostic way :(
    newsitem_models = [NewsIndex.get_newsitem_model()
                       for NewsIndex in allowed_news_types]
    newsitem_results = list(_search_newsitems(request, newsitem_models, query))

    return render(request, 'wagtailnews/search.html', {
        'single_result_type': len(newsitem_results) == 1,
        'single_newsitem_model': len(newsitem_models) == 1,
        'newsitem_results': newsitem_results,
        'search_form': SearchForm(request.GET if request.GET else None),
        'query_string': query,
    })


def index(request, pk):
    newsindex = get_object_or_404(
        Page.objects.specific().type(NewsIndexMixin), pk=pk)
    NewsItem = newsindex.get_newsitem_model()

    if not user_can_edit_newsitem(request.user, NewsItem):
        raise PermissionDenied()

    newsitem_list = NewsItem.objects.filter(newsindex=newsindex)

    query = None
    try:
        query = request.GET['q']
    except KeyError:
        pass
    else:
        backend = get_search_backend()
        newsitem_list = backend.search(query, newsitem_list)

    paginator, page = paginate(request, newsitem_list)

    return render(request, 'wagtailnews/index.html', {
        'newsindex': newsindex,
        'page': page,
        'paginator': paginator,
        'newsitem_list': page.object_list,
        'newsitem_perms': perms_for_template(request, NewsItem),
        'query_string': query,
    })


def get_newsitem_model(model_string):
    """
    Get the NewsItem model from a model string. Raises ValueError if the model
    string is invalid, or references a model that is not a NewsItem.
    """
    try:
        NewsItem = apps.get_model(model_string)
        assert issubclass(NewsItem, AbstractNewsItem)
    except (ValueError, LookupError, AssertionError):
        raise ValueError('Invalid news item model string'.format(model_string))
    return NewsItem


def choose_modal(request):
    try:
        newsitem_model_string = request.GET['type']
        NewsItem = get_newsitem_model(newsitem_model_string)
    except (ValueError, KeyError):
        raise Http404

    newsitem_list = NewsItem.objects.all()

    # Search
    is_searching = False
    search_query = None
    if 'q' in request.GET:
        search_form = SearchForm(request.GET, placeholder="Search news")

        if search_form.is_valid():
            search_query = search_form.cleaned_data['q']

            search_backend = get_search_backend()
            newsitem_list = search_backend.search(search_query, newsitem_list)
            is_searching = True

    else:
        search_form = SearchForm()

    # Pagination
    paginator, paginated_items = paginate(request, newsitem_list, per_page=10)

    # If paginating or searching, render "results.html" - these views are
    # accessed via AJAX so do not need the modal wrapper
    if request.GET.get('results', None) == 'true':
        return render(request, "wagtailnews/chooser/search_results.html", {
            'query_string': search_query,
            'items': paginated_items,
            'is_searching': is_searching,
        })

    return render_modal_workflow(
        request,
        'wagtailnews/chooser/chooser.html', 'wagtailnews/chooser/choose.js',
        {
            'query_string': search_query,
            'newsitem_type': newsitem_model_string,
            'items': paginated_items,
            'is_searchable': True,
            'is_searching': is_searching,
            'search_form': search_form,
        }
    )


def chosen_modal(request, pk, newsitem_pk):
    newsindex = get_object_or_404(
        Page.objects.specific().type(NewsIndexMixin), pk=pk)
    NewsItem = newsindex.get_newsitem_model()

    newsitem = get_object_or_404(NewsItem, pk=newsitem_pk)

    return render_modal_workflow(request, None, 'wagtailnews/chooser/chosen.js', {
        'newsitem_json': json.dumps({
            'id': newsitem.id,
            'string': str(newsitem),
            'edit_link': reverse('wagtailnews:edit', kwargs={
                'pk': newsindex.pk, 'newsitem_pk': newsitem.pk}),
        }),
    })

import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.six import text_type
from wagtail.wagtailadmin.forms import SearchForm as AdminSearchForm
from wagtail.wagtailadmin.modal_workflow import render_modal_workflow
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.backends import get_search_backend
from wagtailnews.utils.pagination import paginate

from ..models import NEWSINDEX_MODEL_CLASSES, NewsIndexMixin
from ..permissions import (perms_for_template, user_can_edit_news,
                           user_can_edit_newsitem)


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

    return render(request, 'wagtailnews/index.html', {
        'newsindex': newsindex,
        'newsitem_list': newsitem_list,
        'newsitem_perms': perms_for_template(request, NewsItem),
    })


def choose_modal(request, pk):
    newsindex = get_object_or_404(
        Page.objects.specific().type(NewsIndexMixin), pk=pk)
    NewsItem = newsindex.get_newsitem_model()
    items = NewsItem.objects.all()

    # Search
    is_searching = False
    search_query = None
    if 'q' in request.GET:
        search_form = AdminSearchForm(request.GET, placeholder=("Search %(snippet_type_name)s") % {
            'snippet_type_name': 'News'
        })

        if search_form.is_valid():
            search_query = search_form.cleaned_data['q']

            search_backend = get_search_backend()
            items = search_backend.search(search_query, items)
            is_searching = True

    else:
        search_form = AdminSearchForm()

    # Pagination
    paginator, paginated_items = paginate(request, items, per_page=10)

    # If paginating or searching, render "results.html"
    if request.GET.get('results', None) == 'true':
        return render(request, "wagtailnews/chooser/search_results.html", {
            'items': paginated_items,
            'query_string': search_query,
            'is_searching': is_searching,
        })

    return render_modal_workflow(
        request,
        'wagtailnews/chooser/chooser.html', 'wagtailnews/chooser/choose.js',
        {
            'snippet_type_name': 'Car',
            'items': paginated_items,
            'is_searchable': True,
            'search_form': search_form,
            'query_string': search_query,
            'is_searching': is_searching,
            'pk': pk,
        }
    )


def chosen_modal(request, pk, newsitem_pk):
    newsindex = get_object_or_404(
        Page.objects.specific().type(NewsIndexMixin), pk=pk)
    NewsItem = newsindex.get_newsitem_model()

    item = get_object_or_404(NewsItem, newsindex=newsindex, pk=newsitem_pk)

    snippet_json = json.dumps({
        'id': item.id,
        'string': text_type(item),
    })

    return render_modal_workflow(
        request,
        None, 'wagtailnews/chooser/chosen.js',
        {
            'snippet_json': snippet_json,
        }
    )

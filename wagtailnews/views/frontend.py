from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.six.moves.urllib.parse import urlparse

from ..conf import paginate


def _newsitem_list(request, newsindex, newsitem_list, extra_context):
    paginator, page = paginate(request, newsitem_list)
    context = {
        'self': newsindex,
        'page': newsindex,
        'paginator': paginator,
        'newsitem_page': page,
        'newsitem_list': page.object_list,
    }
    context.update(extra_context)
    return render(request, newsindex.get_template(request), context)


def news_index(request, newsindex):
    now = timezone.now()
    NewsItem = newsindex.get_newsitem_model()
    newsitem_list = NewsItem.objects.live().filter(
        newsindex=newsindex, date__lte=now)
    return _newsitem_list(request, newsindex, newsitem_list, {
        'list_type': 'index',
    })


def news_year(request, newsindex, year):
    NewsItem = newsindex.get_newsitem_model()
    newsitem_list = NewsItem.objects.live().filter(
        newsindex=newsindex, date__year=year)
    return _newsitem_list(request, newsindex, newsitem_list, {
        'list_type': 'index',
    })


def news_month(request, newsindex, year, month):
    NewsItem = newsindex.get_newsitem_model()
    newsitem_list = NewsItem.objects.live().filter(
        newsindex=newsindex, date__year=year, date__month=month)
    return _newsitem_list(request, newsindex, newsitem_list, {
        'list_type': 'index',
    })


def news_day(request, newsindex, year, month, day):
    NewsItem = newsindex.get_newsitem_model()
    newsitem_list = NewsItem.objects.live().filter(
        newsindex=newsindex, date__year=year, date__month=month, date__day=day)
    return _newsitem_list(request, newsindex, newsitem_list, {
        'list_type': 'index',
    })


def newsitem_detail(request, newsindex, year, month, day, pk, slug):
    NewsItem = newsindex.get_newsitem_model()
    newsitem = get_object_or_404(NewsItem.objects.live(),
                                 newsindex=newsindex, pk=pk)

    newsitem_path = urlparse(newsitem.url(), allow_fragments=True).path
    if request.path != newsitem_path:
        return redirect(newsitem.url())

    template = newsitem.get_template(request)
    context = newsitem.get_context(request, year=year, month=month, day=day,
                                   pk=pk, slug=slug)
    return render(request, template, context)

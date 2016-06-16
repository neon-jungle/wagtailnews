from django.shortcuts import redirect, render, get_object_or_404

from wagtail.wagtailcore.models import Page

from ..models import NewsIndexMixin


def choose(request):
    newsindex_list = Page.objects.type(NewsIndexMixin)
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
    newsitem_list = NewsItem.objects.filter(newsindex=newsindex)

    return render(request, 'wagtailnews/index.html', {
        'newsindex': newsindex,
        'newsitem_list': newsitem_list,
    })

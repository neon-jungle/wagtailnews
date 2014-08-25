from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

# TODO Swap with django.utils.lru_cache.lru_cache at Django 1.7
from django.utils.functional import memoize

from wagtail.wagtailadmin.edit_handlers import (
    ObjectList, extract_panel_definitions_from_model_class, get_form_for_model)
from wagtail.wagtailcore.models import Page

from ..models import get_newsindex_content_types


def get_newsitem_edit_handler(NewsItem):
    panels = extract_panel_definitions_from_model_class(
        NewsItem, exclude=['newsindex'])
    EditHandler = ObjectList(panels)
    return EditHandler
get_newsitem_edit_handler = memoize(get_newsitem_edit_handler, {}, 1)


def get_newsitem_form(NewsItem, EditHandler):
    return get_form_for_model(
        NewsItem,
        formsets=EditHandler.required_formsets(),
        widgets=EditHandler.widget_overrides(),
        exclude=['newsindex'])
get_newsitem_form = memoize(get_newsitem_form, {}, 2)


def create(request, pk):
    newsindex = get_object_or_404(Page, pk=pk, content_type__in=get_newsindex_content_types()).specific
    NewsItem = newsindex.get_newsitem_model()

    newsitem = NewsItem()
    EditHandler = get_newsitem_edit_handler(NewsItem)
    EditForm = get_newsitem_form(NewsItem, EditHandler)

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES)

        if form.is_valid():
            print newsitem.pk
            newsitem = form.save(commit=False)
            print newsitem.pk
            newsitem.newsindex = newsindex
            newsitem.save()

            messages.success(request, _('The news post "{0!s}" has been added').format(newsitem))
            return redirect('wagtailnews_index', pk=newsindex.pk)
        else:
            messages.error(request, _('The news post could not be created due to validation errors'))
            edit_handler = EditHandler(instance=newsitem, form=form)
    else:
        form = EditForm(instance=newsitem)
        edit_handler = EditHandler(instance=newsitem, form=form)

    return render(request, 'wagtailnews/create.html', {
        'newsindex': newsindex,
        'form': form,
        'edit_handler': edit_handler,
    })


def edit(request, pk, newsitem_pk):
    newsindex = get_object_or_404(Page, pk=pk, content_type__in=get_newsindex_content_types()).specific
    NewsItem = newsindex.get_newsitem_model()
    newsitem = get_object_or_404(NewsItem, newsindex=newsindex, pk=newsitem_pk)

    EditHandler = get_newsitem_edit_handler(NewsItem)
    EditForm = get_newsitem_form(NewsItem, EditHandler)

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES, instance=newsitem)

        if form.is_valid():
            print newsitem.pk
            newsitem = form.save(commit=False)
            print newsitem.pk
            newsitem.save()

            messages.success(request, _('The news post "{0!s}" has been updated').format(newsitem))
            return redirect('wagtailnews_index', pk=newsindex.pk)
        else:
            messages.error(request, _('The news post could not be updated due to validation errors'))
            edit_handler = EditHandler(instance=newsitem, form=form)
    else:
        form = EditForm(instance=newsitem)
        edit_handler = EditHandler(instance=newsitem, form=form)

    return render(request, 'wagtailnews/edit.html', {
        'newsindex': newsindex,
        'newsitem': newsitem,
        'form': form,
        'edit_handler': edit_handler,
    })


def delete(request, pk, newsitem_pk):
    newsindex = get_object_or_404(Page, pk=pk, content_type__in=get_newsindex_content_types()).specific
    NewsItem = newsindex.get_newsitem_model()
    newsitem = get_object_or_404(NewsItem, newsindex=newsindex, pk=newsitem_pk)

    if request.method == 'POST':
        newsitem.delete()
        return redirect('wagtailnews_index', pk=pk)

    return render(request, 'wagtailnews/delete.html', {
        'newsindex': newsindex,
        'newsitem': newsitem,
    })

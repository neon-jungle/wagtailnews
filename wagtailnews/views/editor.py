from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.utils.lru_cache import lru_cache

from wagtail.wagtailadmin.edit_handlers import (
    ObjectList, extract_panel_definitions_from_model_class)
from wagtail.wagtailcore.models import Page

from ..models import get_newsindex_content_types


@lru_cache(maxsize=None)
def get_newsitem_edit_handler(NewsItem):
    panels = extract_panel_definitions_from_model_class(
        NewsItem, exclude=['newsindex'])
    return ObjectList(panels).bind_to_model(NewsItem)


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def create(request, pk):
    newsindex = get_object_or_404(Page, pk=pk, content_type__in=get_newsindex_content_types()).specific
    NewsItem = newsindex.get_newsitem_model()

    newsitem = NewsItem(newsindex=newsindex)
    EditHandler = get_newsitem_edit_handler(NewsItem)
    EditForm = EditHandler.get_form_class(NewsItem)

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES, instance=newsitem)

        if form.is_valid():
            form.save()

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


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def edit(request, pk, newsitem_pk):
    newsindex = get_object_or_404(Page, pk=pk, content_type__in=get_newsindex_content_types()).specific
    NewsItem = newsindex.get_newsitem_model()
    newsitem = get_object_or_404(NewsItem, newsindex=newsindex, pk=newsitem_pk)

    EditHandler = get_newsitem_edit_handler(NewsItem)
    EditForm = EditHandler.get_form_class(NewsItem)

    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES, instance=newsitem)

        if form.is_valid():
            form.save()

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


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
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

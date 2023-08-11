import logging

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms.search import SearchForm
from wagtail.admin.ui.tables import Column
from wagtail.admin.views.generic import IndexView
from wagtail.admin.views.generic import chooser as chooser_views
from wagtail.admin.viewsets.chooser import ChooserViewSet
from wagtail.models import Page
from wagtail.search.backends import get_search_backend

from ..models import NEWSINDEX_MODEL_CLASSES, NewsIndexMixin
from ..permissions import (
    format_perm, perms_for_template, user_can_edit_news, user_can_edit_newsitem)

LOGGER = logging.getLogger(__name__)


def get_allowed_news_types(user):
    """Get a list of all NewsIndex models that the user can edit"""
    return [
        NewsIndex
        for NewsIndex in NEWSINDEX_MODEL_CLASSES
        if user_can_edit_newsitem(user, NewsIndex.get_newsitem_model())
    ]


def choose(request):
    if not user_can_edit_news(request.user):
        raise PermissionDenied

    allowed_news_types = get_allowed_news_types(request.user)

    allowed_cts = ContentType.objects.get_for_models(*allowed_news_types).values()
    newsindex_list = Page.objects.filter(content_type__in=allowed_cts).specific()
    newsindex_count = newsindex_list.count()

    if newsindex_count == 1:
        newsindex = newsindex_list.first()
        return redirect("wagtailnews:index", pk=newsindex.pk)

    return render(
        request,
        "wagtailnews/choose.html",
        {
            "has_news": newsindex_count != 0,
            "newsindex_list": (
                (newsindex, newsindex.content_type.model_class()._meta.verbose_name)
                for newsindex in newsindex_list
            ),
        },
    )


def _search_newsitems(request, newsitem_models, query):
    backend = get_search_backend()

    for NewsItem in newsitem_models:
        results = backend.autocomplete(query, NewsItem)[:10]
        for r in results:
            yield r


def search(request):
    if not user_can_edit_news(request.user):
        raise PermissionDenied

    query = request.GET.get("q", "")

    allowed_news_types = get_allowed_news_types(request.user)
    # FIXME: this is crap, need to construct a single query for all types
    # to search by relevance however that's not currently possible in
    # a backend agnostic way :(
    newsitem_models = [
        NewsIndex.get_newsitem_model() for NewsIndex in allowed_news_types
    ]
    if query:
        newsitem_results = list(_search_newsitems(request, newsitem_models, query))
    else:
        newsitem_results = []

    if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        template = "wagtailnews/newsitem_list.html"
    else:
        template = "wagtailnews/search.html"

    return render(
        request,
        template,
        {
            "single_result_type": len(newsitem_results) == 1,
            "single_newsitem_model": len(newsitem_models) == 1,
            "object_list": newsitem_results,
            "search_form": SearchForm(request.GET if request.GET else None),
            "query_string": query,
            "is_searching": True,
        },
    )


class NewsItemIndexView(IndexView):
    results_template_name = "wagtailnews/newsitem_list.html"
    template_name = "wagtailnews/index.html"
    page_title = _("News")
    is_searchable = True
    search_fields = ("title",)

    def dispatch(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=self.kwargs["pk"]
        )
        NewsItem = self.newsindex.get_newsitem_model()
        if not user_can_edit_newsitem(request.user, NewsItem):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_edit_url(self, instance):
        return reverse(
            "wagtailnews:edit",
            kwargs={
                "pk": self.newsindex.pk,
                "newsitem_pk": instance.pk,
            },
        )

    def get_add_url(self):
        if self.request.user.has_perm(
            format_perm(self.newsindex.get_newsitem_model(), "add")
        ):
            return reverse(
                "wagtailnews:create",
                kwargs={
                    "pk": self.newsindex.pk,
                },
            )
        return None

    def get_base_queryset(self):
        newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=self.kwargs["pk"]
        )
        NewsItem = newsindex.get_newsitem_model()
        newsitem_list = NewsItem.objects.filter(newsindex=newsindex)
        return newsitem_list

    def get_queryset(self):
        return self.get_base_queryset()

    def search_queryset(self, queryset):
        search_query = self.request.GET.get("q", "")
        if search_query:
            backend = get_search_backend()
            queryset = backend.autocomplete(search_query, queryset)
            return queryset.get_queryset()
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)
        NewsItem = self.newsindex.get_newsitem_model()
        # Can't customise the form properly (search_url) so just replace the whole thing
        search = render_to_string(
            "wagtailnews/search_form.html",
            {
                "search_form": SearchForm(
                    self.request.GET if self.request.GET else None
                ),
            },
        )
        context.update(
            {
                "newsindex": self.newsindex,
                "newsitem_perms": perms_for_template(self.request, NewsItem),
                "search": search,
            }
        )
        return context


class IndexFilterMixin(forms.Form):
    def __init__(self, *args, indexes=None, **kwargs):
        super().__init__(*args, **kwargs)

        if indexes:
            index_choices = [("", _("All indexes"))] + [
                (index.id, index) for index in indexes
            ]
            self.fields["index_id"] = forms.ChoiceField(
                label=_("News page"),
                choices=index_choices,
                required=False,
                widget=forms.Select(attrs={"data-chooser-modal-search-filter": True}),
            )

    def filter(self, objects):
        index_id = self.cleaned_data.get("index_id")
        if index_id:
            objects = objects.filter(newsindex=index_id)
        return super().filter(objects)


class BaseNewsItemChooserMixin:
    def get_filter_form_class(self):
        filter_class = super().get_filter_form_class()

        allowed_news_types = get_allowed_news_types(self.request.user)

        allowed_cts = ContentType.objects.get_for_models(*allowed_news_types).values()
        self.newsindex_list = Page.objects.filter(
            content_type__in=allowed_cts
        ).specific()
        newsindex_count = self.newsindex_list.count()
        if newsindex_count > 1:
            return type(
                "FilterForm",
                (IndexFilterMixin, filter_class),
                {},
            )
        return filter_class

    def get_filter_form(self):
        FilterForm = self.get_filter_form_class()
        if self.newsindex_list.count() > 1:
            return FilterForm(self.request.GET, indexes=self.newsindex_list)
        return FilterForm(self.request.GET)

    @property
    def columns(self):
        columns = [self.title_column]
        columns += [Column("status", label=_("Status"), accessor="status_button")]
        return columns


class NewsItemChooseResultsView(
    BaseNewsItemChooserMixin, chooser_views.ChooseResultsView
):
    pass


class NewsItemChooseView(BaseNewsItemChooserMixin, chooser_views.ChooseView):
    pass


class NewsItemChosenView(chooser_views.ChosenView):
    def get_edit_item_url(self, instance):
        return reverse(
            "wagtailnews:edit",
            kwargs={
                "pk": instance.newsindex.pk,
                "newsitem_pk": instance.pk,
            },
        )


def choooser_viewset_factory(model):
    model_name = model.__name__
    nice_name = model._meta.verbose_name

    return type(
        f"{model_name}ChooserViewSet",
        (ChooserViewSet,),
        {
            "model": model,
            "icon": "grip",
            "choose_one_text": f"Choose {nice_name}",
            "choose_another_text": f"Choose another {nice_name}",
            "link_to_chosen_text": f"Edit this {nice_name}",
            "choose_view_class": NewsItemChooseView,
            "choose_results_view_class": NewsItemChooseResultsView,
            "chosen_view_class": NewsItemChosenView,
        },
    )(f"{model_name.lower()}_chooser")

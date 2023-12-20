from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.search import SearchArea

from wagtailnews.views.chooser import choooser_viewset_factory

from . import urls
from .menu import NewsMenuItem
from .models import NEWSINDEX_MODEL_CLASSES
from .permissions import user_can_edit_news


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("news/", include(urls)),
    ]


@hooks.register("construct_main_menu")
def construct_main_menu(request, menu_items):
    if user_can_edit_news(request.user):
        menu_items.append(NewsMenuItem())


class NewsItemSearchArea(SearchArea):
    """Admin search for news items."""

    def __init__(self, **kwargs):
        super(NewsItemSearchArea, self).__init__(
            _("News"),
            reverse("wagtailnews:search"),
            classname="icon icon-grip",
            order=250,
            **kwargs,
        )

    def is_shown(self, request):
        return user_can_edit_news(request.user)


@hooks.register("register_admin_search_area")
def register_news_search():
    """Register news search."""
    return NewsItemSearchArea()


@hooks.register("register_permissions")
def newsitem_permissions():
    newsitem_models = [model.get_newsitem_model() for model in NEWSINDEX_MODEL_CLASSES]
    newsitem_cts = ContentType.objects.get_for_models(*newsitem_models).values()
    return Permission.objects.filter(content_type__in=newsitem_cts)


@hooks.register("register_admin_viewset")
def register_newsitem_chooser_viewsets():
    return [
        choooser_viewset_factory(model.get_newsitem_model())
        for model in NEWSINDEX_MODEL_CLASSES
    ]

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from . import urls
from .models import NEWSINDEX_MODEL_CLASSES
from .permissions import user_can_edit_news


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^news/', include(urls)),
    ]


@hooks.register('construct_main_menu')
def construct_main_menu(request, menu_items):
    if user_can_edit_news(request.user):
        menu_items.append(
            MenuItem(_('News'), urlresolvers.reverse('wagtailnews_choose'),
                     classnames='icon icon-grip', order=250)
        )


@hooks.register('register_permissions')
def newsitem_permissions():
    newsitem_models = [model.get_newsitem_model()
                       for model in NEWSINDEX_MODEL_CLASSES]
    newsitem_cts = ContentType.objects.get_for_models(*newsitem_models).values()
    return Permission.objects.filter(content_type__in=newsitem_cts)

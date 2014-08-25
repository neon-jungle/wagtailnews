from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import chooser, editor


urlpatterns = [
    url(r'^$', chooser.choose,
        name='wagtailnews_choose'),
    url(r'^(?P<pk>\d+)/$', chooser.index,
        name='wagtailnews_index'),
    url(r'^(?P<pk>\d+)/create/$', editor.create,
        name='wagtailnews_create'),
    url(r'^(?P<pk>\d+)/edit/(?P<newsitem_pk>.*)/$', editor.edit,
        name='wagtailnews_edit'),
    url(r'^(?P<pk>\d+)/delete/(?P<newsitem_pk>.*)/$', editor.delete,
        name='wagtailnews_delete'),
]

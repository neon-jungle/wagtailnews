from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from .views import chooser, editor

app_name = 'wagtailnews'
urlpatterns = [
    url(r'^$', chooser.choose,
        name='choose'),
    url(r'^search/$', chooser.search,
        name='search'),
    url(r'^(?P<pk>\d+)/$', chooser.index,
        name='index'),
    url(r'^(?P<pk>\d+)/create/$', editor.create,
        name='create'),
    url(r'^(?P<pk>\d+)/edit/(?P<newsitem_pk>.*)/$', editor.edit,
        name='edit'),
    url(r'^(?P<pk>\d+)/unpublish/(?P<newsitem_pk>.*)/$', editor.unpublish,
        name='unpublish'),
    url(r'^(?P<pk>\d+)/delete/(?P<newsitem_pk>.*)/$', editor.delete,
        name='delete'),
    url(r'^(?P<pk>\d+)/view_draft/(?P<newsitem_pk>.*)/$', editor.view_draft,
        name='view_draft'),
    # Choosers
    url(r'^chooser/$', chooser.choose_modal, name='chooser'),
    url(r'^chooser/(?P<pk>\d+)/(?P<newsitem_pk>\d+)/$', chooser.chosen_modal, name='chosen'),
]

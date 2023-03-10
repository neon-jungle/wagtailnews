from django.urls import re_path

from .views import chooser, editor

app_name = 'wagtailnews'
urlpatterns = [
    re_path(r'^$', chooser.choose,
        name='choose'),
    re_path(r'^search/$', chooser.search,
        name='search'),
    re_path(r'^(?P<pk>\d+)/$', chooser.index,
        name='index'),
    re_path(r'^(?P<pk>\d+)/create/$', editor.create,
        name='create'),
    re_path(r'^(?P<pk>\d+)/edit/(?P<newsitem_pk>.*)/$', editor.edit,
        name='edit'),
    re_path(r'^(?P<pk>\d+)/unpublish/(?P<newsitem_pk>.*)/$', editor.unpublish,
        name='unpublish'),
    re_path(r'^(?P<pk>\d+)/delete/(?P<newsitem_pk>.*)/$', editor.delete,
        name='delete'),
    re_path(r'^(?P<pk>\d+)/view_draft/(?P<newsitem_pk>.*)/$', editor.view_draft,
        name='view_draft'),
    # Choosers
    re_path(r'^chooser/$', chooser.choose_modal, name='chooser'),
    re_path(r'^chooser/(?P<pk>\d+)/(?P<newsitem_pk>\d+)/$', chooser.chosen_modal, name='chosen'),
]

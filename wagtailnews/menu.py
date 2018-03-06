from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.menu import MenuItem

from .permissions import user_can_edit_news


class NewsMenuItem(MenuItem):
    def __init__(self, label=_('News'), url=reverse_lazy('wagtailnews:choose'),
                 classnames='icon icon-grip', order=250, **kwargs):
        super(NewsMenuItem, self).__init__(
            label, url, classnames=classnames, order=order, **kwargs)

    def is_shown(self, request):
        return user_can_edit_news(request.user)

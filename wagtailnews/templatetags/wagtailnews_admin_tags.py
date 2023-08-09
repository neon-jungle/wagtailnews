from django.template.library import Library
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext as _

register = Library()


@register.simple_tag()
def newsitem_status(newsitem, link=True):
    return newsitem.status_button(link=link)

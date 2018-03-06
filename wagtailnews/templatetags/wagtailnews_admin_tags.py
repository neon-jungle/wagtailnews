from django.template.library import Library
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext as _

register = Library()


@register.simple_tag()
def newsitem_status(newsitem, link=True):
    buttons = []
    output = []
    if newsitem.live:
        buttons.append({
            'href': newsitem.url,
            'primary': True,
            'text': _('live'),
        })
    if newsitem.has_unpublished_changes or not newsitem.live:
        buttons.append({
            'href': reverse('wagtailnews:view_draft', kwargs={
                'pk': newsitem.newsindex.pk, 'newsitem_pk': newsitem.pk,
            }),
            'primary': False,
            'text': _('draft'),
        })

    if link:
        for button in buttons:
            output.append(format_html(
                '<a href="{}" target="_blank" class="{}">{}</a>',
                button['href'],
                'status-tag primary' if button['primary'] else 'status-tag',
                button['text']))
    else:
        for button in buttons:
            output.append(format_html(
                '<span class="{}">{}</span>',
                'status-tag primary' if button['primary'] else 'status-tag',
                button['text']))

    return mark_safe(' + '.join(output))

from django.template.library import Library

register = Library()


@register.simple_tag()
def newsitem_status(newsitem, link=True):
    return newsitem.status_button(link=link)

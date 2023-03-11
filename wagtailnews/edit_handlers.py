from django.template.loader import render_to_string

import django
if django.VERSION >= (4, 0):
  from django.utils.encoding import force_str
else:
  from django.utils.encoding import force_text as force_str

from django.utils.safestring import mark_safe

import wagtail
if wagtail.VERSION >= (4, 2):
  from wagtail.admin.panels import FieldPanel
elif wagtail.VERSION >= (3, 0):
  from wagtail.admin.edit_handlers import FieldPanel
else:
  from wagtail.admin.edit_handlers import BaseChooserPanel as FieldPanel

from .widgets import AdminNewsChooser


class NewsChooserPanel(FieldPanel):
    """
    An edit handler for editors to pick a news item.
    Takes the field name as the only argument.
    For example:

    .. code-block:: python

        class FooPage(Page):
            news_item = models.ForeignKey('news.NewsItem')

            content_panels = Page.content_panels + [
                NewsChooserPanel('news_item')
            }
    """
    model = None
    field_name = None

    object_type_name = 'item'

    _target_model = None

    def widget_overrides(self):
        if self.model:
            return {self.field_name: AdminNewsChooser(model=self.target_model())}
        return {}

    def target_model(self):
        if self._target_model is None:
            field = self.model._meta.get_field(self.field_name)
            self._target_model = field.remote_field.model

        return self._target_model

    def render_as_field(self):
        instance_obj = self.get_chosen_item()
        return mark_safe(render_to_string(self.field_template, {
            'field': self.bound_field,
            self.object_type_name: instance_obj,
            'newsitem_type_name': self.get_newsitem_type_name(),
        }))

    def get_newsitem_type_name(self):
        return force_str(self.target_model()._meta.verbose_name)

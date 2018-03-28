from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from wagtail.admin.edit_handlers import BaseChooserPanel

from .widgets import AdminNewsChooser


class NewsChooserPanel(BaseChooserPanel):
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
        return force_text(self.target_model()._meta.verbose_name)

from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from wagtail.wagtailadmin.edit_handlers import BaseChooserPanel

from .widgets import AdminNewsChooser


class BaseNewsChooserPanel(BaseChooserPanel):
    object_type_name = 'item'

    _target_model = None
    _target_content_type = None

    @classmethod
    def widget_overrides(cls):
        return {cls.field_name: AdminNewsChooser(model=cls.target_model())}

    @classmethod
    def target_model(cls):
        if cls._target_model is None:
            cls._target_model = cls.model._meta.get_field(cls.field_name).rel.model

        return cls._target_model

    def render_as_field(self):
        instance_obj = self.get_chosen_item()
        return mark_safe(render_to_string(self.field_template, {
            'field': self.bound_field,
            self.object_type_name: instance_obj,
            'snippet_type_name': self.get_snippet_type_name(),
        }))

    @classmethod
    def get_snippet_type_name(cls):
        return force_text(cls.target_model()._meta.verbose_name)


class NewsChooserPanel(object):
    def __init__(self, field_name, snippet_type=None):
        self.field_name = field_name
        self.snippet_type = snippet_type

    def bind_to_model(self, model):
        return type(str('_NewsChooserPanel'), (BaseNewsChooserPanel,), {
            'model': model,
            'field_name': self.field_name,
            'snippet_type': self.snippet_type,
        })

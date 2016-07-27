from __future__ import absolute_import, unicode_literals

import json

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.widgets import AdminChooser

from wagtailnews.utils import model_string


class AdminNewsChooser(AdminChooser):

    class Media():
        js = ['js/news_chooser.js']

    def __init__(self, model, **kwargs):
        self.target_model = model
        name = self.target_model._meta.verbose_name
        self.choose_one_text = _('Choose %s') % name
        self.choose_another_text = _('Choose another %s') % name
        self.link_to_chosen_text = _('Edit this %s') % name

        super(AdminNewsChooser, self).__init__(**kwargs)

    def render_html(self, name, value, attrs):
        instance, value = self.get_instance_and_id(self.target_model, value)

        original_field_html = super(AdminNewsChooser, self).render_html(name, value, attrs)

        return render_to_string("wagtailnews/widgets/news_chooser.html", {
            'widget': self,
            'original_field_html': original_field_html,
            'attrs': attrs,
            'value': value,
            'item': instance,
        })

    def render_js_init(self, id_, name, value):
        return "createNewsChooser({id}, {type});".format(
            id=json.dumps(id_),
            type=json.dumps(model_string(self.target_model)))

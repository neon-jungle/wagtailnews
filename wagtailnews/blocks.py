from django.utils.functional import cached_property
from wagtail.core.blocks import ChooserBlock
from wagtail.core.utils import resolve_model_string


class NewsChooserBlock(ChooserBlock):
    """
    A StreamField block for editors to pick a news item.
    Takes the news item class as its only argument.
    For example:

    .. code-block:: python

        class FooPage(Page):
            content = StreamField([
                ('text', RichTextField()),
                ('news', NewsChooserBlock('news.NewsItem')),
            ])
    """
    def __init__(self, target_model, **kwargs):
        super(NewsChooserBlock, self).__init__(**kwargs)
        self._target_model = target_model

    @cached_property
    def target_model(self):
        return resolve_model_string(self._target_model)

    @cached_property
    def widget(self):
        from wagtailnews.widgets import AdminNewsChooser
        return AdminNewsChooser(self.target_model)

    def deconstruct(self):
        path, args, kwargs = super(NewsChooserBlock, self).deconstruct()
        kwargs['target_model'] = self.target_model._meta.label
        return path, args, kwargs

    class Meta:
        icon = "grip"

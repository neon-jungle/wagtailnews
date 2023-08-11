from django.utils.functional import cached_property
from wagtail.blocks import ChooserBlock
from wagtail.coreutils import resolve_model_string

from .views.chooser import choooser_viewset_factory


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
        viewset = choooser_viewset_factory(self.target_model)
        return viewset.widget_class()

    # only used in migrations, which are useless anyway for streamfields
    def deconstruct(self):
        name, args, kwargs = super().deconstruct()

        if args:
            args = args[1:]  # Remove the args target_model

        kwargs["target_model"] = self.target_model._meta.label_lower
        return name, args, kwargs

    class Meta:
        icon = "grip"

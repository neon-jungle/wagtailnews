from functools import lru_cache

from django.core.exceptions import PermissionDenied
from django.forms import Media
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin import messages
from wagtail.admin.panels import (
    ObjectList, extract_panel_definitions_from_model_class)
from wagtail.admin.ui.side_panels import PreviewSidePanel
from wagtail.admin.views.generic import (
    CreateView, DeleteView, EditView, UnpublishView)
from wagtail.admin.views.generic.preview import \
    PreviewOnEdit as GenericPreviewOnEdit
from wagtail.models import Page

from wagtailnews.permissions import format_perm, format_perms

from .. import signals
from ..forms import SaveActionSet
from ..models import NewsIndexMixin


@lru_cache(maxsize=None)
def get_newsitem_edit_handler(NewsItem):
    if hasattr(NewsItem, "edit_handler"):
        return NewsItem.edit_handler.bind_to_model(NewsItem)

    panels = extract_panel_definitions_from_model_class(NewsItem, exclude=["newsindex"])
    return ObjectList(panels).bind_to_model(NewsItem)


class NewItemPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perms(
            format_perms(self.newsindex.get_newsitem_model(), self.permissions_required)
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class PreviewSidePanel(PreviewSidePanel):
    def __init__(self, object, request, newsindex):
        self.newsindex = newsindex
        if not object:
            object = newsindex.get_newsitem_model()(newsindex=newsindex)
        if object.id:
            preview_url = reverse(
                "wagtailnews:preview_on_edit",
                kwargs={
                    "index_pk": self.newsindex.pk,
                    "newsitem_pk": object.pk,
                },
            )
        else:
            preview_url = reverse(
                "wagtailnews:preview_on_create",
                kwargs={"index_pk": self.newsindex.pk},
            )
        super().__init__(object, request, preview_url=preview_url)


class NewsItemSidePanels:
    def __init__(self, request, object, newsindex):
        self.request = request
        self.object = object

        self.side_panels = [
            PreviewSidePanel(object, request, newsindex),
        ]

    def __iter__(self):
        return iter(sorted(self.side_panels, key=lambda p: p.order))

    @cached_property
    def media(self):
        media = Media()
        for panel in self:
            media += panel.media
        return media


class NewsItemAdminMixin:
    def setup(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=kwargs["pk"]
        )
        super().setup(request, *args, **kwargs)

    def get_add_url(self):
        return reverse("wagtailnews:create", kwargs={"pk": self.kwargs["pk"]})

    def get_edit_url(self):
        return reverse(
            "wagtailnews:edit",
            kwargs={"pk": self.kwargs["pk"], "newsitem_pk": self.object.pk},
        )

    def get_success_url(self):
        return reverse("wagtailnews:index", kwargs={"pk": self.kwargs["pk"]})

    def get_panel(self):
        NewsItem = self.newsindex.get_newsitem_model()
        return get_newsitem_edit_handler(NewsItem)

    def save_instance(self):
        newsitem = self.form.save(commit=False)
        action = SaveActionSet.from_post_data(self.request.POST)
        created = False
        if not newsitem.pk:
            # Must be creation
            created = True
            newsitem.newsindex = self.newsindex
            newsitem.live = action is SaveActionSet.publish
            newsitem.newsindex = self.newsindex
            newsitem.save()

        NewsItem = self.newsindex.get_newsitem_model()
        revision = newsitem.save_revision(user=self.request.user)

        # TODO replace with DraftStateMixin
        if action is SaveActionSet.publish:
            revision.publish()
            signals.newsitem_published.send(
                sender=NewsItem, instance=newsitem, created=created
            )

        elif action is SaveActionSet.draft:
            signals.newsitem_draft_saved.send(
                sender=NewsItem, instance=newsitem, created=created
            )

        return newsitem

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        side_panels = NewsItemSidePanels(self.request, self.object, self.newsindex)
        context.update(
            {
                "newsindex": self.newsindex,
                "newsitem_opts": self.newsindex.get_newsitem_model()._meta,
                # "in_explorer": True,  # hide minimap
                "side_panels": side_panels,
            }
        )
        return context


class CreateNewsItemView(NewItemPermissionMixin, NewsItemAdminMixin, CreateView):
    template_name = "wagtailnews/create.html"
    permissions_required = ["add", "change"]

    def get_success_message(self, instance):
        if instance.live:
            return _('The news post "{0!s}" has been published').format(instance)
        else:
            return _('A draft news post "{0!s}" has been created').format(instance)

    def get_success_buttons(self):
        return [messages.button(self.get_edit_url(), _("Edit"))]


class EditNewsItemView(NewItemPermissionMixin, NewsItemAdminMixin, EditView):
    template_name = "wagtailnews/edit.html"
    permissions_required = ["change"]

    def get_success_message(self):
        if self.object.live:
            return _('Your changes to "{0!s}" have been published').format(self.object)
        else:
            return _('Your changes to "{0!s}" have been saved as a draft').format(
                self.object
            )

    def get_success_buttons(self):
        return [messages.button(self.get_edit_url(), _("Edit"))]

    def get_object(self, queryset=None):
        self.object = self.newsindex.get_newsitem_model().objects.get(
            pk=self.kwargs["newsitem_pk"]
        )
        return self.object.get_latest_revision_as_newsitem()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["can_delete"] = self.request.user.has_perm(
            format_perm(self.newsindex.get_newsitem_model(), "delete")
        )
        return context


class UnpublishNewsItemView(NewItemPermissionMixin, UnpublishView):
    permissions_required = ["change"]

    def setup(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=kwargs["pk"]
        )
        self.model = self.newsindex.get_newsitem_model()
        super().setup(request, *args, **kwargs)
        # self.pk is set incorrectly by the parent class, and kwargs pk is stripped out by named parameter
        self.kwargs["pk"] = kwargs["pk"]
        self.pk = self.kwargs["newsitem_pk"]

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.newsindex.get_newsitem_model(),
            newsindex=self.newsindex,
            pk=self.kwargs["newsitem_pk"],
        )

    def get_success_buttons(self):
        if self.edit_url_name:
            return [
                messages.button(
                    reverse(
                        "wagtailnews:edit",
                        kwargs={"pk": self.kwargs["pk"], "newsitem_pk": self.object.pk},
                    ),
                    _("Edit"),
                )
            ]

    def get_next_url(self):
        return reverse("wagtailnews:index", kwargs={"pk": self.newsindex.pk})

    def get_unpublish_url(self):
        return reverse(
            "wagtailnews:unpublish",
            kwargs={"pk": self.kwargs["pk"], "newsitem_pk": self.object.pk},
        )

    def unpublish(self):
        self.object.unpublish()
        signals.newsitem_unpublished.send(
            sender=self.newsindex.get_newsitem_model(), instance=self.object
        )


class NewsItemDeleteView(NewItemPermissionMixin, DeleteView):
    success_message = _("%(object)s been deleted")
    permissions_required = ["delete"]

    def get_success_url(self):
        return reverse("wagtailnews:index", kwargs={"pk": self.newsindex.pk})

    def get_delete_url(self):
        return reverse(
            "wagtailnews:delete",
            kwargs={"pk": self.newsindex.pk, "newsitem_pk": self.object.pk},
        )

    def setup(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=kwargs["pk"]
        )
        self.object = get_object_or_404(
            self.newsindex.get_newsitem_model(),
            newsindex=self.newsindex,
            pk=kwargs["newsitem_pk"],
        )
        self.queryset = self.newsindex.get_newsitem_model().objects.live()  # pre 5.0
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.object

    def delete_action(self):
        super().delete_action()
        signals.newsitem_deleted.send(
            sender=self.newsindex.get_newsitem_model(), instance=self.object
        )


def view_draft(request, pk, newsitem_pk):
    newsindex = get_object_or_404(Page.objects.specific().type(NewsIndexMixin), pk=pk)
    NewsItem = newsindex.get_newsitem_model()
    newsitem = get_object_or_404(NewsItem, newsindex=newsindex, pk=newsitem_pk)
    newsitem = newsitem.get_latest_revision_as_newsitem()
    return newsitem.serve_preview(request, newsitem.default_preview_mode)


class PreviewOnEdit(GenericPreviewOnEdit):
    def setup(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=kwargs["index_pk"]
        )
        super().setup(request, *args, **kwargs)

    @property
    def session_key(self):
        return f"{self.session_key_prefix}{self.kwargs['newsitem_pk']}"

    def get_object(self):
        return get_object_or_404(
            self.newsindex.get_newsitem_model(),
            newsindex=self.newsindex,
            pk=self.kwargs["newsitem_pk"],
        ).get_latest_revision_as_newsitem()

    def get_form(self, querydict):
        NewsItem = self.newsindex.get_newsitem_model()
        edit_handler = get_newsitem_edit_handler(NewsItem)
        form_class = edit_handler.get_form_class()

        if querydict:
            return form_class(querydict, instance=self.object)

        return form_class(instance=self.object)


class PreviewOnCreate(PreviewOnEdit):
    @property
    def session_key(self):
        model = self.newsindex.get_newsitem_model()
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        return f"{self.session_key_prefix}{app_label}-{model_name}"

    def get_object(self):
        return self.newsindex.get_newsitem_model()(newsindex=self.newsindex)

from functools import lru_cache
from io import StringIO

from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.admin import messages
from wagtail.admin.panels import ObjectList, extract_panel_definitions_from_model_class
from wagtail.admin.views.generic import DeleteView
from wagtail.models import Page

from .. import signals
from ..forms import SaveActionSet
from ..models import NewsIndexMixin
from ..permissions import format_perms, perms_for_template
from wagtail.admin.views.generic import CreateView, EditView, UnpublishView

OPEN_PREVIEW_PARAM = "do_preview"


@lru_cache(maxsize=None)
def get_newsitem_edit_handler(NewsItem):
    if hasattr(NewsItem, "edit_handler"):
        return NewsItem.edit_handler.bind_to_model(NewsItem)

    panels = extract_panel_definitions_from_model_class(NewsItem, exclude=["newsindex"])
    return ObjectList(panels).bind_to_model(NewsItem)


class NewItemPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=self.kwargs["pk"]
        )
        if not self.request.user.has_perms(
            format_perms(self.newsindex.get_newsitem_model(), self.permissions_required)
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class NewsItemAdminMixin:
    def get_add_url(self):
        return reverse("wagtailnews:create", kwargs={"pk": self.kwargs["pk"]})

    def get_edit_url(self):
        return reverse(
            "wagtailnews:edit",
            kwargs={"pk": self.kwargs["pk"], "newsitem_pk": self.object.pk},
        )

    def get_success_url(self):
        return reverse("wagtailnews:index", kwargs={"pk": self.kwargs["pk"]})

    def get_form_class(self):
        NewsItem = self.newsindex.get_newsitem_model()
        edit_handler = get_newsitem_edit_handler(NewsItem)
        return edit_handler.get_form_class()

    def save_instance(self):
        newsitem = self.form.save(commit=False)
        action = SaveActionSet.from_post_data(self.request.POST)
        newsitem.live = action is SaveActionSet.publish
        newsitem.newsindex = self.newsindex
        newsitem.save()
        newsitem.save_revision(user=self.request.user)

        NewsItem = self.newsindex.get_newsitem_model()

        # TODO replace with DraftStateMixin, PreviewMixin
        if action is SaveActionSet.publish:
            signals.newsitem_published.send(
                sender=NewsItem, instance=newsitem, created=True
            )

        elif action is SaveActionSet.draft:
            signals.newsitem_draft_saved.send(
                sender=NewsItem, instance=newsitem, created=True
            )

        return newsitem

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "newsindex": self.newsindex,
                "newsitem_opts": self.newsindex.get_newsitem_model()._meta,
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
        return self.object


class UnpublishNewsItemView(NewItemPermissionMixin, UnpublishView):
    permissions_required = ["change"]

    def setup(self, request, *args, **kwargs):
        self.newsindex = get_object_or_404(
            Page.objects.specific().type(NewsIndexMixin), pk=kwargs["pk"]
        )
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
        return super().setup(request, *args, **kwargs)

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

    dummy_request = build_dummy_request(newsitem)
    template = newsitem.get_template(dummy_request)
    context = newsitem.get_context(
        dummy_request,
        year=newsitem.date.year,
        month=newsitem.date.month,
        day=newsitem.date.day,
        pk=newsitem.pk,
        slug=newsitem.get_slug(),
    )
    return render(dummy_request, template, context)


def build_dummy_request(newsitem):
    """
    Construct a HttpRequest object that is, as far as possible,
    representative of ones that would receive this page as a response. Used
    for previewing / moderation and any other place where we want to
    display a view of this page in the admin interface without going
    through the regular page routing logic.
    """
    url = newsitem.full_url
    if url:
        url_info = urlparse(url)
        hostname = url_info.hostname
        path = url_info.path
        port = url_info.port or 80
    else:
        # Cannot determine a URL to this page - cobble one together based on
        # whatever we find in ALLOWED_HOSTS
        try:
            hostname = settings.ALLOWED_HOSTS[0]
        except IndexError:
            hostname = "localhost"
        path = "/"
        port = 80

    request = WSGIRequest(
        {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": path,
            "SERVER_NAME": hostname,
            "SERVER_PORT": port,
            "HTTP_HOST": hostname,
            "wsgi.input": StringIO(),
        }
    )

    # Apply middleware to the request - see http://www.mellowmorning.com/2011/04/18/mock-django-request-for-testing/
    handler = BaseHandler()
    handler.load_middleware()
    # call each middleware in turn and throw away any responses that they might return
    if hasattr(handler, "_request_middleware"):
        for middleware_method in handler._request_middleware:
            middleware_method(request)
    else:
        handler.get_response(request)

    return request

from django.urls import re_path, include
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

urlpatterns = [
    re_path(r"^admin/", include(wagtailadmin_urls)),
    re_path(r"", include(wagtail_urls)),
]

from django.urls import include, re_path
from wagtail.admin import urls as wagtailadmin_urls

import wagtail
if wagtail.VERSION >= (4, 2):
  from wagtail import urls as wagtail_urls
else: # Support for wagtail <= 4.1
  from wagtail.core import urls as wagtail_urls

urlpatterns = [
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'', include(wagtail_urls)),
]

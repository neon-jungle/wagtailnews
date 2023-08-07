from django.conf.urls import include, url
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'', include(wagtail_urls)),
]

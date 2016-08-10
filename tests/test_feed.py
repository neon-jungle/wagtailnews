import datetime

from django.test import TestCase
from django.utils import timezone
from tests.app.models import NewsIndex, NewsItem
from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailcore.models import Site


class TestFeed(TestCase, WagtailTestUtils):

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)
        now = timezone.now()
        for items in range(5):
            self.newsitem = NewsItem.objects.create(
                newsindex=self.index,
                title='post number {}'.format(items),
                date=now - datetime.timedelta(days=items))
        self.future_newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='future post',
            date=now + datetime.timedelta(days=1)
        )
        self.unpublished_newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='unpublished post',
            date=now,
            live=False
        )

    def test_view(self):
        response = self.client.get(self.index.url + self.index.reverse_subpage('feed'))

        # Check first and last post exist and that future and unpublished posts do not.
        self.assertContains(response, 'post number 0')
        self.assertContains(response, 'post number 4')
        self.assertNotContains(response, self.future_newsitem.title)
        self.assertNotContains(response, self.unpublished_newsitem.title)


class TestCustomFeed(TestCase, WagtailTestUtils):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)
        now = timezone.now()
        self.newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='custompost 1',
            date=now)

    def test_custom_view(self):
        response = self.client.get(self.index.url + self.index.reverse_subpage('feed'))

        # check description exists
        self.assertContains(response, self.newsitem.get_description())

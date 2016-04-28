from django.test import TestCase
from django.utils import timezone

from tests.app.models import NewsIndex, NewsItem

from wagtail.wagtailcore.models import Site
from wagtail.tests.utils import WagtailTestUtils


class TestNewsItem(TestCase, WagtailTestUtils):

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)
        self.newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='A post',
            date=timezone.now())

    def test_view(self):
        response = self.client.get(self.newsitem.url())

        # Check the right NewsIndex was used, and is its most specific type
        self.assertIsInstance(response.context['self'], NewsIndex)
        self.assertEqual(response.context['self'], self.index)
        self.assertEqual(response.context['page'], self.index)

        # Check the right NewsItem was used
        self.assertEqual(response.context['newsitem'], self.newsitem)

        # Check the NewsIndex context is used as a base
        self.assertEqual(response.context['extra'], 'foo')

        # Check the context can be overridden using NewsItem.get_context()
        self.assertEqual(response.context['foo'], 'bar')

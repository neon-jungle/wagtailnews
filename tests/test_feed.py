import datetime

from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import NewsIndex, NewsItem


class TestFeed(TestCase, WagtailTestUtils):
    """
    Test that the RSS feed contains relevant results
    """

    def setUp(self):
        super(TestFeed, self).setUp()
        site = Site.objects.get(is_default_site=True)
        self.root_page = site.root_page
        self.index = self.root_page.add_child(instance=NewsIndex(
            title='News', slug='news'))

        now = timezone.now()
        for items in range(5):
            NewsItem.objects.create(
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

    def test_statuses(self):
        """
        Check that live posts are included, but future posts and draft posts
        are not included
        """
        response = self.client.get(self.index.url + self.index.reverse_subpage('feed'))

        # Check first and last post exist and that future and unpublished posts do not.
        self.assertContains(response, 'post number 0')
        self.assertContains(response, 'post number 4')
        self.assertNotContains(response, self.future_newsitem.title)
        self.assertNotContains(response, self.unpublished_newsitem.title)

    def test_multiple_newsindexes(self):
        """
        Check that the news items for the correct news index are used
        """
        second_index = self.root_page.add_child(instance=NewsIndex(
            title='News II', slug='news-2'))
        newsitem = NewsItem.objects.create(
            newsindex=second_index,
            title='Post on the second index',
            date=timezone.now())

        first_response = self.client.get(self.index.url + self.index.reverse_subpage('feed'))
        second_response = self.client.get(second_index.url + second_index.reverse_subpage('feed'))

        self.assertContains(first_response, 'post number 0')
        self.assertNotContains(first_response, newsitem.title)

        self.assertNotContains(second_response, 'post number 0')
        self.assertContains(second_response, newsitem.title)


class TestCustomFeed(TestCase, WagtailTestUtils):
    """
    Test custom Feed classes on the NewsIndex are used
    """
    def setUp(self):
        super(TestCustomFeed, self).setUp()
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

        # check descriptions
        self.assertContains(response, self.newsitem.get_description())

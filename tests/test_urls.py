import datetime

from django.test import TestCase
from django.utils import timezone

from tests.app.models import NewsIndex, NewsItem

from wagtail.wagtailcore.models import Page, Site
from wagtail.tests.utils import WagtailTestUtils


def dt(*args):
    return datetime.datetime(*args, tzinfo=timezone.get_current_timezone())


def noop(x):
    return x


class TestNewsList(TestCase, WagtailTestUtils):

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)

    def test_index(self):
        item1 = NewsItem.objects.create(
            newsindex=self.index,
            title='One post',
            date=dt(2015, 8, 24, 0, 0, 0))
        item2 = NewsItem.objects.create(
            newsindex=self.index,
            title='Two post',
            date=dt(2015, 8, 24, 0, 0, 0))

        response = self.client.get(self.index.url)
        self.assertIn('newsitem_list', response.context)
        self.assertQuerysetEqual(
            response.context['newsitem_list'],
            [item1, item2], transform=noop)

    def test_archive_year(self):
        NewsItem.objects.create(
            newsindex=self.index,
            title='2015',
            date=dt(2015, 8, 24, 0, 0, 0))
        item2014 = NewsItem.objects.create(
            newsindex=self.index,
            title='2014',
            date=dt(2014, 8, 24, 0, 0, 0))
        NewsItem.objects.create(
            newsindex=self.index,
            title='2013',
            date=dt(2013, 8, 24, 0, 0, 0))

        response = self.client.get(self.index.url + self.index.reverse_subpage(
            'year', kwargs={'year': '2014'}))

        self.assertIn('newsitem_list', response.context)
        self.assertQuerysetEqual(
            response.context['newsitem_list'],
            [item2014], transform=noop)

    def test_archive_month(self):
        NewsItem.objects.create(
            newsindex=self.index,
            title='2015-08-24',
            date=dt(2015, 8, 24, 0, 0, 0))
        item = NewsItem.objects.create(
            newsindex=self.index,
            title='2015-07-24',
            date=dt(2015, 7, 24, 0, 0, 0))
        NewsItem.objects.create(
            newsindex=self.index,
            title='2015-06-24',
            date=dt(2015, 6, 24, 0, 0, 0))
        NewsItem.objects.create(
            newsindex=self.index,
            title='2014-07-24',
            date=dt(2014, 7, 24, 0, 0, 0))

        response = self.client.get(self.index.url + self.index.reverse_subpage(
            'month', kwargs={'year': '2015', 'month': '7'}))

        self.assertIn('newsitem_list', response.context)
        self.assertQuerysetEqual(
            response.context['newsitem_list'],
            [item], transform=noop)

    def test_archive_day(self):
        NewsItem.objects.create(
            newsindex=self.index,
            title='2015-08-24',
            date=dt(2015, 8, 24, 12, 0, 0))
        item = NewsItem.objects.create(
            newsindex=self.index,
            title='2015-08-23',
            date=dt(2015, 8, 23, 12, 0, 0))
        NewsItem.objects.create(
            newsindex=self.index,
            title='2015-08-22',
            date=dt(2015, 8, 22, 12, 0, 0))
        NewsItem.objects.create(
            newsindex=self.index,
            title='2015-07-23',
            date=dt(2015, 7, 23, 12, 0, 0))

        response = self.client.get(self.index.url + self.index.reverse_subpage(
            'day', kwargs={'year': '2015', 'month': '8', 'day': '23'}))

        self.assertIn('newsitem_list', response.context)
        self.assertQuerysetEqual(
            response.context['newsitem_list'],
            [item], transform=noop)


class TestMultipleSites(TestCase, WagtailTestUtils):

    def setUp(self):
        root = Page.objects.get(pk=1)
        root_a = Page(
            title='Home A', slug='home-a')
        root.add_child(instance=root_a)

        root_b = Page(
            title='Home B', slug='home-b')
        root.add_child(instance=root_b)

        self.index_a = NewsIndex(title='News A', slug='news-a')
        root_a.add_child(instance=self.index_a)

        self.index_b = NewsIndex(title='News B', slug='news-b')
        root_b.add_child(instance=self.index_b)

        self.site_a = Site.objects.create(
            hostname='site-a.com',
            root_page=root_a)

        self.site_b = Site.objects.create(
            hostname='site-b.org',
            root_page=root_b)

        self.item_a = NewsItem.objects.create(
            newsindex=self.index_a, title='Post A', date=dt(2015, 8, 1))
        self.item_b = NewsItem.objects.create(
            newsindex=self.index_b, title='Post B', date=dt(2015, 8, 2))

    def test_index(self):
        response = self.client.get(self.index_a.url,
                                   HTTP_HOST=self.site_a.hostname)
        self.assertIn('newsitem_list', response.context)
        self.assertQuerysetEqual(
            response.context['newsitem_list'],
            [self.item_a], transform=noop)

        response = self.client.get(self.index_b.url,
                                   HTTP_HOST=self.site_b.hostname)
        self.assertIn('newsitem_list', response.context)
        self.assertQuerysetEqual(
            response.context['newsitem_list'],
            [self.item_b], transform=noop)

    def test_item_url(self):
        self.assertEqual(
            self.item_a.url(), 'http://{}/{}/2015/8/1/{}-{}/'.format(
                self.site_a.hostname, self.index_a.slug,
                self.item_a.pk, self.item_a.get_nice_url()))
        self.assertEqual(
            self.item_b.url(), 'http://{}/{}/2015/8/2/{}-{}/'.format(
                self.site_b.hostname, self.index_b.slug,
                self.item_b.pk, self.item_b.get_nice_url()))

    def test_item(self):
        response = self.client.get(self.item_a.url(),
                                   HTTP_HOST=self.site_a.hostname)
        self.assertEqual(response.status_code, 200)
        self.assertIn('newsitem', response.context)
        self.assertEqual(response.context['newsitem'], self.item_a)

        response = self.client.get(self.item_b.url(),
                                   HTTP_HOST=self.site_b.hostname)
        self.assertEqual(response.status_code, 200)
        self.assertIn('newsitem', response.context)
        self.assertEqual(response.context['newsitem'], self.item_b)

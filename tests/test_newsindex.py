import datetime

from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import (
    NewsIndex, NewsItem, SecondaryNewsIndex, SecondaryNewsItem)


class TestNewsIndex(TestCase, WagtailTestUtils):
    def setUp(self):
        super(TestNewsIndex, self).setUp()
        self.root = Page.objects.get(pk=2)
        self.rf = RequestFactory()

    def test_get_template(self):
        index = self.root.add_child(instance=NewsIndex(title='News index'))
        self.assertEqual(
            index.get_template(self.rf.get('/news/'), view='month'),
            ['app/news_index_month.html', 'app/news_index.html'])

    def test_get_template_custom(self):
        index = self.root.add_child(instance=SecondaryNewsIndex(title='News index'))
        self.assertEqual(
            index.get_template(self.rf.get('/news/'), view='all'),
            ['app/secondaryindex_all.jade', 'app/secondaryindex.jade'])

    def test_get_newsitems(self):
        news = self.root.add_child(instance=NewsIndex(title='Index 1'))
        other_news = self.root.add_child(instance=NewsIndex(title='Index 2'))

        live = NewsItem.objects.create(newsindex=news, title='First')
        draft = NewsItem.objects.create(newsindex=news, title='Draft', live=False)
        future = NewsItem.objects.create(newsindex=news, title='Future', date=timezone.now() + datetime.timedelta(hours=1))
        other = NewsItem.objects.create(newsindex=other_news, title='Other')

        self.assertEqual(list(news.get_newsitems()),
                         [future, draft, live])
        self.assertEqual(list(news.get_newsitems_for_display()),
                         [live])
        self.assertEqual(list(other_news.get_newsitems()),
                         [other])


class TestGetNewsItem(TestCase, WagtailTestUtils):

    @classmethod
    def setUpClass(cls):
        super(TestGetNewsItem, cls).setUpClass()
        cls._old_newsitem = NewsIndex.newsitem_model

    @classmethod
    def tearDownClass(cls):
        super(TestGetNewsItem, cls).tearDownClass()
        NewsIndex.newsitem_model = cls._old_newsitem

    def test_newsitem_just_model(self):
        NewsIndex.newsitem_model = 'NewsItem'
        self.assertIs(NewsIndex.get_newsitem_model(), NewsItem)

    def test_newsitem_app_model(self):
        NewsIndex.newsitem_model = 'app.SecondaryNewsItem'
        self.assertIs(NewsIndex.get_newsitem_model(), SecondaryNewsItem)

    def test_newsitem_model_class(self):
        NewsIndex.newsitem_model = NewsItem
        self.assertIs(NewsIndex.get_newsitem_model(), NewsItem)

    def test_bad_newsitem_string(self):
        NewsIndex.newsitem_model = 'NoSuchModel'
        with self.assertRaises(LookupError):
            NewsIndex.get_newsitem_model()

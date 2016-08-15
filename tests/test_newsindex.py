from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils

from tests.app.models import NewsIndex, NewsItem, SecondaryNewsItem


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

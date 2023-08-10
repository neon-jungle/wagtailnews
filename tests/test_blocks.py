from django.test import TestCase

from tests.app.models import NewsItem
from wagtailnews.blocks import NewsChooserBlock


class TestNewsChooserBlock(TestCase):
    def test_target_model_string(self):
        block = NewsChooserBlock(target_model="app.NewsItem")
        self.assertIs(block.target_model, NewsItem)

    def test_target_model_literal(self):
        block = NewsChooserBlock(target_model=NewsItem)
        self.assertIs(block.target_model, NewsItem)

    def test_deconstruct(self):
        block = NewsChooserBlock(target_model=NewsItem)
        path, args, kwargs = block.deconstruct()
        self.assertEqual(path, "wagtailnews.blocks.NewsChooserBlock")
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {"target_model": "app.newsitem"})

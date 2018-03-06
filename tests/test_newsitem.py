# -*- coding: utf8 -*-
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.utils import timezone
from django.utils.http import urlquote
from wagtail.core.models import Site
from wagtail.tests.utils import WagtailTestUtils

from tests.app.models import NewsIndex, NewsItem


class TestNewsItem(TestCase, WagtailTestUtils):

    def setUp(self):
        super(TestNewsItem, self).setUp()
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)
        self.newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='A post',
            date=timezone.localtime(timezone.now()).replace(2017, 4, 13))

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

    def test_bad_url_redirect(self):
        response = self.client.get(
            '/news/1234/2/3/{}-bad-title/'.format(self.newsitem.pk),
            follow=True)

        self.assertEqual(
            self.newsitem.url(),
            urlquote('/news/2017/4/13/{}-a-post/'.format(self.newsitem.pk)))
        self.assertEqual(
            response.redirect_chain,
            [(self.newsitem.url(), 301)])

    def test_bad_url_redirect_unicode(self):
        self.newsitem.title = '你好，世界！'
        self.newsitem.save()

        response = self.client.get(
            '/news/1234/2/3/{}-bad-title/'.format(self.newsitem.pk),
            follow=True)

        self.assertEqual(
            self.newsitem.url(),
            urlquote('/news/2017/4/13/{}-你好世界/'.format(self.newsitem.pk)))
        self.assertEqual(
            response.redirect_chain,
            [(self.newsitem.url(), 301)])

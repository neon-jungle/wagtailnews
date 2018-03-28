from django.test import TestCase
from django.urls import reverse
from taggit.models import Tag
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailTestUtils

from tests.app.models import NewsIndex, NewsItem


class TestNewsItemWithTags(TestCase, WagtailTestUtils):

    def setUp(self):
        super(TestNewsItemWithTags, self).setUp()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)

    def test_create_item_with_tags(self):
        item = NewsItem.objects.create(
            newsindex=self.index,
            title='News post!')
        item.tags = ['hello', 'world']

        # Get a fresh one from the DB
        item = NewsItem.objects.get()
        self.assertQuerysetEqual(item.tags.order_by('name'),
                                 Tag.objects.order_by('name'))

    def test_create_item_admin(self):
        create_url = reverse('wagtailnews:create', kwargs={'pk': self.index.pk})
        self.login()
        tags = ['hello', 'world']

        self.client.post(create_url, {
            'title': 'Test post',
            'tags': ', '.join(tags),
            'date': '2015-08-20 00:48',
            'initial-date': '2015-08-20 00:48:31.123456'})

        item = NewsItem.objects.get()
        self.assertQuerysetEqual(
            item.tags.order_by('name'),
            tags, transform=lambda t: t.name)

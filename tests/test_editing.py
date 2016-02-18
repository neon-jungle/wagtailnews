from django.core.urlresolvers import reverse
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailcore.models import Page

from tests.app.models import NewsIndex, NewsItem


class TestCreateNewsItem(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)

    def test_create_newsitem(self):
        self.assertEqual(NewsItem.objects.count(), 0)

        # Make a news item
        self.client.post(
            reverse('wagtailnews_create', kwargs={'pk': self.index.pk}), {
                'title': 'test title',
                'tags': '',
                'date': '2015-11-03 17:12',
                'action-publish': 'publish',
            })

        # Check that a NewsItem was created
        self.assertEqual(NewsItem.objects.count(), 1)
        newsitem = NewsItem.objects.get()

        # Make sure it got all the bits we were expecting
        self.assertEqual(newsitem.title, 'test title')
        self.assertTrue(newsitem.live)

        # Make sure the revision behaves itself
        newsitem_revision = newsitem.get_latest_revision_as_newsitem()
        self.assertEqual(newsitem.to_json(),
                         newsitem_revision.to_json())

    def test_create_newsitem_draft(self):
        self.assertEqual(NewsItem.objects.count(), 0)

        # Make a news item
        self.client.post(
            reverse('wagtailnews_create', kwargs={'pk': self.index.pk}), {
                'title': 'test title',
                'tags': '',
                'date': '2015-11-03 17:12',
                'action-draft': 'draft',
            })

        # Check that a NewsItem was created
        self.assertEqual(NewsItem.objects.count(), 1)
        newsitem = NewsItem.objects.get()

        # Make sure it got all the bits we were expecting
        self.assertEqual(newsitem.title, 'test title')
        self.assertFalse(newsitem.live)
        self.assertEqual(NewsItem.objects.live().count(), 0)

        # Make sure the revision behaves itself
        newsitem_revision = newsitem.get_latest_revision_as_newsitem()
        self.assertEqual(newsitem.to_json(),
                         newsitem_revision.to_json())


class TestEditNewsItem(TestCase, WagtailTestUtils):

    def setUp(self):
        self.login()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)
        self.newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='test title')

    def test_publish_changes(self):
        # Make a news item
        response = self.client.post(
            reverse('wagtailnews_edit', kwargs={
                'pk': self.index.pk,
                'newsitem_pk': self.newsitem.pk}),
            {
                'title': 'updated title',
                'tags': '',
                'date': '2015-11-03 17:12',
                'action-publish': 'publish'})
        self.assertRedirects(response, reverse('wagtailnews_index', kwargs={
            'pk': self.index.pk}))

        # Check that no new NewsItem was created
        self.assertEqual(NewsItem.objects.count(), 1)
        newsitem = NewsItem.objects.get()

        # Make sure it got all the bits we were expecting
        self.assertEqual(newsitem.title, 'updated title')
        self.assertTrue(newsitem.live)

        # Make sure the revision behaves itself
        newsitem_revision = newsitem.get_latest_revision_as_newsitem()
        self.assertEqual(newsitem.to_json(),
                         newsitem_revision.to_json())

    def test_save_draft_changes(self):
        # Make a news item
        self.client.post(
            reverse('wagtailnews_edit', kwargs={
                'pk': self.index.pk,
                'newsitem_pk': self.newsitem.pk}),
            {
                'title': 'draft title',
                'tags': 'test',
                'date': '2015-11-03 17:12',
                'action-draft': 'draft'})

        # Check that no new NewsItem was created
        self.assertEqual(NewsItem.objects.count(), 1)

        newsitem = NewsItem.objects.get()

        # Make sure the NewsItem didn't change
        self.assertEqual(newsitem.title, 'test title')
        self.assertTrue(newsitem.live)

        # Make sure the revision behaves itself
        self.assertEqual(newsitem.revisions.count(), 1)
        revision = newsitem.get_latest_revision()
        newsitem_revision = revision.as_newsitem()
        self.assertEqual(newsitem_revision.title, 'draft title')

        revision.publish()
        newsitem = NewsItem.objects.get()
        self.assertEqual(newsitem.title, 'draft title')
        self.assertTrue(newsitem.live)


class TestPreviewDraft(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)

    def test_preview_live_item(self):
        " Preview a live item with no draft "
        newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='Preview me')
        response = self.client.get(reverse('wagtailnews_view_draft', kwargs={
            'pk': self.index.pk, 'newsitem_pk': newsitem.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preview me')
        self.assertTemplateUsed(response, 'app/newsitem.html')

    def test_preview_draft_item(self):
        " Preview a draft of an article"
        newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='Live title')

        draft_newsitem = NewsItem.objects.get(pk=newsitem.pk)
        draft_newsitem.title = 'Draft title'
        draft_newsitem.save_revision(user=self.user)

        response = self.client.get(reverse('wagtailnews_view_draft', kwargs={
            'pk': self.index.pk, 'newsitem_pk': draft_newsitem.pk}))
        self.assertContains(response, 'Draft title')

        live_newsitem = NewsItem.objects.get(pk=newsitem.pk)
        response = self.client.get(live_newsitem.url())
        self.assertContains(response, 'Live title')

    def test_save_and_preview(self):
        " Preview straight from the editor "
        newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='Live title')

        response = self.client.post(
            reverse('wagtailnews_edit', kwargs={
                'pk': self.index.pk, 'newsitem_pk': newsitem.pk}),
            follow=True, data={
                'title': 'Draft title', 'date': '2015-11-03 17:12',
                'action-preview': 'preview'})

        preview_url = reverse('wagtailnews_view_draft', kwargs={
            'pk': self.index.pk, 'newsitem_pk': newsitem.pk})
        # redirect_chain changed in Django 1.9, which makes testing it annoying
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(response.redirect_chain[0][0].endswith(preview_url))
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, 'Draft title')

        live_newsitem = NewsItem.objects.get(pk=newsitem.pk)
        response = self.client.get(live_newsitem.url())
        self.assertContains(response, 'Live title')

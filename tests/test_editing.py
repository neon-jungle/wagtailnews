from unittest.mock import MagicMock

from django.test import TestCase
from django.urls import reverse
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailTestUtils

from tests.app.models import NewsIndex, NewsItem, SecondaryNewsIndex
from wagtailnews import signals
from wagtailnews.views.editor import OPEN_PREVIEW_PARAM


class TestCreateNewsItem(TestCase, WagtailTestUtils):

    def setUp(self):
        super().setUp()
        self.login()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)

    def test_create_newsitem(self):
        self.assertEqual(NewsItem.objects.count(), 0)

        uncalled_handler = MagicMock()
        handler = MagicMock()

        signals.newsitem_published.connect(uncalled_handler, sender=object())
        signals.newsitem_published.connect(handler, sender=NewsItem)

        uncalled_handler.assert_not_called()
        handler.assert_not_called()

        # Make a news item
        response = self.client.post(
            reverse('wagtailnews:create', kwargs={'pk': self.index.pk}), {
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

        # Make sure the user is redirected to the index
        self.assertRedirects(response, reverse('wagtailnews:index', kwargs={
            'pk': self.index.pk}))

        # Make sure siginals were called as expected
        uncalled_handler.not_called()
        handler.assert_called_once_with(
            sender=NewsItem, signal=signals.newsitem_published,
            instance=newsitem, created=True)

    def test_create_newsitem_draft(self):
        self.assertEqual(NewsItem.objects.count(), 0)

        uncalled_handler = MagicMock()
        handler = MagicMock()
        signals.newsitem_published.connect(uncalled_handler, sender=NewsItem)
        signals.newsitem_draft_saved.connect(handler, sender=NewsItem)
        uncalled_handler.assert_not_called()
        handler.assert_not_called()

        # Make a news item
        response = self.client.post(
            reverse('wagtailnews:create', kwargs={'pk': self.index.pk}), {
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

        # Make sure the user is redirected to the edit page
        self.assertRedirects(response, reverse('wagtailnews:edit', kwargs={
            'pk': self.index.pk, 'newsitem_pk': newsitem.pk}))

        # Make sure siginals were called as expected
        uncalled_handler.not_called()
        handler.assert_called_once_with(
            sender=NewsItem, signal=signals.newsitem_draft_saved,
            instance=newsitem, created=True)


class TestEditNewsItem(TestCase, WagtailTestUtils):

    def setUp(self):
        super().setUp()
        self.login()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(
            title='News', slug='news')
        root_page.add_child(instance=self.index)
        self.newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='test title')

    def test_publish_changes(self):
        handler = MagicMock()
        signals.newsitem_published.connect(handler, sender=NewsItem)
        handler.assert_not_called()

        # Make a news item
        response = self.client.post(
            reverse('wagtailnews:edit', kwargs={
                'pk': self.index.pk,
                'newsitem_pk': self.newsitem.pk}),
            {
                'title': 'updated title',
                'tags': '',
                'date': '2015-11-03 17:12',
                'action-publish': 'publish'})
        self.assertRedirects(response, reverse('wagtailnews:index', kwargs={
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

        # Make sure signal was called as expected
        handler.assert_called_once_with(
            sender=NewsItem, signal=signals.newsitem_published,
            instance=newsitem, created=False)

    def test_save_draft_changes(self):
        handler = MagicMock()
        signals.newsitem_draft_saved.connect(handler, sender=NewsItem)
        handler.assert_not_called()

        # Make a news item
        self.client.post(
            reverse('wagtailnews:edit', kwargs={
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

        # Make sure signal was called as expected
        handler.assert_called_once_with(
            sender=NewsItem, signal=signals.newsitem_draft_saved,
            instance=newsitem, created=False)

    def test_delete(self):
        handler = MagicMock()
        signals.newsitem_deleted.connect(handler, sender=NewsItem)
        handler.assert_not_called()

        # delete the news item
        response = self.client.post(
            reverse('wagtailnews:delete', kwargs={
                'pk': self.index.pk,
                'newsitem_pk': self.newsitem.pk}), {})
        self.assertRedirects(response, reverse('wagtailnews:index', kwargs={
            'pk': self.index.pk}))

        # Check that the newsitem was deleted
        self.assertEqual(NewsItem.objects.count(), 0)

        # Make sure signal was called as expected.  Need to pull out the
        # deleted instance, because it will not compare equal to an instance
        # that isn't aware of its deletion
        instance = handler.call_args[1]['instance']
        handler.assert_called_once_with(
            sender=NewsItem, signal=signals.newsitem_deleted,
            instance=instance)

    def test_actions_present(self):
        """ Ensure that all the required actions are present """
        response = self.client.get(
            reverse('wagtailnews:edit', kwargs={
                'pk': self.index.pk,
                'newsitem_pk': self.newsitem.pk}))

        url_kwargs = {'pk': self.index.pk, 'newsitem_pk': self.newsitem.pk}
        self.assertContains(response, reverse('wagtailnews:delete', kwargs=url_kwargs))
        self.assertContains(response, reverse('wagtailnews:unpublish', kwargs=url_kwargs))


class TestPreviewDraft(TestCase, WagtailTestUtils):
    def setUp(self):
        super().setUp()
        self.user = self.login()
        root_page = Page.objects.get(pk=2)
        self.index = root_page.add_child(instance=NewsIndex(
            title='News', slug='news'))
        self.second_index = root_page.add_child(instance=SecondaryNewsIndex(
            title='Secondary news', slug='news-the-second'))

    def test_preview_live_item(self):
        " Preview a live item with no draft "
        newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='Preview me')
        response = self.client.get(reverse('wagtailnews:view_draft', kwargs={
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

        response = self.client.get(reverse('wagtailnews:view_draft', kwargs={
            'pk': self.index.pk, 'newsitem_pk': draft_newsitem.pk}))
        self.assertContains(response, 'Draft title')

        live_newsitem = NewsItem.objects.get(pk=newsitem.pk)
        response = self.client.get(live_newsitem.url())
        self.assertContains(response, 'Live title')

    def test_create_and_preview(self):
        " Preview straight from creating a news item"
        self.assertEqual(NewsItem.objects.count(), 0)

        # Make a news item
        response = self.client.post(
            reverse('wagtailnews:create', kwargs={'pk': self.index.pk}),
            follow=True, data={
                'title': 'test title',
                'tags': '',
                'date': '2015-11-03 17:12',
                'action-preview': 'preview',
            })

        newsitem = NewsItem.objects.get(title='test title')
        edit_url = reverse('wagtailnews:edit', kwargs={
            'pk': self.index.pk, 'newsitem_pk': newsitem.pk})
        self.assertRedirects(response, '{}?{}=1'.format(edit_url, OPEN_PREVIEW_PARAM))

        preview_url = reverse('wagtailnews:view_draft', kwargs={
            'pk': self.index.pk, 'newsitem_pk': newsitem.pk})
        self.assertContains(response, 'url = "{}"'.format(preview_url))
        self.assertContains(response, 'window.open(url,')

    def test_save_and_preview(self):
        " Preview straight from the editor "
        newsitem = NewsItem.objects.create(
            newsindex=self.index,
            title='Live title')

        response = self.client.post(
            reverse('wagtailnews:edit', kwargs={
                'pk': self.index.pk, 'newsitem_pk': newsitem.pk}),
            data={
                'title': 'Draft title', 'date': '2015-11-03 17:12',
                'action-preview': 'preview'})

        preview_url = reverse('wagtailnews:view_draft', kwargs={
            'pk': self.index.pk, 'newsitem_pk': newsitem.pk})
        self.assertContains(response, 'url = "{}"'.format(preview_url))
        self.assertContains(response, 'window.open(url,')

        response = self.client.get(preview_url)
        self.assertContains(response, 'Draft title')

        live_newsitem = NewsItem.objects.get(pk=newsitem.pk)
        response = self.client.get(live_newsitem.url())
        self.assertContains(response, 'Live title')

    def test_edit_handlers(self):
        """Test custom edit handlers using NewsItem.edit_handler."""
        response = self.client.get(
            reverse('wagtailnews:create', kwargs={'pk': self.second_index.pk}))
        self.assertContains(response, 'tab-content')
        self.assertContains(response, 'Tab the first')
        self.assertContains(response, 'Tab the second')

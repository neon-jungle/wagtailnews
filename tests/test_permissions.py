from functools import wraps

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from wagtail.models import GroupPagePermission, Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import NewsIndex, NewsItem, SecondaryNewsIndex


def p(permission_string):
    app_label, codename = permission_string.split(".", 1)
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)


def grant_permissions(perms):
    def decorator(fn):
        @wraps(fn)
        def method(self):
            self.user.user_permissions.add(*[p(perm) for perm in perms])
            self.user.save()
            return fn(self)

        return method

    return decorator


class WithNewsIndexTestCase(TestCase):
    def setUp(self):
        super(WithNewsIndexTestCase, self).setUp()
        root_page = Page.objects.get(pk=2)
        self.index = NewsIndex(title="News", slug="news")
        root_page.add_child(instance=self.index)


class WithNewsItemTestCase(WithNewsIndexTestCase):
    def setUp(self):
        super(WithNewsItemTestCase, self).setUp()
        self.newsitem = NewsItem.objects.create(newsindex=self.index, title="News item")


class PermissionTestCase(TestCase, WagtailTestUtils):
    def setUp(self):
        super(PermissionTestCase, self).setUp()

        # Create a group with permission to edit pages
        # Required to enable page searching
        self.group = Group.objects.create(name="Test group")
        GroupPagePermission.objects.create(
            group=self.group, page=Page.objects.get(pk=1), permission_type="add"
        )

        self.user = self.create_test_user()
        self.client.login(username="test@email.com", password="password")

    def create_test_user(self):
        """
        Create a normal boring user, not a super user. This user has no news
        related permissions by default.
        """
        user = User.objects.create_user(username="test@email.com", password="password")
        user.groups.add(self.group)
        user.user_permissions.add(p("wagtailadmin.access_admin"))
        user.save()
        return user

    def assertStatusCode(self, url, status_code, msg=None):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_code, msg=msg)


class TestChooseNewsIndex(PermissionTestCase):
    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_chooser_multiple_choices(self):
        """
        Test the chooser when there are multiple valid choices, and some
        missing due to lack of permissions.
        """
        root_page = Page.objects.get(pk=2)
        news1 = root_page.add_child(
            instance=NewsIndex(title="Normal News 1", slug="news-1")
        )
        news2 = root_page.add_child(
            instance=NewsIndex(title="Normal News 2", slug="news-2")
        )
        secondary_news = root_page.add_child(
            instance=SecondaryNewsIndex(title="Secondary News", slug="secondary-news")
        )

        response = self.client.get(reverse("wagtailnews:choose"))
        self.assertContains(response, news1.title)
        self.assertContains(response, news2.title)
        self.assertNotContains(response, secondary_news.title)

    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_chooser_one_choice(self):
        """
        Test the chooser when there is a single valid choice, and some
        missing due to lack of permissions.
        """
        root_page = Page.objects.get(pk=2)
        news = root_page.add_child(instance=NewsIndex(title="News", slug="news"))
        root_page.add_child(
            instance=SecondaryNewsIndex(title="Secondary News", slug="secondary-news")
        )

        response = self.client.get(reverse("wagtailnews:choose"))
        self.assertRedirects(
            response, reverse("wagtailnews:index", kwargs={"pk": news.pk})
        )

    def test_chooser_no_perms(self):
        """
        Test the chooser when there are no valid choices.
        """
        root_page = Page.objects.get(pk=2)
        root_page.add_child(instance=NewsIndex(title="News", slug="news"))
        root_page.add_child(
            instance=SecondaryNewsIndex(title="Secondary News", slug="secondary-news")
        )

        response = self.client.get(reverse("wagtailnews:choose"))
        self.assertEqual(response.status_code, 302)

    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_chooser_has_perms_no_news(self):
        """
        Test the chooser when there are no news items, but the user has
        relevant permissions.
        """
        response = self.client.get(reverse("wagtailnews:choose"))
        self.assertEqual(response.status_code, 200)


class TestNewsIndex(WithNewsIndexTestCase, PermissionTestCase):
    def setUp(self):
        super(TestNewsIndex, self).setUp()
        self.url = reverse("wagtailnews:index", kwargs={"pk": self.index.pk})

    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_news_index_has_perm(self):
        """
        Check the user is allowed to access the news index list
        """
        self.assertStatusCode(self.url, 200)

    def test_news_index_no_perm(self):
        """
        Check the user is denied access to the news index list
        """
        self.assertStatusCode(self.url, 302)


class TestCreateNewsItem(WithNewsIndexTestCase, PermissionTestCase):
    def setUp(self):
        super(TestCreateNewsItem, self).setUp()
        self.url = reverse("wagtailnews:create", kwargs={"pk": self.index.pk})

    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_has_permission(self):
        """Test users can create NewsItems"""
        self.assertStatusCode(self.url, 200)

    @grant_permissions(["app.add_newsitem"])
    def test_only_add_perm(self):
        """Users need both add and edit. Add is not sufficient"""
        self.assertStatusCode(self.url, 302)

    @grant_permissions(["app.change_newsitem"])
    def test_only_edit_perm(self):
        """Users need both add and edit. Edit is not sufficient"""
        self.assertStatusCode(self.url, 302)

    def test_no_permission(self):
        """Test user can not create without permission"""
        self.assertStatusCode(self.url, 302)

    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_add_button_appears(self):
        """Test that the add button appears"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertContains(response, self.url)

    @grant_permissions(["app.change_newsitem"])
    def test_no_add_button_appears(self):
        """Test that the add button does not appear"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertNotContains(response, self.url)


class TestEditNewsItem(WithNewsItemTestCase, PermissionTestCase):
    def setUp(self):
        super(TestEditNewsItem, self).setUp()
        self.url = reverse(
            "wagtailnews:edit",
            kwargs={"pk": self.index.pk, "newsitem_pk": self.newsitem.pk},
        )

    @grant_permissions(["app.change_newsitem"])
    def test_has_permission(self):
        """Test users can create NewsItems"""
        self.assertStatusCode(self.url, 200)

    def test_no_permission(self):
        """Test user can not edit without permission"""
        self.assertStatusCode(self.url, 302)

    @grant_permissions(["app.change_newsitem"])
    def test_edit_button_appears(self):
        """Test that the edit button appears"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertContains(response, self.url)

    @grant_permissions(["app.delete_newsitem"])
    def test_no_edit_button_appears(self):
        """Test that the edit button does not appear"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertNotContains(response, self.url)


class TestUnpublishNewsItem(WithNewsItemTestCase, PermissionTestCase):
    def setUp(self):
        super(TestUnpublishNewsItem, self).setUp()
        self.url = reverse(
            "wagtailnews:unpublish",
            kwargs={"pk": self.index.pk, "newsitem_pk": self.newsitem.pk},
        )

    @grant_permissions(["app.change_newsitem"])
    def test_has_permission(self):
        """Test users can unpublish NewsItems"""
        self.assertStatusCode(self.url, 200)

    def test_no_permission(self):
        """Test user can not unpublish without permission"""
        self.assertStatusCode(self.url, 302)

    @grant_permissions(["app.change_newsitem"])
    def test_unpublish_button_appears(self):
        """Test that the unpublish button appears"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertContains(response, self.url)

    @grant_permissions(["app.delete_newsitem"])
    def test_no_unpublish_button_appears(self):
        """Test that the unpublish button does not appear"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertNotContains(response, self.url)


class TestDeleteNewsItem(WithNewsItemTestCase, PermissionTestCase):
    def setUp(self):
        super(TestDeleteNewsItem, self).setUp()
        self.url = reverse(
            "wagtailnews:delete",
            kwargs={"pk": self.index.pk, "newsitem_pk": self.newsitem.pk},
        )

    @grant_permissions(["app.delete_newsitem"])
    def test_has_permission(self):
        """Test users can delete NewsItems"""
        self.assertStatusCode(self.url, 200)

    def test_no_permission(self):
        """Test user can not delete without permission"""
        self.assertStatusCode(self.url, 302)

    @grant_permissions(["app.delete_newsitem"])
    def test_delete_button_appears_index(self):
        """Test that the delete button appears on the index page"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertContains(response, self.url)

    @grant_permissions(["app.change_newsitem"])
    def test_no_delete_button_appears_index(self):
        """Test that the delete button does not appear on the index page"""
        response = self.client.get(
            reverse("wagtailnews:index", kwargs={"pk": self.index.pk})
        )
        self.assertNotContains(response, self.url)

    @grant_permissions(["app.change_newsitem", "app.delete_newsitem"])
    def test_delete_button_appears_edit(self):
        """Test that the delete button appears on the edit page"""
        response = self.client.get(
            reverse(
                "wagtailnews:edit",
                kwargs={"pk": self.index.pk, "newsitem_pk": self.newsitem.pk},
            )
        )
        self.assertContains(response, self.url)

    @grant_permissions(["app.change_newsitem"])
    def test_no_delete_button_appears_edit(self):
        """Test that the delete button does not appear on the edit page"""
        response = self.client.get(
            reverse(
                "wagtailnews:edit",
                kwargs={"pk": self.index.pk, "newsitem_pk": self.newsitem.pk},
            )
        )
        self.assertNotContains(response, self.url)


class TestSearchNewsItem(WithNewsItemTestCase, PermissionTestCase):
    def setUp(self):
        super(TestSearchNewsItem, self).setUp()
        self.url = reverse("wagtailnews:search")
        self.search_url = reverse("wagtailadmin_pages:search") + "?q=hello"

    @grant_permissions(["app.change_newsitem"])
    def test_has_permission(self):
        self.assertStatusCode(self.url, 200)

    def test_no_permission(self):
        self.assertStatusCode(self.url, 302)

    @grant_permissions(["app.add_newsitem", "app.change_newsitem"])
    def test_search_area_appears_permission(self):
        response = self.client.get(self.search_url)
        self.assertContains(response, self.url)

    def test_search_area_hidden_no_permission(self):
        response = self.client.get(self.search_url)
        self.assertNotContains(response, "News")
        self.assertNotContains(response, self.url)

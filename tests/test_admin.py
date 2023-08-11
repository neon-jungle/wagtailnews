from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils

from tests.app.models import NewsIndex, SecondaryNewsIndex


class TestNewsIndexChooser(TestCase, WagtailTestUtils):
    def setUp(self):
        super(TestNewsIndexChooser, self).setUp()
        self.login()
        root_page = Page.objects.get(pk=2)

        self.index1 = root_page.add_child(instance=NewsIndex(
            title='Standard index'))
        self.index2 = root_page.add_child(instance=SecondaryNewsIndex(
            title='Secondary index'))

    def test_admin_title(self):
        response = self.client.get(reverse('wagtailnews:choose'))
        self.assertContains(response, self.index1.get_admin_display_title())
        self.assertContains(response, self.index2.get_admin_display_title())

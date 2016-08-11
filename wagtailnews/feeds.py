from django.contrib.syndication.views import Feed
from django.utils import timezone


class LatestEntriesFeed(Feed):

    def items(self):
        now = timezone.now()
        NewsItem = self.news_index.get_newsitem_model()
        newsitem_list = NewsItem.objects.live().order_by('-date').filter(
            newsindex=self.news_index, date__lte=now)[:20]
        return newsitem_list

    def item_link(self, item):
        return item.full_url()

    def item_guid(self, item):
        return item.full_url()

    item_guid_is_permalink = True

    def item_pubdate(self, item):
        return item.date

    def __init__(self, news_index):
        super(LatestEntriesFeed, self).__init__()
        self.news_index = news_index

        self.title = news_index.title
        self.description = news_index.title

        self.link = news_index.full_url
        self.feed_url = self.link + news_index.reverse_subpage('feed')

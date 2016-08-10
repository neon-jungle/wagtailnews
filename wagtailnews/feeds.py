from django.contrib.syndication.views import Feed
from django.utils import timezone


class LatestEnteriesFeed(Feed):
    description = "Latest news"

    def items(self):
        now = timezone.now()
        NewsItem = self.news_index.get_newsitem_model()
        newsitem_list = NewsItem.objects.live().order_by('-date').filter(
            newsindex=self.news_index, date__lte=now)[:20]
        return newsitem_list

    def item_link(self, item):
        return item.url()

    def __init__(self, news_index):
        super(LatestEnteriesFeed, self).__init__()
        self.news_index = news_index
        self.title = news_index.title
        self.link = news_index.url

    def item_pubdate(self, item):
        return item.date

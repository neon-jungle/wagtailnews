from wagtailnews.feeds import LatestEnteriesFeed


class LatestEnteriesTestFeed(LatestEnteriesFeed):
    def item_description(self, item):
        return item.get_description()

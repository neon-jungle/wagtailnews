from wagtailnews.feeds import LatestEntriesFeed


class LatestEntriesTestFeed(LatestEntriesFeed):
    def item_description(self, item):
        return item.get_description()

import abc


class Plugin(abc.ABC):

    @abc.abstractmethod
    def get_feed(self, feed_id, base_url):
        """Calculates and returns the subscribable feed."""

    @abc.abstractmethod
    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""

    @abc.abstractmethod
    def extract_link(self, url):
        """Calculates the downloadable url from the html url of an item."""

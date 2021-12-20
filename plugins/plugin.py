import abc


class Plugin(abc.ABC):

    @abc.abstractmethod
    def get_feed(self, feed_id, base_url, options: dict[str, str]):
        """Calculates and returns the subscribable feed."""

    @abc.abstractmethod
    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""

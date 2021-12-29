import abc

from core.model import PodcastFeed


class Plugin(abc.ABC):

    def __init__(self, options: dict[str, str]):
        self.options = options

    @abc.abstractmethod
    def get_feed(self, feed_id: str) -> PodcastFeed:
        """Calculates and returns the subscribable feed."""

    @abc.abstractmethod
    def get_item_url(self, item_id: str) -> str:
        """Calculates the downloadable url of an item in the feed."""

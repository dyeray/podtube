import abc

from core.model import PodcastFeed
from core.options import Options, GlobalOptions


class Service(abc.ABC):

    GlobalOptions = GlobalOptions
    ServiceOptions = Options  # Redefine the ServiceOptions class on a service to set the specific service options.

    def __init__(self, options: dict[str, str]):
        self.options = self.ServiceOptions(**options)

    @abc.abstractmethod
    def get_feed(self, feed_id: str) -> PodcastFeed:
        """Calculates and returns the subscribable feed."""

    @abc.abstractmethod
    def get_item_url(self, item_id: str) -> str:
        """Calculates the downloadable url of an item in the feed."""

import abc

from fake_useragent import UserAgent

from core.model import PodcastFeed
from core.options import Options


class Plugin(abc.ABC):
    service = None
    plugin_name = None
    supports_fs_mode = False
    default_fs_mode_enabled = False

    PluginOptions = Options  # Redefine the PluginOptions class on a plugin to set the specific plugin options.

    def __init__(self, options: dict[str, str]):
        self.options = self.PluginOptions(**options)

    @abc.abstractmethod
    def get_feed(self, feed_id: str) -> PodcastFeed:
        """Calculates and returns the subscribable feed."""

    @abc.abstractmethod
    def get_item_url(self, item_id: str) -> str:
        """Calculates the downloadable url of an item in the feed."""

    def random_user_agent(self):
        return UserAgent().random

    def peek(self, item_id: str) -> dict[str, str]:
        """Handle a lightweight HEAD for a downloadable item. Returns a dict of headers."""
        return {}

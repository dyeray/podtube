import abc
from typing import Callable

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

    def get_download_fn(self, item_id: str) -> Callable[[str], None] | None:
        """Returns a callable that downloads the item into a given temp directory path.
        The callable signature is: download_fn(temp_dir: str) -> None.
        Returns None if the plugin does not support background downloads."""
        return None

    def random_user_agent(self):
        return UserAgent().random

    def peek(self, item_id: str) -> dict[str, str]:
        """Handle a lightweight HEAD for a downloadable item. Returns a dict of headers."""
        return {}

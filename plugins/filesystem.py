from datetime import datetime
from typing import List, Literal
from typing_extensions import ItemsView

import httpx
from parsel import Selector, SelectorList
from yt_dlp import YoutubeDL

from ytdl_config import ytdl_opts
from core.model import PodcastItem, PodcastFeed
from core.exceptions import PluginError
from core.options import Options
from core.plugin.plugin import Plugin
from core.storage.files import FileInfo
from core.storage.storage import Storage


class PluginImpl(Plugin):
    def __init__(self, options):
        super().__init__(options)
        self.storage = Storage(self)

    def get_feed(self, feed_id):
        items = self.storage.list_items(feed_id)

        return PodcastFeed(
            feed_id=feed_id,
            title=feed_id,
            description=feed_id,
            link="https://github.com/dyeray/podtube/",
            image="",
            items=self._get_items(feed_id, items),
        )

    def get_item_url(self, item_id):
        feed_id, item = item_id.split(":")
        return f"http://<base_url>/serve?plugin=filesystem&id={item}&namespace={feed_id}" # TODO

    def _get_items(self, feed_id: str, items: list[FileInfo]) -> list[PodcastItem]:
        return [self._get_item(feed_id, item) for item in items]

    def _get_item(self, feed_id: str, item: FileInfo):
        return PodcastItem(
            item_id=f'{feed_id}:{item.id}',
            title=item.filename.split(".")[0],
            description="",
            link="",
            date=None,
            image=None,
            content_type=item.mimetype or "",
        )

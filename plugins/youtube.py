from datetime import datetime
from typing import List

import httpx
from parsel import Selector, SelectorList
from yt_dlp import YoutubeDL

from ytdl_config import ytdl_opts
from core.model import PodcastItem, PodcastFeed
from core.exceptions import PluginError
from core.plugin.plugin import Plugin


class PluginImpl(Plugin):

    def __init__(self, options):
        super().__init__(options)
        self.resolver = YoutubeDL(ytdl_opts)

    def get_feed(self, feed_id):
        response = httpx.get(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={feed_id}"
        )
        sel = Selector(response.text)
        entries = sel.css("feed > entry")
        title = sel.css("feed > title::text").get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link=f"https://www.youtube.com/channel/{feed_id}",
            image="",
            items=self._get_items(entries),
        )

    def get_item_url(self, item_id):
        try:
            return self.resolver.extract_info(
                f"https://www.youtube.com/watch?v={item_id}", download=False
            )["url"]
        except Exception as ex:
            raise PluginError(ex)

    def _get_items(self, entries: SelectorList) -> List[PodcastItem]:
        return [self._get_item(entry) for entry in entries]

    def _get_item(self, entry: Selector):
        video_id = entry.css("videoId::text").get()
        return PodcastItem(
            item_id=video_id,
            title=entry.css("title::text").get(),
            description=entry.css("group > description::text").get(),
            link=f"https://www.youtube.com/watch?v={video_id}",
            date=datetime.fromisoformat(entry.css("published::text").get()),
            image=entry.css("group > thumbnail::attr(url)").get(),
            content_type="video/mp4",
        )

from datetime import datetime
from typing import List

import httpx
from parsel import Selector, SelectorList
from yt_dlp import YoutubeDL

from ytdl_config import ytdl_opts
from core.model import PodcastItem, PodcastFeed
from core.exceptions import PluginError
from core.options import Choice, Options
from core.plugin.plugin import Plugin

class FeedType(Choice):
    channel = "channel"
    playlist = "playlist"

    def __str__(self):
        return self.value


class PluginImpl(Plugin):
    service = "youtube.com"

    class PluginOptions(Options):
        feed_type: FeedType = "channel"

    namespace_map = {
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
        "atom": "http://www.w3.org/2005/Atom",  # Assigning a prefix to the default namespace
    }

    def __init__(self, options):
        super().__init__(options)
        self.resolver = YoutubeDL(ytdl_opts)

    def get_feed(self, feed_id):
        response = httpx.get(
            f"https://www.youtube.com/feeds/videos.xml?{self.options.feed_type}_id={feed_id}"
        )
        sel = Selector(response.text, type="xml")
        entries = sel.xpath("//atom:feed/atom:entry", namespaces=self.namespace_map)
        title = sel.xpath("//atom:feed/atom:title/text()", namespaces=self.namespace_map).get()
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
        video_id = entry.xpath("yt:videoId/text()", namespaces=self.namespace_map).get()
        return PodcastItem(
            item_id=video_id,
            title=entry.xpath("atom:title/text()", namespaces=self.namespace_map).get(),
            description=entry.xpath("media:group/media:description/text()", namespaces=self.namespace_map).get(),
            link=f"https://www.youtube.com/watch?v={video_id}",
            date=datetime.fromisoformat(entry.xpath("atom:published/text()", namespaces=self.namespace_map).get()),
            image=entry.xpath("media:group/media:thumbnail/@url", namespaces=self.namespace_map).get(),
            content_type="video/mp4",
        )

import os
from datetime import datetime

import ftfy
import httpx
from parsel import Selector, SelectorList
from pydantic import constr

from core.model import PodcastItem, PodcastFeed
from core.options import Options, Choice
from core.plugin.plugin import Plugin


class FeedType(Choice):
    channel = "channel"
    playlist = "playlist"

    def __str__(self):
        return self.value


class PluginImpl(Plugin):
    service = "youtube.com"

    class PluginOptions(Options):
        domain: constr(pattern=r"^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$")
        feed_type: FeedType = "channel"

    options: PluginOptions

    namespace_map = {
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
        "atom": "http://www.w3.org/2005/Atom",  # Assigning a prefix to the default namespace
    }

    def __init__(self, options: dict[str, str]):
        super().__init__({"domain": os.getenv("INVIDIOUS_DOMAIN"), **options})

    def get_feed(self, feed_id):
        response = httpx.get(
            f"https://{self.options.domain}/feed/{self.options.feed_type}/{feed_id}",
            timeout=15,
        )
        sel = Selector(response.text, type="xml")
        title = sel.xpath(
            "//atom:feed/atom:title/text()", namespaces=self.namespace_map
        ).get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link=self._get_feed_link(feed_id),
            image=sel.xpath(
                "//atom:feed/atom:icon/text()", namespaces=self.namespace_map
            ).get()
            or "",
            items=self._get_items(
                sel.xpath("//atom:feed/atom:entry", namespaces=self.namespace_map)
            ),
        )

    def _get_feed_link(self, feed_id):
        match self.options.feed_type:
            case FeedType.channel:
                return f"https://{self.options.domain}/channel/{feed_id}"
            case FeedType.playlist:
                return f"https://{self.options.domain}/playlist?list={feed_id}"

    def get_item_url(self, item_id):
        return f"https://{self.options.domain}/latest_version?id={item_id}&itag=18&local=true"

    def _get_items(self, entries: SelectorList) -> list[PodcastItem]:
        return [self._get_item(entry) for entry in entries]

    def _get_item(self, entry: Selector):
        video_id = (
            entry.xpath("yt:videoId/text()", namespaces=self.namespace_map).get()
            or entry.xpath("yt:videoId/text()", namespaces=self.namespace_map)
            .get()
            .split(":")[-1]
        )
        description = (
            entry.xpath("atom:content", namespaces=self.namespace_map).get()
            or entry.xpath(
                "media:group/media:description/text()", namespaces=self.namespace_map
            ).get()
        )
        return PodcastItem(
            item_id=video_id,
            title=entry.xpath("atom:title/text()", namespaces=self.namespace_map).get(),
            description=description and ftfy.fix_text(description),
            link=f"https://{self.options.domain}/watch?v={video_id}",
            date=datetime.fromisoformat(
                entry.xpath(
                    "atom:published/text()", namespaces=self.namespace_map
                ).get()
            ),
            image=entry.xpath(
                "media:group/media:thumbnail/@url", namespaces=self.namespace_map
            ).get(),
            content_type="video/mp4",
        )

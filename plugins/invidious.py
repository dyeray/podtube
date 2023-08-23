import os
from datetime import datetime

import requests
from parsel import Selector, SelectorList

from core.model import PodcastItem, PodcastFeed
from core.options import Options, Choice
from core.plugin.plugin import Plugin


class FeedType(Choice):
    channel = 'channel'
    playlist = 'playlist'

    def __str__(self):
        return self.value


class PluginImpl(Plugin):
    class PluginOptions(Options):
        domain: str
        feed_type: FeedType = 'channel'
    options: PluginOptions

    def __init__(self, options: dict[str, str]):
        super().__init__({'domain': os.getenv('INVIDIOUS_DOMAIN'), **options})

    def get_feed(self, feed_id):
        response = requests.get(f"https://{self.options.domain}/feed/{self.options.feed_type}/{feed_id}")
        sel = Selector(response.text)
        title = sel.css('feed > title::text').get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link=self._get_feed_link(feed_id),
            image=sel.css('feed > icon::text').get() or '',
            items=self._get_items(sel.css('feed > entry'))
        )

    def _get_feed_link(self, feed_id):
        match self.options.feed_type:
            case FeedType.channel:
                return f'https://{self.options.domain}/channel/{feed_id}'
            case FeedType.playlist:
                return f'https://{self.options.domain}/playlist?list={feed_id}'

    def get_item_url(self, item_id):
        return f'https://{self.options.domain}/latest_version?id={item_id}&itag=18'

    def _get_items(self, entries: SelectorList) -> list[PodcastItem]:
        return [self._get_item(entry) for entry in entries]

    def _get_item(self, entry: Selector):
        video_id = entry.css('videoId::text').get()
        return PodcastItem(
            item_id=video_id,
            title=entry.css('title::text').get(),
            description=entry.css('description::text').get(),
            date=datetime.fromisoformat(entry.css('published::text').get()),
            image=entry.css('group > thumbnail::attr(url)').get(),
            content_type="video/mp4",
        )

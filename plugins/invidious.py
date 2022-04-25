from datetime import datetime

import requests
from parsel import Selector, SelectorList

from core.model import PodcastItem, PodcastFeed
from core.options import Options
from core.plugin.plugin import Plugin


class PluginImpl(Plugin):
    class PluginOptions(Options):
        domain = 'invidious.namazso.eu'
    options: PluginOptions

    def get_feed(self, feed_id):
        response = requests.get(f"https://{self.options.domain}/feed/channel/{feed_id}")
        sel = Selector(response.text)
        title = sel.css('feed > title::text').get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link=f'https://{self.options.domain}/channel/{feed_id}',
            image=sel.css('feed > icon::text').get(),
            items=self._get_items(sel.css('feed > entry'))
        )

    def get_item_url(self, item_id):
        return f'https://{self.options.domain}/latest_version?id={item_id}&itag=18&local=true'

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

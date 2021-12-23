from datetime import datetime

import requests
from parsel import Selector, SelectorList

from model import PodcastItem, PodcastFeed
from plugins.plugin import Plugin


class InvidiousPlugin(Plugin):
    def get_feed(self, feed_id, base_url, options: dict[str, str]):
        domain = options.get('domain', 'yewtu.be')
        response = requests.get(f"https://yewtu.be/feed/channel/{feed_id}")
        sel = Selector(response.text)
        title = sel.css('feed > title::text').get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link=f'https://{domain}/channel/{feed_id}',
            image=sel.css('feed > icon::text').get(),
            items=self._get_items(sel.css('feed > entry'), base_url, domain)
        )

    def get_item_url(self, item_id):
        domain, yt_id = item_id.split('-', 1)
        return f'https://{domain}/latest_version?id={yt_id}&itag=18&local=true'

    def _get_items(self, entries: SelectorList, base_url: str, domain: str) -> list[PodcastItem]:
        return [self._get_item(entry, base_url, domain) for entry in entries]

    def _get_item(self, entry: Selector, base_url: str, domain: str):
        video_id = entry.css('videoId::text').get()
        return PodcastItem(
            item_id=video_id,
            url=f'{base_url}download?s=invidious&id={domain}-{video_id}',
            title=entry.css('title::text').get(),
            description=entry.css('description::text').get(),
            date=datetime.fromisoformat(entry.css('published::text').get()),
            image=entry.css('group > thumbnail::attr(url)').get(),
            content_type="video/mp4",
        )

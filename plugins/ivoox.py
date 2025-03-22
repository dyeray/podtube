import re
from typing import List, Union

import dateparser
import ftfy
import httpx
from parsel import Selector, SelectorList

from core.model import PodcastFeed, PodcastItem
from core.plugin.plugin import Plugin


class PluginImpl(Plugin):
    service = "ivoox.com"

    feed_id_pattern = r'^.+_sq_(f\d+)_1$'

    def get_feed(self, feed_id):
        """Calculates and returns the subscribable feed."""
        url = f"https://www.ivoox.com/{feed_id}.html"
        match = re.match(self.feed_id_pattern, feed_id)
        parsed_feed_id = match.group(1) if match else None
        feed_url = f"https://www.ivoox.com/feed_fg_{parsed_feed_id}_filtro_1.xml"
        response = httpx.get(feed_url, follow_redirects=True)
        sel = Selector(response.text, type='xml')
        return PodcastFeed(
            feed_id=feed_id,
            title=ftfy.fix_text(sel.css("channel > title::text").get()),
            description=ftfy.fix_text(sel.css("channel > description::text").get()),
            link=url,
            image=sel.css("channel > image > url::text").get(),
            items=self._get_items(sel.css("channel > item")),
        )

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        return f"http://www.ivoox.com/listen_mn_{item_id}_feed_1.m4a?internal=HTML5"

    def _get_items(self, items: SelectorList) -> List[PodcastItem]:
        return [
            item
            for item in (self._get_item(item) for item in items)
            if item is not None
        ]

    def _get_item(self, item: Selector) -> Union[PodcastItem, None]:
        return PodcastItem(
            item_id=item.css('guid::text').get().split('/')[-1],
            title=ftfy.fix_text(item.css('title::text').get()),
            description=ftfy.fix_text(item.css('description::text').get()),
            link=item.css('link::text').get(),
            date=dateparser.parse(item.css('pubDate::text').get()),
            image=item.xpath('.//*[local-name()="image"]/@href').get(),
            content_type="audio/mp4",
        )

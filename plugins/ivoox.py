import json
import re
from typing import List, Union

import dateparser
import httpx
from parsel import Selector, SelectorList

from core.model import PodcastFeed, PodcastItem
from core.options import Options
from core.utils import clean
from core.plugin.plugin import Plugin


class PluginImpl(Plugin):
    service = "ivoox.com"

    class PluginOptions(Options):
        max_pagination: int = 1

    options: PluginOptions

    def get_feed(self, feed_id):
        """Calculates and returns the subscribable feed."""
        url = f"https://www.ivoox.com/{feed_id}.html"
        response = httpx.get(url, follow_redirects=True)
        sel = Selector(response.text)
        videos = sel.xpath('.//div[contains(@class, "play-container")]/../../..')
        '''
        current_page = 1
        while current_page < self.options.max_pagination:
            current_page += 1
            next_page_url = sel.css(".pagination li:last-child a::attr(href)").get()
            if next_page_url == "#":
                break
            response = httpx.get(next_page_url, follow_redirects=True)
            sel = Selector(response.text)
            videos.extend(sel.css(".modulo-type-episodio"))
        '''
        match = re.search(r'<script[^>]*>\s*(\{"@context":"https://schema.org/","@type":"PodcastSeries",.*?\})\s*</script>', response.text, re.DOTALL)
        data = json.loads(match[1])
        return PodcastFeed(
            feed_id=feed_id,
            title=data['name'],
            description=data['description'],
            link=url,
            image=data['image'],
            items=self._get_items(videos),
        )

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        match = re.match(r".*(_\d+_\d)", item_id)
        podcast_id = match and match.group(1)[1:]
        return f"http://www.ivoox.com/listen_mn_{podcast_id}.m4a?internal=HTML5"

    def _get_items(self, items: SelectorList) -> List[PodcastItem]:
        return [
            item
            for item in (self._get_item(item) for item in items)
            if item is not None
        ]

    def _get_item(self, item: Selector) -> Union[PodcastItem, None]:
        '''
        has_support_badge = item.css(".title-wrapper span.fan-title").get() is not None
        if has_support_badge:
            return None
        date = dateparser.parse(
            item.css(".action .date::attr(title)").get(),
            settings={"RETURN_AS_TIMEZONE_AWARE": True, "TO_TIMEZONE": "UTC"},
        )
        '''
        url = item.xpath('.//a/@href').get().strip('//')
        re_item_id = re.match(r'www\.ivoox\.com/(.+?)\.html$', url)
        item_id = re_item_id and re_item_id.group(1)
        return PodcastItem(
            item_id=item_id,
            title=item.xpath('.//img/@alt').get(),
            description=clean(item.xpath('.//div[contains(@class, "description")]/text()').get())
            or "",
            link=f"https://www.ivoox.com/{item_id}.html",
            date=None,
            image=item.xpath('.//img/@data-lazy-src').get(),
            content_type="audio/mp4",
        )

    def _get_episode_image(self, item: Selector):
        image_url = item.css("a img::attr(data-src)").get()
        if not image_url:
            return
        if image_url.endswith(".jpg") or image_url.endswith(".png"):
            return image_url
        match = re.match(r".*url=(.*)\?ts=.*", image_url)
        return match and match.group(1)

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
        videos = sel.css(".modulo-type-episodio")
        current_page = 1
        while current_page < self.options.max_pagination:
            current_page += 1
            next_page_url = sel.css(".pagination li:last-child a::attr(href)").get()
            if next_page_url == "#":
                break
            response = httpx.get(next_page_url, follow_redirects=True)
            sel = Selector(response.text)
            videos.extend(sel.css(".modulo-type-episodio"))
        return PodcastFeed(
            feed_id=feed_id,
            title=clean(sel.css("#list_title_new::text").get()),
            description=clean(sel.css(".overview::text").get()),
            link=url,
            image=sel.css("meta[property='og:image']::attr(content)").get(),
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
        has_support_badge = item.css(".title-wrapper span.fan-title").get() != None
        if has_support_badge == True:
            return None
        url = item.css(".title-wrapper a::attr(href)").get()
        re_item_id = re.match(r"https?://www\.ivoox\.com/([-_\w\d]+)\.html", url)
        item_id = re_item_id and re_item_id.group(1)
        date = dateparser.parse(
            item.css(".action .date::attr(title)").get(),
            settings={"RETURN_AS_TIMEZONE_AWARE": True, "TO_TIMEZONE": "UTC"},
        )
        return PodcastItem(
            item_id=item_id,
            title=item.css(".title-wrapper a::attr(title)").get(),
            description=item.css(".audio-description button::attr(data-content)").get()
            or "",
            link=f"https://www.ivoox.com/{item_id}.html",
            date=date,
            image=self._get_episode_image(item),
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

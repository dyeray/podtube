import json
import re
from datetime import datetime
from typing import List, Union

import dateparser
import httpx
from parsel import Selector, SelectorList

from core.model import PodcastFeed, PodcastItem
from core.options import Options
from core.utils import clean
from core.plugin.plugin import Plugin


def find_path(data, target, path=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            result = find_path(value, target, path + [str(key)])
            if result:
                return result
    elif isinstance(data, list):
        for i, value in enumerate(data):
            result = find_path(value, target, path + [str(i)])
            if result:
                return result
    elif isinstance(data, str) and target in data:
        return path
    return None


class PluginImpl(Plugin):
    service = "mitele.es"

    class PluginOptions(Options):
        pass

    options: PluginOptions

    pattern = r'<script type="text/javascript">window.\$REACTBASE_STATE.container_mtweb = (.*?)(?=</script>\n)'

    def get_feed(self, feed_id):
        """Calculates and returns the subscribable feed."""
        url = f"https://www.mitele.es/programas-tv/{feed_id}/"
        response = httpx.get(url, follow_redirects=True)
        episodes = self.get_episode_dict(response)
        return PodcastFeed(
            feed_id=feed_id,
            title="",
            description="",
            link="",
            image="",
            items=self._get_items(feed_id, episodes),
        )

    def get_episode_dict(self, response):
        match = re.search(self.pattern, response.text)
        if match:
            json_data = match.group(1)
            dictionary = json.loads(json_data)
        return dictionary["container"]["tabs"][0]["contents"][0]["children"]

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        url = f"https://www.mitele.es/programas-tv/{item_id}/player"
        breakpoint()
        pass

    def _get_items(self, feed_id: str, items: List[dict]) -> List[PodcastItem]:
        return [
            item
            for item in (self._get_item(feed_id, item) for item in items)
            if item is not None
        ]

    def _get_item(self, feed_id: str, item: dict) -> Union[PodcastItem, None]:
        pattern = r"/programas-tv/{}/(.*?)/player".format(feed_id)
        result = re.search(pattern, item["link"]["href"]).group(1)
        return PodcastItem(
            item_id=result,
            title=f"{item['info']['episode_number']} - {item['title']}",
            description=item["info"]["synopsis"],
            link=item["link"]["href"],
            date=datetime.fromisoformat(f"{item['info']['creation_date']}T00:00:00Z"),
            image=item["images"]["thumbnail"]["src"],
            content_type="video/mp4",
        )

    def _get_episode_image(self, item: Selector):
        image_url = item.css("a img::attr(data-src)").get()
        if not image_url:
            return
        if image_url.endswith(".jpg") or image_url.endswith(".png"):
            return image_url
        match = re.match(r".*url=(.*)\?ts=.*", image_url)
        return match and match.group(1)

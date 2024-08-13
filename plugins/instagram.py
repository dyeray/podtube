import datetime
import json
import re
from typing import List, Union

import httpx
from yt_dlp import YoutubeDL

from core.exceptions import PluginError
from core.model import PodcastFeed, PodcastItem
from core.plugin.plugin import Plugin
from core.utils import safe_traverse


class PluginImpl(Plugin):
    service = "instagram.com"

    def get_feed(self, feed_id):
        """Calculates and returns the subscribable feed."""
        with httpx.Client() as client:
            url = f"https://www.instagram.com/{feed_id}/"
            response = client.get(url)
            match = re.search(r'"customHeaders":({.*?}),', response.text, re.DOTALL)
            custom_headers = match and json.loads(match.group(1))
            api_response = client.get(
                url=f"https://www.instagram.com/api/v1/users/web_profile_info/?username={feed_id}",
                headers={"X-IG-App-ID": custom_headers["X-IG-App-ID"]},
            )
            data = json.loads(api_response.text)
            videos = [
                item["node"]
                for item in data["data"]["user"]["edge_owner_to_timeline_media"][
                    "edges"
                ]
                if item["node"]["__typename"] == "GraphVideo"
            ]
        return PodcastFeed(
            feed_id=feed_id,
            title=f"{data['data']['user']['full_name']} @{data['data']['user']['username']}",
            description=data["data"]["user"]["biography"],
            link=url,
            image=data["data"]["user"]["profile_pic_url"],
            items=self._get_items(videos),
        )

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        try:
            # It would be possible to get the video by accessing data API key 'video_url'. Issues:
            # * If we return the url directly when genrating the feed, url may expire before download.
            # * If we call data API when user requests download, info about that video might not be there anymore.
            return YoutubeDL().extract_info(
                self._get_story_url(item_id), download=False
            )["url"]
        except Exception as ex:
            raise PluginError(ex)

    def _get_items(self, items: List[dict]) -> List[PodcastItem]:
        return [
            item
            for item in (self._get_item(item) for item in items)
            if item is not None
        ]

    def _get_item(self, item: dict) -> Union[PodcastItem, None]:
        item_id = item["shortcode"]
        info = (
            safe_traverse(item, "edge_media_to_caption", "edges", 0, "node", "text")
            or ""
        ).split("\n", 1)
        return PodcastItem(
            item_id=item_id,
            title=safe_traverse(info, 0) or "",
            description=safe_traverse(info, 1) or "",
            link=self._get_story_url(item_id),
            date=datetime.datetime.utcfromtimestamp(item["taken_at_timestamp"]).replace(
                tzinfo=datetime.timezone.utc
            ),
            image=item["thumbnail_src"],
            content_type="video/mp4",
        )

    @staticmethod
    def _get_story_url(item_id: str):
        return f"https://www.instagram.com/reel/{item_id}/"

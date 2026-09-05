import json
import os
import re
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime
from typing import Callable
from urllib.parse import urlparse

import httpx
from parsel import Selector
from yt_dlp import YoutubeDL

from core.exceptions import PluginError
from core.model import PodcastFeed, PodcastItem
from core.plugin.plugin import Plugin
from core.plugin.ytdl_logger import Logger


class PluginImpl(Plugin):
    service = "rumble.com"
    supports_fs_mode = True

    @property
    def downloader(self):
        return YoutubeDL(
            {"format": "best", "logger": Logger()}
        )

    def get_feed(self, feed_id: str) -> PodcastFeed:
        url = f"https://rumble.com/user/{feed_id}/videos"
        response = httpx.get(
            url,
            follow_redirects=True,
            headers={"User-Agent": self.random_user_agent()},
        )
        response.raise_for_status()
        selector = Selector(response.text)
        data = json.loads(selector.css('script[type="application/json"]::text').get())
        return PodcastFeed(
            feed_id=feed_id,
            title=selector.css('meta[property="og:title"]::attr(content)').get(),
            description=selector.css('meta[name="description"]::attr(content)').get(),
            link=url,
            image=selector.css("img.channel-header--img::attr(src)").get(),
            items=[self._get_item(item) for item in data["items"]],
        )

    def get_item_url(self, item_id: str) -> str:
        try:
            return self.downloader.extract_info(
                self._get_video_url(item_id), download=False
            )["url"]
        except Exception as ex:
            raise PluginError(ex)

    def get_download_fn(self, item_id: str) -> Callable[[str], None]:
        url = self._get_video_url(item_id)

        def download(temp_dir: str) -> None:
            with YoutubeDL(
                {
                    "format": "best",
                    "logger": Logger(),
                    "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
                }
            ) as downloader:
                downloader.download([url])

        return download

    @staticmethod
    def _get_video_url(item_id: str) -> str:
        try:
            url = urlsafe_b64decode(item_id + "=" * (-len(item_id) % 4)).decode()
            parsed_url = urlparse(url)
            if (
                parsed_url.scheme != "https"
                or parsed_url.netloc != "rumble.com"
                or not re.fullmatch(r"/v(?!ideos)[\w.-]+\.html", parsed_url.path)
                or parsed_url.query
                or parsed_url.fragment
            ):
                raise ValueError("Invalid Rumble video URL")
            return url
        except Exception as ex:
            raise PluginError(ex)

    @staticmethod
    def _get_item(item: dict) -> PodcastItem:
        return PodcastItem(
            item_id=urlsafe_b64encode(item["url"].encode()).decode().rstrip("="),
            title=item["title"],
            description=item["title"],
            link=item["url"],
            date=datetime.fromisoformat(item["upload_date"]),
            image=item["thumb"],
            content_type="video/mp4",
        )

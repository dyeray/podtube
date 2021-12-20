from abc import ABC
from datetime import datetime
from typing import List

import requests
from parsel import Selector, SelectorList
from pytube import YouTube
from pytube.exceptions import PytubeError
from yt_dlp import YoutubeDL

from ytdl_config import ytdl_opts
from model import PodcastItem, PodcastFeed
from plugins.plugin import Plugin


class YouTubePlugin(Plugin, ABC):

    def get_feed(self, feed_id, base_url, options: dict[str, str]):
        response = requests.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={feed_id}")
        sel = Selector(response.text)
        entries = sel.css('feed > entry')
        title = sel.css("feed > title::text").get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link='https://www.youtube.com/channel/' + feed_id,
            image="",
            items=self._get_items(entries, base_url)
        )

    def _get_items(self, entries: SelectorList, base_url: str) -> List[PodcastItem]:
        return [self._get_item(entry, base_url) for entry in entries]

    def _get_item(self, entry: Selector, base_url: str):
        video_id = entry.css('videoId::text').get()
        return PodcastItem(
            item_id=video_id,
            url=base_url + 'download?id=' + video_id,
            title=entry.css('title::text').get(),
            description=entry.css('group > description::text').get(),
            date=datetime.fromisoformat(entry.css('published::text').get()),
            image=entry.css('group > thumbnail::attr(url)').get(),
            content_type="video/mp4",
        )


class PyTube(YouTubePlugin):

    def get_item_url(self, item_id):
        try:
            return (YouTube(f'https://www.youtube.com/watch?v={item_id}').streams
                    .filter(progressive=True, subtype='mp4')
                    .order_by('resolution')
                    .desc()
                    .all()[0].url)
        except PytubeError:
            raise PluginException


class YouTubeDL(YouTubePlugin):
    def __init__(self):
        self.ytdl = YoutubeDL(ytdl_opts)

    def get_item_url(self, item_id):
        try:
            return self.ytdl.extract_info(f'https://www.youtube.com/watch?v={item_id}', download=False)['url']
        except Exception:
            raise PluginException


class PluginException(Exception):
    pass

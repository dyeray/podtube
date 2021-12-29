from datetime import datetime
from typing import List

import requests
from parsel import Selector, SelectorList
from pytube import YouTube
from pytube.exceptions import PytubeError
from yt_dlp import YoutubeDL

from ytdl_config import ytdl_opts
from core.model import PodcastItem, PodcastFeed
from core.exceptions import PluginError, InputError
from core.plugin.plugin import Plugin


class PluginImpl(Plugin):

    def get_feed(self, feed_id):
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
            items=self._get_items(entries)
        )

    def get_item_url(self, item_id):
        match self.options.get('plugin.library', 'pytube'):
            case 'yt-dlp':
                return YtDlpResolver().get_url(item_id)
            case 'pytube':
                return PyTubeResolver().get_url(item_id)
            case _:
                raise InputError('Invalid youtube library defined')

    def _get_items(self, entries: SelectorList) -> List[PodcastItem]:
        return [self._get_item(entry) for entry in entries]

    def _get_item(self, entry: Selector):
        video_id = entry.css('videoId::text').get()
        return PodcastItem(
            item_id=video_id,
            title=entry.css('title::text').get(),
            description=entry.css('group > description::text').get(),
            date=datetime.fromisoformat(entry.css('published::text').get()),
            image=entry.css('group > thumbnail::attr(url)').get(),
            content_type="video/mp4",
        )


class PyTubeResolver:

    def get_url(self, video_id: str):
        try:
            return (YouTube(f'https://www.youtube.com/watch?v={video_id}').streams
                    .filter(progressive=True, subtype='mp4')
                    .order_by('resolution')
                    .desc()
                    .all()[0].url)
        except PytubeError as ex:
            raise PluginError(ex)


class YtDlpResolver:
    def __init__(self):
        self.ytdl = YoutubeDL(ytdl_opts)

    def get_url(self, video_id: str):
        try:
            return self.ytdl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)['url']
        except Exception as ex:
            raise PluginError(ex)

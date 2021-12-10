from typing import List

import dateutil.parser
import requests
from parsel import Selector, SelectorList
from pytube import YouTube
from pytube.exceptions import PytubeError
from yt_dlp import YoutubeDL

from scraper import extract
from ytdl_config import ytdl_opts
from model import PodcastItem, PodcastFeed
from plugins.plugin import Plugin


class YouTubePlugin(Plugin):

    def get_feed(self, feed_id, base_url):
        response = requests.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={feed_id}")
        sel = Selector(response.text)
        entries = sel.css('feed > entry')
        title = sel.css("feed > title").get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link='https://www.youtube.com/channel/' + feed_id,
            image="",
            items=self._get_items(entries, base_url)
        )

    def get_item_url(self, item_id):
        return self.extract_link(f'https://www.youtube.com/watch?v={item_id}')

    def _get_items(self, entries: SelectorList, base_url: str) -> List[PodcastItem]:
        items = []
        for entry in entries:
            video_id = extract(entry.css('videoId::text'))
            items.append(PodcastItem(
                item_id=video_id,
                url=base_url + 'download?id=' + video_id,
                title=extract(entry.css('title::text')),
                description=extract(entry.css('group > description::text')),
                date=dateutil.parser.parse(extract(entry.css('published::text'))),
                image=extract(entry.css('group > thumbnail::attr(url)')),
                content_type="video/mp4",
            ))
        return items


class PyTube(YouTubePlugin):

    def extract_link(self, url):
        try:
            return (YouTube(url).streams
                    .filter(progressive=True, subtype='mp4')
                    .order_by('resolution')
                    .desc()
                    .all()[0].url)
        except PytubeError:
            raise PluginException


class YouTubeDL(YouTubePlugin):
    def __init__(self):
        self.ytdl = YoutubeDL(ytdl_opts)

    def extract_link(self, url):
        try:
            return self.ytdl.extract_info(url, download=False)['url']
        except Exception:
            raise PluginException


class PluginException(Exception):
    pass

import os
from functools import lru_cache
from typing import List

import dateutil.parser
import requests
import youtube_dl
from apiclient import discovery
from pytube import YouTube
from pytube.exceptions import PytubeError

from ytdl_config import ytdl_opts
from model import PodcastItem, PodcastFeed


class YouTubePlugin:

    def get_feed(self, channel_id):
        service = self._get_youtube_client()
        channel = service.channels().list(part='snippet', id=channel_id).execute()['items'][0]
        return self._get_feed(
            feed_id=channel_id,
            query={'channelId': channel_id},
            title=channel['snippet']['title'],
            description=channel['snippet']['description'],
            link='https://www.youtube.com/channel/' + channel_id,
            image=channel['snippet']['thumbnails']['high']['url'],
        )

    def _get_feed(self, feed_id, query, title, description, link, image):
        service = self._get_youtube_client()
        videos = service.search().list(part='snippet', **query, order='date',
                                       type='video', safeSearch='none').execute()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=description,
            link=link,
            image=image,
            items=self._get_items(videos)
        )

    def _get_items(self, videos) -> List[PodcastItem]:
        items = []
        for video in videos['items']:
            try:
                video_url = self.extract_link(
                    "https://www.youtube.com/watch?v=" + video['id']['videoId'])
            except PluginException:
                continue
            video_info = requests.head(video_url)
            items.append(PodcastItem(
                item_id=video['id']['videoId'],
                url=video_url,
                title=video['snippet']['title'],
                description=video['snippet']['description'],
                date=dateutil.parser.parse(video['snippet']['publishedAt']),
                image=video['snippet']['thumbnails']['high']['url'],
                content_length=video_info.headers['Content-Length'],
                content_type=video_info.headers['Content-Type'],
            ))
        return items

    def extract_link(self, url):
        raise NotImplementedError

    @lru_cache(maxsize=1)
    def _get_youtube_client(self):
        return discovery.build('youtube', 'v3', developerKey=os.environ['youtube_developer_key'])


class PyTube(YouTubePlugin):

    def extract_link(self, url):
        try:
            return YouTube(url).streams.filter(progressive=True, subtype='mp4').order_by('resolution').desc().all()[0]
        except PytubeError:
            raise PluginException


class YouTubeDL(YouTubePlugin):
    def __init__(self):
        self.ytdl = youtube_dl.YoutubeDL(ytdl_opts)

    def extract_link(self, url):
        try:
            return self.ytdl.extract_info(url, download=False)['url']
        except Exception:
            raise PluginException


class PluginException(Exception):
    pass

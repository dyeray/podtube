import os
from functools import lru_cache

import youtube_dl
from pytube import YouTube
from pytube.exceptions import PytubeError, AgeRestricted

from ytdl_config import ytdl_opts


class YouTubePlugin:

    def extract_link(self, url):
        raise NotImplementedError


class PyTube(YouTubePlugin):

    def extract_link(self, url):
        try:
            return YouTube(url).filter('mp4')[0].url
        except (PytubeError, AgeRestricted):
            raise PluginException


class YouTubeDL(YouTubePlugin):
    def __init__(self):
        self.ytdl = youtube_dl.YoutubeDL(ytdl_opts)

    def extract_link(self, url):
        try:
            return self.ytdl.extract_info(url, download=False)['url']
        except Exception:
            raise PluginException


@lru_cache(maxsize=1)
def get_plugin_from_settings():
    name_to_class = {
        'YouTubeDL': YouTubeDL,
        'PyTube': PyTube,
    }
    plugin_cls = name_to_class[os.environ['youtube_backend']]
    return plugin_cls()


class PluginException(Exception):
    pass

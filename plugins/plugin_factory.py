import os
from functools import lru_cache

from plugins.youtube import YouTubeDL, PyTube
from plugins.ivoox import IvooxPlugin


@lru_cache(maxsize=1)
def get_plugin_from_settings():
    name_to_class = {
        'YouTubeDL': YouTubeDL,
        'PyTube': PyTube,
    }
    plugin_cls = name_to_class[os.environ['youtube_backend']]
    return plugin_cls()


class PluginFactory:

    plugins = {
        'youtube': get_plugin_from_settings,
        'ivoox': IvooxPlugin
    }

    @classmethod
    def create(cls, service):
        constructor = cls.plugins.get(service, 'youtube')
        return constructor()


class PluginException(Exception):
    pass

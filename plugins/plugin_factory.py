import os
from functools import lru_cache

from plugins.youtube import YouTubeDL, PyTube
from plugins.ivoox import IvooxPlugin
from plugins.invidious import InvidiousPlugin


@lru_cache(maxsize=1)
def get_plugin_from_settings():
    name_to_class = {
        'YouTubeDL': YouTubeDL,
        'PyTube': PyTube,
    }
    plugin_cls = name_to_class[os.environ.get('youtube_backend', 'PyTube')]
    return plugin_cls()


class PluginFactory:

    plugins = {
        'youtube': get_plugin_from_settings,
        'ivoox': IvooxPlugin,
        'invidious': InvidiousPlugin
    }

    @classmethod
    def create(cls, service):
        constructor = cls.plugins.get(service, get_plugin_from_settings)
        return constructor()


class PluginException(Exception):
    pass

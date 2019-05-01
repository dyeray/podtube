import os
from functools import lru_cache

from plugins.youtube import YouTubeDL, PyTube


class PluginFactory:

    @staticmethod
    def create(service):
        return get_plugin_from_settings()


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

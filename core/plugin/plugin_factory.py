import os
import pkgutil

from importlib import import_module
from typing import Type

from core.exceptions import InputError
from core.plugin import Plugin
from core.utils import find_first


class PluginFactory:
    plugins: list[Type[Plugin]] = []

    @classmethod
    def autodiscover(cls):
        plugins_package = 'plugins'

        # Discover and import each plugin module
        discovered_plugins = pkgutil.iter_modules([plugins_package.replace('.', '/')])
        for finder, name, ispkg in discovered_plugins:
            if not ispkg:
                module_name = f"{plugins_package}.{name}"
                module = import_module(module_name)
                if hasattr(module, 'PluginImpl'):
                    module.PluginImpl.plugin_name = name
                    cls.plugins.append(module.PluginImpl)

    @classmethod
    def create(cls, service: str | None, plugin_name: str | None, options: dict[str, str]) -> Plugin:
        plugins = cls.get_plugins_from_service(service) if service else cls.get_plugins_from_plugin_name(plugin_name)
        if len(plugins) == 0:
            raise InputError(f"Invalid service '{service}' or plugin '{plugin_name}' defined")
        plugin_cls = plugins[0]
        return plugin_cls(options)

    @classmethod
    def get_plugins_from_service(cls, service: str) -> list[Type[Plugin]]:
        plugins = [plugin for plugin in cls.plugins if plugin.service == service]
        preferred_plugin_name = os.getenv(f"PODTUBE_PLUGIN_{service}")
        preferred_plugin = preferred_plugin_name and find_first(plugins, lambda x: x.plugin_name == preferred_plugin_name)
        return [preferred_plugin] if preferred_plugin else plugins

    @classmethod
    def get_plugins_from_plugin_name(cls, plugin_name):
        return [plugin for plugin in cls.plugins if plugin.plugin_name == plugin_name]

# Usage
PluginFactory.autodiscover()

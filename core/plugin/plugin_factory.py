import pkgutil

from importlib import import_module
from typing import Type

from core.exceptions import InputError
from core.plugin import Plugin


class PluginFactory:
    plugins_dict: dict[str, Type[Plugin]] = {}

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
                    cls.plugins_dict[name] = module.PluginImpl

    @classmethod
    def create(cls, service: str, options: dict[str, str]) -> Plugin:
        if service not in cls.plugins_dict:
            raise InputError(f"Invalid service {service} defined")
        plugin_cls = cls.plugins_dict[service]
        return plugin_cls(options)


# Usage
PluginFactory.autodiscover()

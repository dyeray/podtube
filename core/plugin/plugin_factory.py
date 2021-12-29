from importlib import import_module
from typing import Type

from core.plugin import Plugin
from core.exceptions import InputError


class PluginFactory:

    @classmethod
    def create(cls, service, options: dict[str, str]) -> Plugin:
        try:
            module = import_module(f'plugins.{service}')
        except ModuleNotFoundError:
            raise InputError(f'Invalid service {service} defined')
        plugin_cls: Type[Plugin] = module.PluginImpl
        return plugin_cls(options)

from importlib import import_module
from typing import Type

from core.service import Service
from core.exceptions import InputError


class ServiceFactory:

    @classmethod
    def create(cls, service: str, options: dict[str, str]) -> Service:
        try:
            module = import_module(f'plugins.{service}')
        except ModuleNotFoundError:
            raise InputError(f'Invalid service {service} defined')
        service_cls: Type[Service] = module.ServiceImpl
        return service_cls(options)

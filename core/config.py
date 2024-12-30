import os

from core.plugin import Plugin


class Config:
    @staticmethod
    def is_filesystem_mode_enabled(plugin: Plugin) -> bool:
        global_fs_mode_enabled = get_bool_env('PODTUBE_FILESYSTEM_MODE')
        plugin_fs_mode_enabled = get_bool_env(f'PODTUBE_FILESYSTEM_MODE_PLUGIN_{plugin.plugin_name}', plugin.default_fs_mode_enabled)
        return global_fs_mode_enabled and plugin.supports_fs_mode and plugin_fs_mode_enabled

    @staticmethod
    def get_port():
        port = os.getenv("PODTUBE_PORT")
        return int(port) if port and port.isdigit() else 8080

    @staticmethod
    def get_required_api_key():
        return os.getenv("PODTUBE_API_KEY")

    @staticmethod
    def get_preferred_plugin_for_service(service: str):
        return os.getenv(f"PODTUBE_PLUGIN_{service}")

def get_bool_env(name, default=False):
    str_value = os.getenv(name)
    if str_value is None:
        return default
    return str_value.lower() == 'true'

import glob
import mimetypes
import os
from collections import OrderedDict

from core.plugin.plugin import Plugin
from core.storage.hasher import Hasher
from core.storage.files import SharedFile, FileInfo

class Storage:
    def __init__(self, plugin: Plugin):
        self.path = f'storage/{plugin.plugin_name}'
        self.hasher = Hasher()

    def list_items(self, namespace: str) -> list[FileInfo]:
        return [FileInfo(id=id, mimetype=mimetypes.guess_type(filename)[0], filename=filename) for id, filename in self._get_namespace_files(namespace).items()]

    def serve(self, namespace: str, id: str) -> SharedFile:
        path = self.path + f'/{namespace}/'
        filename = self._get_namespace_files(namespace)[id]
        return SharedFile(
            file_handle=open(path + filename, 'rb'),
            file_info=FileInfo(
                id=id,
                mimetype=mimetypes.guess_type(filename)[0],
                filename=filename
            )
        )

    def _get_namespace_files(self, namespace: str) -> dict[str, str]:
        path = self.path + f'/{namespace}/'
        items = sorted(glob.glob('*', root_dir=path), key=lambda x: os.path.getmtime(f"{path}{x}"))
        return OrderedDict((self.hasher.hash(item), item) for item in items)

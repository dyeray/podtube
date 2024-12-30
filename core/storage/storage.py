import glob
import mimetypes
import os
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from core.config import Config
from core.exceptions import InputError
from core.plugin.plugin import Plugin
from core.storage.hasher import Hasher
from core.storage.files import SharedFile, FileInfo


class Storage:
    def __init__(self, plugin: Plugin):
        self.base_path = Path('storage').joinpath(plugin.plugin_name).resolve()
        self.hasher = Hasher()
        self.plugin = plugin

    def list_items(self, namespace: str) -> list[FileInfo]:
        self._assert_permissions()
        return [self._build_file_info(file_id, filename, namespace) for file_id, filename in self._get_namespace_files(namespace).items()]

    def serve(self, namespace: str, file_id: str) -> SharedFile:
        self._assert_permissions()
        filename = self._get_namespace_files(namespace)[file_id]
        full_filename = self._path(namespace, filename)
        return SharedFile(
            file_handle=open(full_filename, 'rb'),
            file_info=FileInfo(
                id=file_id,
                mimetype=mimetypes.guess_type(full_filename)[0],
                filename=filename,
                date=self._datetime_from_path(full_filename),
                size=os.path.getsize(full_filename)
            )
        )

    def _build_file_info(self, file_id: str, filename: str, namespace: str):
        full_filename = self._path(namespace, filename)
        return FileInfo(
            id=file_id,
            mimetype=mimetypes.guess_type(full_filename)[0],
            filename=filename,
            date=self._datetime_from_path(full_filename),
            size=os.path.getsize(full_filename)
        )

    def _get_namespace_files(self, namespace: str) -> dict[str, str]:
        items = sorted(glob.glob('*', root_dir=self._path(namespace)), key=lambda x: os.path.getmtime(self._path(namespace, x)))
        return OrderedDict((self.hasher.hash(item), item) for item in items)

    def _datetime_from_path(self, path: Path):
        return datetime.fromtimestamp(os.path.getmtime(path), timezone.utc)

    def _path(self, *path_parts: str):
        path = self.base_path.joinpath(*path_parts).resolve()
        if path.is_relative_to(self.base_path):
            return path
        else:
            raise InputError

    def _assert_permissions(self):
        if not Config.is_filesystem_mode_enabled(self.plugin):
            raise InputError

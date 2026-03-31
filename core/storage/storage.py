import glob
import logging
import mimetypes
import os
import shutil
import tempfile
import threading
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from core.config import Config
from core.exceptions import InputError
from core.plugin.plugin import Plugin
from core.storage.hasher import Hasher
from core.storage.files import SharedFile, FileInfo

logger = logging.getLogger(__name__)

DOWNLOADING_EXTENSION = ".downloading"


class Storage:
    def __init__(self, plugin: Plugin):
        self.base_path = Path("storage").joinpath(plugin.plugin_name).resolve()
        self.hasher = Hasher()
        self.plugin = plugin

    def list_items(self, namespace: str) -> list[FileInfo]:
        self._assert_permissions()
        return [
            self._build_file_info(file_id, filename, namespace)
            for file_id, filename in self._get_namespace_files(namespace).items()
        ]

    def serve(self, namespace: str, file_id: str) -> SharedFile:
        """Serve a file from storage by its file_id (hash of filename)."""
        self._assert_permissions()
        try:
            filename = self._get_namespace_files(namespace)[file_id]
        except KeyError:
            raise InputError(f"File not found: {namespace}:{file_id}")
        full_filename = self._path(namespace, filename)
        return SharedFile(
            file_handle=open(full_filename, "rb"),
            file_info=FileInfo(
                id=file_id,
                mimetype=mimetypes.guess_type(full_filename)[0],
                filename=filename,
                date=self._datetime_from_path(full_filename),
                size=os.path.getsize(full_filename),
            ),
        )

    def find_stored_id(self, namespace: str, item_id: str) -> str | None:
        """Check if a completed download exists for the given item.
        Returns the file_id (usable with serve()) if found, None otherwise.

        Supports two lookup modes:
        - Hash-based: files stored via store() are named hash(item_id).ext,
          so we look for files whose stem matches hash(item_id).
        - Direct file_id: for pre-existing files (e.g. filesystem plugin),
          item_id may already be a file_id (hash of filename). We check if
          item_id is a known key in the namespace file listing.
        """
        self._assert_permissions()
        hashed = self.hasher.hash(item_id)
        try:
            namespace_path = self._path(namespace)
        except InputError:
            return None
        if not namespace_path.exists():
            return None
        # Hash-based lookup: files stored via store() have stem == hash(item_id)
        for filename in os.listdir(namespace_path):
            path = namespace_path / filename
            stem, suffix = os.path.splitext(filename)
            if path.is_file() and stem == hashed and suffix != DOWNLOADING_EXTENSION:
                return self.hasher.hash(filename)
        # Direct file_id lookup: item_id may already be a file_id (hash of filename)
        namespace_files = self._get_namespace_files(namespace)
        if item_id in namespace_files:
            return item_id
        return None

    def is_downloading(self, namespace: str, item_id: str) -> bool:
        """Check if a download is in progress for the given item."""
        self._assert_permissions()
        marker = self._downloading_marker_path(namespace, item_id)
        return marker.exists()

    def request_download(
        self, namespace: str, item_id: str, download_fn: Callable[[str], None]
    ) -> None:
        """Trigger a background download if the item is not already stored or downloading."""
        self._assert_permissions()
        if self.find_stored_id(namespace, item_id) is not None or self.is_downloading(
            namespace, item_id
        ):
            return

        namespace_path = self._path(namespace)
        namespace_path.mkdir(parents=True, exist_ok=True)

        marker = self._downloading_marker_path(namespace, item_id)
        marker.touch()

        temp_dir = tempfile.mkdtemp()
        thread = threading.Thread(
            target=self._run_download,
            args=(namespace, item_id, temp_dir, download_fn),
            daemon=True,
        )
        thread.start()

    def store(self, namespace: str, item_id: str, source_path: str) -> Path:
        """Move a file from source_path into the storage namespace with a deterministic name."""
        self._assert_permissions()
        namespace_path = self._path(namespace)
        namespace_path.mkdir(parents=True, exist_ok=True)

        source = Path(source_path)
        extension = source.suffix
        hashed_name = self.hasher.hash(item_id) + extension
        dest = self._path(namespace, hashed_name)
        shutil.move(str(source), str(dest))
        return dest

    def _run_download(
        self,
        namespace: str,
        item_id: str,
        temp_dir: str,
        download_fn: Callable[[str], None],
    ) -> None:
        """Execute the download function in a background thread and move the result to storage."""
        try:
            download_fn(temp_dir)
            output_file = self._find_download_output(temp_dir)
            if output_file is None:
                logger.error("Download produced no output file for item %s", item_id)
                return
            self.store(namespace, item_id, str(output_file))
        except Exception:
            logger.exception("Background download failed for item %s", item_id)
        finally:
            marker = self._downloading_marker_path(namespace, item_id)
            if marker.exists():
                marker.unlink()
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _find_download_output(self, temp_dir: str) -> Path | None:
        """Find the output file in the temp directory. Returns the largest file if multiple exist."""
        files = [
            p
            for p in Path(temp_dir).iterdir()
            if p.is_file() and not p.name.startswith(".")
        ]
        if not files:
            return None
        return max(files, key=lambda p: p.stat().st_size)

    def _downloading_marker_path(self, namespace: str, item_id: str) -> Path:
        """Return the path for the .downloading marker file."""
        hashed = self.hasher.hash(item_id)
        namespace_path = self._path(namespace)
        namespace_path.mkdir(parents=True, exist_ok=True)
        return self._path(namespace, hashed + DOWNLOADING_EXTENSION)

    def _build_file_info(self, file_id: str, filename: str, namespace: str):
        full_filename = self._path(namespace, filename)
        return FileInfo(
            id=file_id,
            mimetype=mimetypes.guess_type(full_filename)[0],
            filename=filename,
            date=self._datetime_from_path(full_filename),
            size=os.path.getsize(full_filename),
        )

    def _get_namespace_files(self, namespace: str) -> dict[str, str]:
        items = sorted(
            glob.glob("*", root_dir=self._path(namespace)),
            key=lambda x: os.path.getmtime(self._path(namespace, x)),
        )
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

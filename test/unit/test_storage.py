import os
import shutil
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.storage.storage import Storage


@pytest.fixture
def mock_plugin():
    plugin = MagicMock()
    plugin.plugin_name = "test_plugin"
    plugin.supports_fs_mode = True
    plugin.default_fs_mode_enabled = True
    return plugin


@pytest.fixture
def storage_dir(tmp_path):
    """Override the storage base path to use a temp directory."""
    return tmp_path


@pytest.fixture
def storage(mock_plugin, storage_dir, monkeypatch):
    """Create a Storage instance with a temp-dir-based base path."""
    monkeypatch.setattr(
        "core.config.Config.is_filesystem_mode_enabled", lambda self_or_plugin: True
    )
    s = Storage(mock_plugin)
    s.base_path = storage_dir
    return s


class TestIsStored:
    def test_not_stored_when_empty(self, storage):
        assert storage.is_stored("ns", "item1") is False

    def test_not_stored_when_namespace_missing(self, storage):
        assert storage.is_stored("nonexistent", "item1") is False

    def test_stored_when_file_exists(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        (ns_dir / f"{hashed}.mp4").write_text("content")

        assert storage.is_stored("ns", "item1") is True

    def test_not_stored_when_only_downloading_marker(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        (ns_dir / f"{hashed}.downloading").touch()

        assert storage.is_stored("ns", "item1") is False


class TestIsDownloading:
    def test_not_downloading_when_empty(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        assert storage.is_downloading("ns", "item1") is False

    def test_downloading_when_marker_exists(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        (ns_dir / f"{hashed}.downloading").touch()

        assert storage.is_downloading("ns", "item1") is True

    def test_not_downloading_when_complete(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        (ns_dir / f"{hashed}.mp4").write_text("content")

        assert storage.is_downloading("ns", "item1") is False


class TestStore:
    def test_store_moves_file(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()

        source = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        source.write(b"video data")
        source.close()

        try:
            dest = storage.store("ns", "item1", source.name)
            hashed = storage.hasher.hash("item1")
            assert dest.name == f"{hashed}.mp4"
            assert dest.exists()
            assert dest.read_bytes() == b"video data"
            assert not Path(source.name).exists()  # moved, not copied
        finally:
            if Path(source.name).exists():
                os.unlink(source.name)

    def test_store_creates_namespace_dir(self, storage, storage_dir):
        source = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
        source.write(b"data")
        source.close()

        try:
            dest = storage.store("new_ns", "item1", source.name)
            assert (storage_dir / "new_ns").is_dir()
            assert dest.exists()
        finally:
            if Path(source.name).exists():
                os.unlink(source.name)


class TestServeByItemId:
    def test_serve_existing_file(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        file_path = ns_dir / f"{hashed}.mp4"
        file_path.write_bytes(b"video content")

        shared_file = storage.serve_by_item_id("ns", "item1")
        try:
            assert shared_file.file_info.id == hashed
            assert shared_file.file_info.filename == f"{hashed}.mp4"
            assert shared_file.file_info.size == len(b"video content")
            assert shared_file.file_handle.read() == b"video content"
        finally:
            shared_file.close()

    def test_serve_nonexistent_raises(self, storage, storage_dir):
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()

        from core.exceptions import InputError

        with pytest.raises(InputError):
            storage.serve_by_item_id("ns", "nonexistent")


class TestRequestDownload:
    def test_download_creates_file(self, storage, storage_dir):
        """Test that request_download runs download_fn and stores the result."""

        def download_fn(temp_dir):
            with open(os.path.join(temp_dir, "output.mp4"), "wb") as f:
                f.write(b"downloaded video")

        storage.request_download("ns", "item1", download_fn)

        # Wait for the background thread to complete
        for _ in range(50):
            if storage.is_stored("ns", "item1"):
                break
            time.sleep(0.1)

        assert storage.is_stored("ns", "item1") is True
        assert storage.is_downloading("ns", "item1") is False

        shared = storage.serve_by_item_id("ns", "item1")
        try:
            assert shared.file_handle.read() == b"downloaded video"
        finally:
            shared.close()

    def test_download_sets_marker_during_download(self, storage, storage_dir):
        """Test that a .downloading marker exists while download is in progress."""
        download_started = threading.Event()
        download_proceed = threading.Event()

        def slow_download_fn(temp_dir):
            download_started.set()
            download_proceed.wait(timeout=5)
            with open(os.path.join(temp_dir, "output.mp4"), "wb") as f:
                f.write(b"data")

        storage.request_download("ns", "item1", slow_download_fn)
        download_started.wait(timeout=5)

        assert storage.is_downloading("ns", "item1") is True
        assert storage.is_stored("ns", "item1") is False

        download_proceed.set()
        for _ in range(50):
            if not storage.is_downloading("ns", "item1"):
                break
            time.sleep(0.1)

        assert storage.is_downloading("ns", "item1") is False
        assert storage.is_stored("ns", "item1") is True

    def test_noop_if_already_stored(self, storage, storage_dir):
        """Test that request_download is a no-op if file is already stored."""
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        (ns_dir / f"{hashed}.mp4").write_bytes(b"existing")

        download_called = threading.Event()

        def download_fn(temp_dir):
            download_called.set()

        storage.request_download("ns", "item1", download_fn)
        time.sleep(0.3)

        assert not download_called.is_set()

    def test_noop_if_already_downloading(self, storage, storage_dir):
        """Test that request_download is a no-op if download is in progress."""
        ns_dir = storage_dir / "ns"
        ns_dir.mkdir()
        hashed = storage.hasher.hash("item1")
        (ns_dir / f"{hashed}.downloading").touch()

        download_called = threading.Event()

        def download_fn(temp_dir):
            download_called.set()

        storage.request_download("ns", "item1", download_fn)
        time.sleep(0.3)

        assert not download_called.is_set()

    def test_download_cleans_up_on_failure(self, storage, storage_dir):
        """Test that marker and temp dir are cleaned up when download fails."""

        def failing_download_fn(temp_dir):
            raise RuntimeError("download failed")

        storage.request_download("ns", "item1", failing_download_fn)

        for _ in range(50):
            if not storage.is_downloading("ns", "item1"):
                break
            time.sleep(0.1)

        assert storage.is_downloading("ns", "item1") is False
        assert storage.is_stored("ns", "item1") is False

    def test_download_cleans_up_when_no_output(self, storage, storage_dir):
        """Test cleanup when download_fn produces no output file."""

        def empty_download_fn(temp_dir):
            pass  # writes nothing

        storage.request_download("ns", "item1", empty_download_fn)

        for _ in range(50):
            if not storage.is_downloading("ns", "item1"):
                break
            time.sleep(0.1)

        assert storage.is_downloading("ns", "item1") is False
        assert storage.is_stored("ns", "item1") is False


class TestPathSecurity:
    def test_path_traversal_rejected_on_store(self, storage, storage_dir):
        """Storing with a traversal namespace must raise InputError."""
        from core.exceptions import InputError
        import tempfile

        source = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        source.write(b"data")
        source.close()
        try:
            with pytest.raises(InputError):
                storage.store("../../etc", "item1", source.name)
        finally:
            if Path(source.name).exists():
                os.unlink(source.name)

    def test_serve_path_traversal_rejected(self, storage, storage_dir):
        """Serving with a traversal namespace must raise InputError."""
        from core.exceptions import InputError

        with pytest.raises(InputError):
            storage.serve("../../etc", "file_id")

    def test_list_items_path_traversal_rejected(self, storage, storage_dir):
        """Listing items with a traversal namespace must raise InputError."""
        from core.exceptions import InputError

        with pytest.raises(InputError):
            storage.list_items("../../etc")

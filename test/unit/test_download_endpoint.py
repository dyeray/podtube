import os
import threading
import time
from unittest.mock import patch, MagicMock

import pytest

from main import app
from core.storage.hasher import Hasher


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def storage_dir(tmp_path):
    return tmp_path


@pytest.fixture
def hasher():
    return Hasher()


class TestDownloadWithFilesystemMode:
    """Test the /download endpoint with filesystem mode enabled for non-filesystem plugins."""

    def test_returns_202_and_triggers_download(self, client, storage_dir, hasher):
        """First request for an uncached video returns 202 and starts download."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "youtube"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = False
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}

        download_called = threading.Event()

        def fake_download_fn(item_id):
            def download(temp_dir):
                download_called.set()
                with open(os.path.join(temp_dir, "video.mp4"), "wb") as f:
                    f.write(b"fake video")

            return download

        mock_plugin.get_download_fn = fake_download_fn

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
            patch(
                "core.storage.storage.Config.is_filesystem_mode_enabled",
                return_value=True,
            ),
            patch.object(
                __import__("core.storage.storage", fromlist=["Storage"]).Storage,
                "__init__",
                lambda self, plugin: setattr(self, "base_path", storage_dir)
                or setattr(self, "hasher", hasher)
                or setattr(self, "plugin", plugin),
            ),
        ):
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest")

            assert resp.status_code == 202
            assert resp.headers.get("Retry-After") == "30"

            # Wait for background download to complete
            download_called.wait(timeout=5)
            time.sleep(0.5)

    def test_serves_file_when_cached(self, client, storage_dir, hasher):
        """Request for an already-cached video returns 200 with file content."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "youtube"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = False
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}

        # Pre-populate storage with a cached file
        ns_dir = storage_dir / "UCtest"
        ns_dir.mkdir()
        hashed = hasher.hash("dQw4w9WgXcQ")
        (ns_dir / f"{hashed}.mp4").write_bytes(b"cached video content")

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
            patch(
                "core.storage.storage.Config.is_filesystem_mode_enabled",
                return_value=True,
            ),
            patch.object(
                __import__("core.storage.storage", fromlist=["Storage"]).Storage,
                "__init__",
                lambda self, plugin: setattr(self, "base_path", storage_dir)
                or setattr(self, "hasher", hasher)
                or setattr(self, "plugin", plugin),
            ),
        ):
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest")

            assert resp.status_code == 200
            assert resp.data == b"cached video content"
            assert "video/mp4" in resp.content_type

    def test_returns_202_when_downloading(self, client, storage_dir, hasher):
        """Request for a video that is currently downloading returns 202."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "youtube"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = False
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}

        # Create a .downloading marker
        ns_dir = storage_dir / "UCtest"
        ns_dir.mkdir()
        hashed = hasher.hash("dQw4w9WgXcQ")
        (ns_dir / f"{hashed}.downloading").touch()

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
            patch(
                "core.storage.storage.Config.is_filesystem_mode_enabled",
                return_value=True,
            ),
            patch.object(
                __import__("core.storage.storage", fromlist=["Storage"]).Storage,
                "__init__",
                lambda self, plugin: setattr(self, "base_path", storage_dir)
                or setattr(self, "hasher", hasher)
                or setattr(self, "plugin", plugin),
            ),
        ):
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest")

            assert resp.status_code == 202
            assert resp.headers.get("Retry-After") == "30"

    def test_returns_400_when_no_feed_id(self, client):
        """Request without feed_id returns 400."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "youtube"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = False
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
        ):
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ")

            assert resp.status_code == 400

    def test_redirects_when_no_download_fn(self, client, storage_dir, hasher):
        """Plugin without get_download_fn falls back to redirect."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "youtube"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = False
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}
        mock_plugin.get_download_fn.return_value = None
        mock_plugin.get_item_url.return_value = "https://example.com/video.mp4"

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
            patch(
                "core.storage.storage.Config.is_filesystem_mode_enabled",
                return_value=True,
            ),
            patch.object(
                __import__("core.storage.storage", fromlist=["Storage"]).Storage,
                "__init__",
                lambda self, plugin: setattr(self, "base_path", storage_dir)
                or setattr(self, "hasher", hasher)
                or setattr(self, "plugin", plugin),
            ),
        ):
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest")

            assert resp.status_code == 302
            assert "example.com/video.mp4" in resp.headers["Location"]

    def test_filesystem_plugin_unchanged(self, client, storage_dir, hasher):
        """The filesystem plugin still uses the original namespace:file_id format."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "filesystem"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = True
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}

        # Pre-populate storage with a file
        ns_dir = storage_dir / "myns"
        ns_dir.mkdir()
        test_file = ns_dir / "test_audio.mp3"
        test_file.write_bytes(b"audio data")
        file_hash = hasher.hash("test_audio.mp3")

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
            patch(
                "core.storage.storage.Config.is_filesystem_mode_enabled",
                return_value=True,
            ),
            patch.object(
                __import__("core.storage.storage", fromlist=["Storage"]).Storage,
                "__init__",
                lambda self, plugin: setattr(self, "base_path", storage_dir)
                or setattr(self, "hasher", hasher)
                or setattr(self, "plugin", plugin),
            ),
        ):
            resp = client.get(f"/download?plugin=filesystem&id=myns:{file_hash}")

            assert resp.status_code == 200
            assert resp.data == b"audio data"

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
    with patch("core.auth.Config.get_required_api_key", return_value=None):
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
            resp = client.get(
                "/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest&storage=true"
            )

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
            resp = client.get(
                "/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest&storage=true"
            )

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
            resp = client.get(
                "/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest&storage=true"
            )

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
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ&storage=true")

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
            resp = client.get(
                "/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest&storage=true"
            )

            assert resp.status_code == 302
            assert "example.com/video.mp4" in resp.headers["Location"]

    def test_filesystem_plugin_serves_pre_existing_file(
        self, client, storage_dir, hasher
    ):
        """The filesystem plugin serves pre-existing files through the unified storage path."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "filesystem"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = True
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}

        # Pre-populate storage with a file (original name, not hash-named)
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
            resp = client.get(
                f"/download?plugin=filesystem&id={file_hash}&feed_id=myns&storage=true"
            )

            assert resp.status_code == 200
            assert resp.data == b"audio data"

    def test_redirects_when_storage_not_requested(self, client):
        """When server allows storage mode but the feed does not request it, redirect."""
        mock_plugin = MagicMock()
        mock_plugin.plugin_name = "youtube"
        mock_plugin.supports_fs_mode = True
        mock_plugin.default_fs_mode_enabled = False
        mock_plugin.options = MagicMock()
        mock_plugin.options.model_dump.return_value = {}
        mock_plugin.get_item_url.return_value = "https://example.com/video.mp4"

        with (
            patch("main.PluginFactory.create", return_value=mock_plugin),
            patch("main.Config.is_filesystem_mode_enabled", return_value=True),
        ):
            resp = client.get("/download?plugin=youtube&id=dQw4w9WgXcQ&feed_id=UCtest")

            assert resp.status_code == 302
            assert "example.com/video.mp4" in resp.headers["Location"]


class TestYoutubeSubtitles:
    """Test that the YouTube plugin configures yt-dlp subtitle options correctly."""

    def test_download_fn_includes_subtitle_opts_when_set(self):
        """When subtitles=en is set, get_download_fn produces yt-dlp opts with subtitle config
        and registers FFmpegBurnSubtitlePP."""
        from plugins.youtube import PluginImpl, FFmpegBurnSubtitlePP

        plugin = PluginImpl({"subtitles": "en"})
        download_fn = plugin.get_download_fn("test_id")
        assert download_fn is not None

        captured_opts = {}
        added_pps = []

        def mock_ytdl_init(self_ydl, opts):
            captured_opts.update(opts)

        def mock_add_pp(self_ydl, pp, when="post_process"):
            added_pps.append(pp)

        with (
            patch("plugins.youtube.YoutubeDL.__init__", mock_ytdl_init),
            patch("plugins.youtube.YoutubeDL.__enter__", lambda self: self),
            patch("plugins.youtube.YoutubeDL.__exit__", lambda *a: None),
            patch("plugins.youtube.YoutubeDL.download", lambda self, urls: None),
            patch("plugins.youtube.YoutubeDL.add_post_processor", mock_add_pp),
        ):
            download_fn("/tmp/test")

        assert captured_opts["writesubtitles"] is True
        assert captured_opts["writeautomaticsub"] is True
        assert captured_opts["subtitleslangs"] == ["en"]
        assert "postprocessors" not in captured_opts
        assert len(added_pps) == 1
        assert isinstance(added_pps[0], FFmpegBurnSubtitlePP)

    def test_download_fn_no_subtitle_opts_when_not_set(self):
        """When subtitles is not set, get_download_fn does not include subtitle config."""
        from plugins.youtube import PluginImpl

        plugin = PluginImpl({})
        download_fn = plugin.get_download_fn("test_id")
        assert download_fn is not None

        captured_opts = {}
        added_pps = []

        def mock_ytdl_init(self_ydl, opts):
            captured_opts.update(opts)

        def mock_add_pp(self_ydl, pp, when="post_process"):
            added_pps.append(pp)

        with (
            patch("plugins.youtube.YoutubeDL.__init__", mock_ytdl_init),
            patch("plugins.youtube.YoutubeDL.__enter__", lambda self: self),
            patch("plugins.youtube.YoutubeDL.__exit__", lambda *a: None),
            patch("plugins.youtube.YoutubeDL.download", lambda self, urls: None),
            patch("plugins.youtube.YoutubeDL.add_post_processor", mock_add_pp),
        ):
            download_fn("/tmp/test")

        assert "writesubtitles" not in captured_opts
        assert "writeautomaticsub" not in captured_opts
        assert "subtitleslangs" not in captured_opts
        assert "postprocessors" not in captured_opts
        assert len(added_pps) == 0

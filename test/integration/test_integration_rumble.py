from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from core.exceptions import PluginError
from plugins.rumble import PluginImpl


def test_get_feed_scrapes_channel_page(utils, httpx_mock):
    channel_id = "JOHNMH82"
    channel_url = f"https://rumble.com/user/{channel_id}/videos"
    httpx_mock.add_response(
        method="GET",
        url=channel_url,
        content=utils.get_fixture("rumble.html"),
        status_code=200,
    )

    feed = PluginImpl({}).get_feed(channel_id)

    assert feed.feed_id == channel_id
    assert feed.link == channel_url
    assert feed.title == "JOHNMH82"
    assert feed.description == "JOHNMH82's videos on Rumble.com"
    assert feed.image == "https://hugh.cdn.rumble.cloud/video/channel.jpeg"
    assert len(feed.items) == 2
    assert feed.items[0].item_id == (
        "aHR0cHM6Ly9ydW1ibGUuY29tL3YxMjNhYmMtc2FtcGxlLXZpZGVvLmh0bWw"
    )
    assert feed.items[0].title == "Sample video"
    assert feed.items[0].description == feed.items[0].title
    assert feed.items[0].link == (
        "https://rumble.com/v123abc-sample-video.html"
    )
    assert feed.items[0].date.isoformat() == "2026-09-02T14:15:26+00:00"
    assert feed.items[0].image == "https://hugh.cdn.rumble.cloud/video/first.jpg"
    assert feed.items[0].content_type == "video/mp4"


def test_get_item_url_resolves_video_page_with_ytdlp():
    downloader = MagicMock()
    downloader.extract_info.return_value = {"url": "https://media.example/video.mp4"}

    with patch.object(
        PluginImpl, "downloader", new_callable=PropertyMock, return_value=downloader
    ):
        result = PluginImpl({}).get_item_url(
            "aHR0cHM6Ly9ydW1ibGUuY29tL3YxMjNhYmMtc2FtcGxlLXZpZGVvLmh0bWw"
        )

    assert result == "https://media.example/video.mp4"
    downloader.extract_info.assert_called_once_with(
        "https://rumble.com/v123abc-sample-video.html",
        download=False,
    )


def test_get_item_url_wraps_ytdlp_errors():
    downloader = MagicMock()
    downloader.extract_info.side_effect = RuntimeError("extract failed")

    with patch.object(
        PluginImpl, "downloader", new_callable=PropertyMock, return_value=downloader
    ), pytest.raises(PluginError):
        PluginImpl({}).get_item_url(
            "aHR0cHM6Ly9ydW1ibGUuY29tL3YxMjNhYmMtc2FtcGxlLXZpZGVvLmh0bWw"
        )


def test_get_item_url_rejects_non_rumble_urls():
    downloader = MagicMock()
    downloader.extract_info.return_value = {"url": "https://media.example/video.mp4"}

    with patch.object(
        PluginImpl, "downloader", new_callable=PropertyMock, return_value=downloader
    ), pytest.raises(PluginError):
        PluginImpl({}).get_item_url("aHR0cDovLzEyNy4wLjAuMS9wcml2YXRl")

    downloader.extract_info.assert_not_called()


def test_get_item_url_rejects_rumble_channel_urls():
    downloader = MagicMock()

    with patch.object(
        PluginImpl, "downloader", new_callable=PropertyMock, return_value=downloader
    ), pytest.raises(PluginError):
        PluginImpl({}).get_item_url(
            "aHR0cHM6Ly9ydW1ibGUuY29tL3VzZXIvSk9ITk1IODIvdmlkZW9z"
        )

    downloader.extract_info.assert_not_called()

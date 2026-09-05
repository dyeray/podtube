from datetime import datetime
from typing import Callable, List, Literal, Optional
import os

import httpx
from parsel import Selector, SelectorList
from yt_dlp import YoutubeDL
from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor
from yt_dlp.utils import prepend_extension

from core.model import PodcastItem, PodcastFeed
from core.exceptions import PluginError
from core.options import Options
from core.plugin.plugin import Plugin
from core.plugin.ytdl_logger import Logger
from core.utils import find_first

from pydantic import constr


class FFmpegBurnSubtitlePP(FFmpegPostProcessor):
    """Post-processor that burns (hardcodes) subtitles into the video frames.
    Unlike FFmpegEmbedSubtitle which adds a togglable track, this re-encodes the
    video with the subtitle text rendered directly onto the frames, guaranteeing
    visibility in all players."""

    def run(self, info):
        filename = info["filepath"]
        subtitles = info.get("requested_subtitles")
        if not subtitles:
            self.to_screen("No subtitles to burn in")
            return [], info

        # Get the first (and typically only) subtitle file
        sub_info = next(iter(subtitles.values()))
        sub_filepath = sub_info.get("filepath", "")
        if not os.path.exists(sub_filepath):
            self.report_warning(f"Subtitle file not found: {sub_filepath}")
            return [], info

        temp_filename = prepend_extension(filename, "temp")
        # Escape special characters in the subtitle path for FFmpeg filter syntax
        escaped_path = (
            sub_filepath.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")
        )
        self.to_screen(f'Burning subtitles into "{filename}"')
        self.run_ffmpeg(
            filename,
            temp_filename,
            [
                "-map",
                "0",
                "-dn",
                "-ignore_unknown",
                "-c:a",
                "copy",
                "-vf",
                f"subtitles='{escaped_path}'",
            ],
        )
        os.replace(temp_filename, filename)
        return [sub_filepath], info


class PluginImpl(Plugin):
    service = "youtube.com"
    supports_fs_mode = True
    default_fs_mode_enabled = True

    class PluginOptions(Options):
        feed_type: Literal["channel", "playlist"] = "channel"
        subtitles: Optional[constr(pattern=r"^[a-z]{2,3}$")] = None

    namespace_map = {
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
        "atom": "http://www.w3.org/2005/Atom",  # Assigning a prefix to the default namespace
    }

    @property
    def downloader(self):
        return YoutubeDL(
            {
                "format": "best[protocol=https]/best[protocol=http]",
                "extractor_args": {"youtube": {"player_client": ["mweb"]}},
                "logger": Logger(),
            }
        )

    @property
    def info_extractor(self):
        return YoutubeDL({"playlist_items": "0", "logger": Logger()})

    def get_feed(self, feed_id):
        response = httpx.get(
            f"https://www.youtube.com/feeds/videos.xml?{self.options.feed_type}_id={feed_id}"
        )
        if self.options.feed_type == "channel":
            metadata = self.info_extractor.extract_info(
                f"https://www.youtube.com/channel/{feed_id}", download=False
            )
            profile_info = find_first(
                metadata["thumbnails"], lambda x: x["id"] == "avatar_uncropped"
            ) or find_first(metadata["thumbnails"])
            feed_url = profile_info and profile_info["url"]
        else:
            feed_url = None

        sel = Selector(response.text, type="xml")
        entries = sel.xpath("//atom:feed/atom:entry", namespaces=self.namespace_map)
        title = sel.xpath(
            "//atom:feed/atom:title/text()", namespaces=self.namespace_map
        ).get()
        return PodcastFeed(
            feed_id=feed_id,
            title=title,
            description=title,
            link=f"https://www.youtube.com/channel/{feed_id}",
            image=feed_url,
            items=self._get_items(entries),
        )

    def get_item_url(self, item_id):
        try:
            return self.downloader.extract_info(
                f"https://www.youtube.com/watch?v={item_id}", download=False
            )["url"]
        except Exception as ex:
            raise PluginError(ex)

    def get_download_fn(self, item_id: str) -> Callable[[str], None] | None:
        subtitles_lang = self.options.subtitles

        def download(temp_dir: str) -> None:
            ydl_opts = {
                "format": "best[protocol=https]/best[protocol=http]",
                "extractor_args": {"youtube": {"player_client": ["mweb"]}},
                "logger": Logger(),
                "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
            }
            if subtitles_lang:
                ydl_opts["writesubtitles"] = True
                ydl_opts["writeautomaticsub"] = True
                ydl_opts["subtitleslangs"] = [subtitles_lang]
            with YoutubeDL(ydl_opts) as ydl:
                if subtitles_lang:
                    ydl.add_post_processor(FFmpegBurnSubtitlePP())
                ydl.download([f"https://www.youtube.com/watch?v={item_id}"])

        return download

    def _get_items(self, entries: SelectorList) -> List[PodcastItem]:
        return [self._get_item(entry) for entry in entries]

    def _get_item(self, entry: Selector):
        video_id = entry.xpath("yt:videoId/text()", namespaces=self.namespace_map).get()
        return PodcastItem(
            item_id=video_id,
            title=entry.xpath("atom:title/text()", namespaces=self.namespace_map).get(),
            description=entry.xpath(
                "media:group/media:description/text()", namespaces=self.namespace_map
            ).get(),
            link=f"https://www.youtube.com/watch?v={video_id}",
            date=datetime.fromisoformat(
                entry.xpath(
                    "atom:published/text()", namespaces=self.namespace_map
                ).get()
            ),
            image=entry.xpath(
                "media:group/media:thumbnail/@url", namespaces=self.namespace_map
            ).get(),
            content_type="video/mp4",
        )

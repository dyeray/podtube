from core.model import PodcastItem, PodcastFeed
from core.plugin.plugin import Plugin
from core.storage.files import FileInfo
from core.storage.storage import Storage


class PluginImpl(Plugin):
    supports_fs_mode = True
    default_fs_mode_enabled = True

    def __init__(self, options):
        super().__init__(options)
        self.storage = Storage(self)

    def get_feed(self, feed_id):
        items = self.storage.list_items(feed_id)

        return PodcastFeed(
            feed_id=feed_id,
            title=feed_id,
            description=feed_id,
            link="https://github.com/dyeray/podtube/",
            image="",
            items=self._get_items(feed_id, items),
        )

    def get_item_url(self, item_id):
        raise NotImplementedError()

    def _get_items(self, feed_id: str, items: list[FileInfo]) -> list[PodcastItem]:
        return [self._get_item(feed_id, item) for item in items]

    def _get_item(self, feed_id: str, item: FileInfo):
        return PodcastItem(
            item_id=f'{feed_id}:{item.id}',
            title=item.filename.split(".")[0],
            description="",
            link="",
            date=item.date,
            image=None,
            content_type=item.mimetype or "",
            content_length=str(item.size)
        )

from hashlib import md5
from typing import List

import dateparser
import feedparser

from core.model import PodcastFeed, PodcastItem
from core.service.service import Service
from core.utils import first
from core.scrape_utils import clean_image_url


class ServiceImpl(Service):
    def get_feed(self, feed_id):
        """Calculates and returns the subscribable feed."""
        parsed_dict = feedparser.parse(feed_id)
        image = parsed_dict.feed.image
        return PodcastFeed(
            feed_id=md5(feed_id.encode()).digest().hex(),
            title=parsed_dict.feed.title,
            description=parsed_dict.feed.description,
            link=feed_id,
            image=image and clean_image_url(image.href),
            items=self._get_items(parsed_dict.entries)
        )

    def _get_items(self, items) -> List[PodcastItem]:
        return [self._get_item(item) for item in items]

    def _get_item(self, item) -> PodcastItem:
        enclosure = first(item.enclosures)
        image = item.image
        return PodcastItem(
            item_id=enclosure and enclosure.href,
            title=item.title,
            description=item.description,
            date=dateparser.parse(item.published),
            image=image and clean_image_url(image.href),
            content_type=enclosure and enclosure.type,
        )

    def get_item_url(self, item_id):
        return item_id

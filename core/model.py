from dataclasses import dataclass
from datetime import datetime


@dataclass
class PodcastItem:
    item_id: str
    title: str
    description: str
    date: datetime
    image: str
    content_type: str
    content_length: str | None = None


@dataclass
class PodcastFeed:
    title: str
    description: str
    link: str
    image: str
    items: list[PodcastItem]
    feed_id: str

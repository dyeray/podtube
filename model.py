from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class PodcastItem:
    item_id: str
    title: str
    description: str
    date: datetime
    image: str
    url: str
    content_length: str
    content_type: str


@dataclass
class PodcastFeed:
    title: str
    description: str
    link: str
    image: str
    items: List[PodcastItem]
    feed_id: str

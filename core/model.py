from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PodcastItem:
    item_id: str
    title: str
    description: str
    date: datetime
    image: str
    url: str
    content_type: str
    content_length: Optional[str] = None


@dataclass
class PodcastFeed:
    title: str
    description: str
    link: str
    image: str
    items: List[PodcastItem]
    feed_id: str

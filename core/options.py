from enum import Enum

from pydantic import BaseModel

Options = BaseModel


class FeedFormat(str, Enum):
    rss = 'rss'
    atom = 'atom'


class GlobalOptions(Options):
    service: str
    id: str
    format: FeedFormat = 'rss'
    proxy_url: bool = True
    proxy_download: bool = False
    icon: str = None


class Choice(str, Enum):
    pass

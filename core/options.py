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
    proxy_url = True
    proxy_download = False


class Choice(str, Enum):
    pass

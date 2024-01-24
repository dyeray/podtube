from enum import Enum

from pydantic import BaseModel, constr, HttpUrl


class Options(BaseModel):
    pass


class FeedFormat(str, Enum):
    rss = 'rss'
    atom = 'atom'


class GlobalOptions(Options):
    service: constr(pattern=r'^[a-z]+$')
    id: constr(pattern=r'^[a-zA-Z0-9_-]+$')
    format: FeedFormat = 'rss'
    proxy_url: bool = True
    proxy_download: bool = False
    icon: HttpUrl | None = None


class Choice(str, Enum):
    pass

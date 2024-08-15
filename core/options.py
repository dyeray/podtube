from typing import Literal

from pydantic import BaseModel, constr, HttpUrl


class Options(BaseModel):
    pass


class GlobalOptions(Options):
    service: constr(pattern=r"^[a-z]+$")
    id: constr(pattern=r"^[a-zA-Z0-9_-]+$")
    format: Literal["rss", "atom"] = "rss"
    proxy_url: bool = True
    proxy_download: bool = False
    icon: HttpUrl | None = None

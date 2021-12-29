from pydantic import BaseModel


class Options(BaseModel):
    service: str
    id: str
    format = 'rss'
    proxy_url = True
    proxy_download = False

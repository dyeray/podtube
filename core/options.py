from pydantic import BaseModel

Options = BaseModel


class GlobalOptions(Options):
    service: str
    id: str
    format = 'rss'
    proxy_url = True
    proxy_download = False

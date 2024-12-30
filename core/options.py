from typing import Literal, Optional

from pydantic import BaseModel, constr, HttpUrl, model_validator


class Options(BaseModel):
    pass


class GlobalOptions(Options):
    service: Optional[constr(pattern=r"^[a-z.]+$")] = None
    plugin: Optional[constr(pattern=r"^[a-z]+$")] = None
    id: constr(pattern=r"^[a-zA-Z0-9_\-:]+$")
    format: Literal["rss", "atom"] = "rss"
    proxy_download: bool = False
    icon: HttpUrl | None = None
    api_key: Optional[constr(pattern=r"^[a-zA-Z0-9]+$")] = None


    @model_validator(mode='after')
    def global_checks(self):
        if self.service is None and self.plugin is None:
            raise ValueError("Either 'service' or 'plugin' need to be defined")
        if self.service is not None and self.plugin is not None:
            raise ValueError("'service' and 'plugin' cannot be defined at the same time")
        return self

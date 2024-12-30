from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO

@dataclass
class FileInfo:
    id: str
    mimetype: str | None
    filename: str
    date: datetime
    size: int

@dataclass
class SharedFile:
    file_handle: BinaryIO
    file_info: FileInfo

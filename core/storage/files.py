from dataclasses import dataclass
from typing import BinaryIO, Optional

@dataclass
class FileInfo:
    id: str
    mimetype: str | None
    filename: str

@dataclass
class SharedFile:
    file_handle: BinaryIO
    file_info: FileInfo

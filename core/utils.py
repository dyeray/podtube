from typing import Iterable, Optional, Callable

from typing import TypeVar

T = TypeVar('T')


def first(iterable: Iterable[T], function: Callable[[T], bool] = lambda x: True) -> Optional[T]:
    for item in iterable:
        if function(item):
            return item
    return None

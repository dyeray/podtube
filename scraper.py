from typing import Union

from parsel import Selector, SelectorList


def extract(selector: Union[SelectorList, Selector]):
    if isinstance(selector, SelectorList):
        text = selector.extract_first() or ''
    else:
        text = selector.extract() or ''
    return text.strip()

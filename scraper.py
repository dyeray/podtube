from typing import Union

from parsel import Selector, SelectorList


def extract(selector: Union[SelectorList, Selector]):
    if isinstance(selector, SelectorList):
        text = selector.extract_first()
    else:
        text = selector.extract()
    return text.strip()

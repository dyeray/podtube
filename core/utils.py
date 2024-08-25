def clean(text: str | None) -> str | None:
    return text.strip() if text else None


def safe_traverse(input_data, *args):
    current = input_data
    for key in args:
        try:
            current = current[key]
        except Exception:
            return None
    return current

def find_first(iterable, function = lambda x: True):
    for item in iterable:
        if function(item):
            return item
    return None

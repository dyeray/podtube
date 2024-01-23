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

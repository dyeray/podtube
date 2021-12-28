def clean(text: str | None) -> str | None:
    return text.strip() if text else None

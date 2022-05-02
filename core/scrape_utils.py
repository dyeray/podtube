import re


def clean(text: str | None) -> str | None:
    return text.strip() if text else None


def clean_image_url(url: str | None) -> str | None:
    if not url:
        return
    if url.endswith('.jpg') or url.endswith('.png'):
        return url
    match = re.match(r'.*url=(.*)\?ts=.*', url)
    return match and match.group(1)

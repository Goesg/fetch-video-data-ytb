import re
from urllib.parse import urlparse, parse_qs

_PLAYLIST_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/.*[?&]list=([A-Za-z0-9_-]+)"
)


def is_valid_playlist_url(url: str) -> bool:
    return bool(_PLAYLIST_PATTERN.match(url))


def extract_playlist_id(url: str) -> str | None:
    match = _PLAYLIST_PATTERN.match(url)
    if match:
        return match.group(1)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    ids = params.get("list")
    return ids[0] if ids else None

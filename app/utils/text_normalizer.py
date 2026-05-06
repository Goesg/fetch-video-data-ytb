import re
import unicodedata

# Suffixes/tags stripped before parsing — order matters (longer patterns first)
_NOISE_PATTERNS = [
    r"\(official\s+(?:music\s+)?(?:video|audio|lyric(?:s)?|visuali[sz]er|clip)\)",
    r"\[official\s+(?:music\s+)?(?:video|audio|lyric(?:s)?|visuali[sz]er|clip)\]",
    r"\((?:official|original)\s+(?:hd\s+)?(?:video|audio)\)",
    r"\[(?:official|original)\s+(?:hd\s+)?(?:video|audio)\]",
    r"\((?:lyrics?|lyric\s+video)\)",
    r"\[(?:lyrics?|lyric\s+video)\]",
    r"\((?:remastered?|remaster)\s*(?:\d{4})?\)",
    r"\[(?:remastered?|remaster)\s*(?:\d{4})?\]",
    r"\((?:hd|hq|4k|1080p|720p)\)",
    r"\[(?:hd|hq|4k|1080p|720p)\]",
    r"\(visuali[sz]er\)",
    r"\[visuali[sz]er\]",
    r"\(audio\)",
    r"\[audio\]",
    r"\(video\)",
    r"\[video\]",
    r"\(explicit\)",
    r"\[explicit\]",
    r"\(extended\s+(?:version|mix)?\)",
    r"\[extended\s+(?:version|mix)?\]",
    r"\(full\s+(?:album|version)\)",
    r"\[full\s+(?:album|version)\]",
    r"\(slowed(?:\s*\+\s*reverb)?\)",
    r"\[slowed(?:\s*\+\s*reverb)?\]",
    r"\(nightcore\)",
    r"\[nightcore\]",
    r"\(sped\s+up\)",
    r"\[sped\s+up\]",
    r"\(topic\)",
    r"\[topic\]",
    r"#\w+",
]

_NOISE_RE = re.compile(
    "|".join(_NOISE_PATTERNS),
    flags=re.IGNORECASE,
)

_WHITESPACE_RE = re.compile(r"\s{2,}")


def normalize_title(title: str) -> str:
    """Return a cleaned, lowercased, whitespace-collapsed version of a title."""
    text = _NOISE_RE.sub("", title)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    text = _strip_unicode_noise(text)
    return text.lower()


def clean_title(title: str) -> str:
    """Remove noise tags but preserve original casing and whitespace structure."""
    text = _NOISE_RE.sub("", title)
    return _WHITESPACE_RE.sub(" ", text).strip()


def _strip_unicode_noise(text: str) -> str:
    # Normalize unicode so lookups work consistently
    return unicodedata.normalize("NFKC", text)

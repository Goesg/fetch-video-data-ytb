"""
Heuristic parser for YouTube video titles.

This is intentionally conservative: when uncertain, it returns null fields
and logs the ambiguity rather than guessing incorrectly.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from app.utils.text_normalizer import clean_title, normalize_title

# Separators that typically divide artist from track
_SEPARATORS = re.compile(r"\s+[-–—|]\s+")

# feat / ft / with / x (collaboration markers)
_FEAT_RE = re.compile(
    r"\s+(?:feat\.?|ft\.?|featuring|with)\s+",
    flags=re.IGNORECASE,
)

# Collaboration via "x" only when surrounded by spaces (avoids matching inside words)
_COLLAB_X_RE = re.compile(r"\s+x\s+", flags=re.IGNORECASE)

# Year: 4-digit number in a realistic music range
_YEAR_RE = re.compile(r"\b((?:19[0-9]{2}|20[0-2][0-9]))\b")

# Patterns that suggest the left side of a separator is artist
# e.g. "Artist - Track" is far more common than "Track - Artist" on YouTube
_ARTIST_FIRST_CONFIDENCE_THRESHOLD = 0.6


@dataclass
class ParsedTitle:
    original_title: str
    cleaned_title: str
    normalized_title: str
    artist: Optional[str]
    track: Optional[str]
    year: Optional[int]
    confidence: str  # "high" | "medium" | "low"
    notes: list[str] = field(default_factory=list)


def parse_title(raw_title: str) -> ParsedTitle:
    """
    Attempt to extract artist and track from a raw YouTube title.
    Returns a ParsedTitle with confidence annotation and notes.
    """
    cleaned = clean_title(raw_title)
    normalized = normalize_title(raw_title)
    notes: list[str] = []

    year = _extract_year(cleaned, notes)
    artist, track, confidence = _split_artist_track(cleaned, notes)

    return ParsedTitle(
        original_title=raw_title,
        cleaned_title=cleaned,
        normalized_title=normalized,
        artist=artist,
        track=track,
        year=year,
        confidence=confidence,
        notes=notes,
    )


def _extract_year(text: str, notes: list[str]) -> Optional[int]:
    matches = _YEAR_RE.findall(text)
    if len(matches) == 1:
        return int(matches[0])
    if len(matches) > 1:
        notes.append("multiple year-like numbers found; year not extracted")
    return None


def _split_artist_track(
    text: str, notes: list[str]
) -> tuple[Optional[str], Optional[str], str]:
    parts = _SEPARATORS.split(text, maxsplit=1)

    if len(parts) != 2:
        notes.append("no clear artist/track separator found")
        return None, None, "low"

    left, right = parts[0].strip(), parts[1].strip()

    if not left or not right:
        notes.append("separator found but one side is empty")
        return None, None, "low"

    # Strip feat from the right side (it belongs to artist block on left)
    # e.g. "Artist feat. Guest - Track Title"
    feat_in_left = _FEAT_RE.search(left)
    if feat_in_left:
        # Keep full left side as artist (including feat.)
        artist = left
        track = right
        notes.append("feat/ft detected in artist field; kept as-is")
        return artist, track, "medium"

    # Collab via "x" in left side
    if _COLLAB_X_RE.search(left):
        notes.append("collaboration marker 'x' detected in artist field")
        return left, right, "medium"

    # Clean simple case: "Artist - Track"
    return left, right, "high"

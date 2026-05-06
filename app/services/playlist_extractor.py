"""
Extracts playlist and video metadata from YouTube using yt-dlp.

Uses extract_flat=True to avoid downloading videos — only metadata is fetched.
Individual item failures are caught and annotated rather than aborting the run.
"""

import logging
from datetime import datetime, timezone
from typing import Any

import yt_dlp

from app.models.playlist import PlaylistMetadata
from app.models.track_item import TrackItem
from app.services.metadata_parser import parse_title
from app.utils.text_normalizer import normalize_title
from app.utils.logging_utils import get_logger

logger = get_logger(__name__)

_YTDLP_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": "in_playlist",
    "skip_download": True,
    "ignoreerrors": True,
}

# yt-dlp uses these titles for unavailable entries
_UNAVAILABLE_TITLES = {"[deleted video]", "[private video]"}


def extract_playlist(url: str) -> tuple[PlaylistMetadata, list[TrackItem]]:
    raw = _fetch_raw(url)
    playlist_meta = _build_playlist_metadata(url, raw)
    items = _build_items(raw, playlist_meta)
    return playlist_meta, items


def _fetch_raw(url: str) -> dict[str, Any]:
    with yt_dlp.YoutubeDL(_YTDLP_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
    if info is None:
        raise RuntimeError(f"yt-dlp returned no data for URL: {url}")
    return info


def _build_playlist_metadata(url: str, raw: dict[str, Any]) -> PlaylistMetadata:
    return PlaylistMetadata(
        source_url=url,
        playlist_id=raw.get("id") or "",
        title=raw.get("title") or "Unknown Playlist",
        total_items=len(raw.get("entries") or []),
        extracted_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _build_items(raw: dict[str, Any], meta: PlaylistMetadata) -> list[TrackItem]:
    entries = raw.get("entries") or []
    items: list[TrackItem] = []

    for position, entry in enumerate(entries, start=1):
        try:
            item = _build_single_item(entry, position, meta)
        except Exception as exc:
            logger.warning("Failed to process item at position %d: %s", position, exc)
            item = _unavailable_item(entry, position, meta, notes=[f"processing error: {exc}"])
        items.append(item)

    return items


def _build_single_item(
    entry: dict[str, Any] | None, position: int, meta: PlaylistMetadata
) -> TrackItem:
    if entry is None:
        return _unavailable_item(entry, position, meta, notes=["entry is None"])

    video_id = entry.get("id") or ""
    raw_title = entry.get("title") or ""
    availability = _detect_availability(entry, raw_title)

    if availability != "available":
        return TrackItem(
            video_id=video_id,
            playlist_id=meta.playlist_id,
            playlist_title=meta.title,
            original_title=raw_title,
            normalized_title=normalize_title(raw_title) if raw_title else "",
            artist=None,
            track=None,
            year=None,
            uploader=entry.get("uploader"),
            channel=entry.get("channel"),
            duration_seconds=entry.get("duration"),
            url=_build_url(video_id),
            position=position,
            availability_status=availability,
            extraction_confidence="low",
            extraction_notes=[f"video status: {availability}"],
        )

    parsed = parse_title(raw_title)

    return TrackItem(
        video_id=video_id,
        playlist_id=meta.playlist_id,
        playlist_title=meta.title,
        original_title=parsed.original_title,
        normalized_title=parsed.normalized_title,
        artist=parsed.artist,
        track=parsed.track,
        year=parsed.year,
        uploader=entry.get("uploader"),
        channel=entry.get("channel"),
        duration_seconds=entry.get("duration"),
        url=_build_url(video_id),
        position=position,
        availability_status="available",
        extraction_confidence=parsed.confidence,
        extraction_notes=parsed.notes,
    )


def _detect_availability(entry: dict[str, Any], title: str) -> str:
    if title.lower() in _UNAVAILABLE_TITLES:
        if "private" in title.lower():
            return "private"
        return "removed"

    # yt-dlp may expose this field on full extraction; on flat it may be absent
    if entry.get("availability") in {"private", "premium_only", "subscriber_only"}:
        return "private"

    if not entry.get("id"):
        return "unavailable"

    return "available"


def _build_url(video_id: str) -> str:
    if not video_id:
        return ""
    return f"https://www.youtube.com/watch?v={video_id}"


def _unavailable_item(
    entry: dict[str, Any] | None,
    position: int,
    meta: PlaylistMetadata,
    notes: list[str],
) -> TrackItem:
    entry = entry or {}
    return TrackItem(
        video_id=entry.get("id") or "",
        playlist_id=meta.playlist_id,
        playlist_title=meta.title,
        original_title=entry.get("title") or "",
        normalized_title="",
        artist=None,
        track=None,
        year=None,
        uploader=entry.get("uploader"),
        channel=entry.get("channel"),
        duration_seconds=None,
        url=_build_url(entry.get("id") or ""),
        position=position,
        availability_status="unknown",
        extraction_confidence="low",
        extraction_notes=notes,
    )

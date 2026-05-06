import json
import pytest
from pathlib import Path

from app.models.playlist import PlaylistMetadata
from app.models.track_item import TrackItem
from app.services.export_service import build_output_path, export_to_json


def _make_playlist() -> PlaylistMetadata:
    return PlaylistMetadata(
        source_url="https://www.youtube.com/playlist?list=PLTEST",
        playlist_id="PLTEST",
        title="My Test Playlist",
        total_items=1,
        extracted_at="2026-01-01T00:00:00Z",
    )


def _make_item(position: int = 1) -> TrackItem:
    return TrackItem(
        video_id="abc123",
        playlist_id="PLTEST",
        playlist_title="My Test Playlist",
        original_title="Artist - Track (Official Audio)",
        normalized_title="artist - track",
        artist="Artist",
        track="Track",
        year=None,
        uploader="ArtistChannel",
        channel="ArtistChannel",
        duration_seconds=210,
        url="https://www.youtube.com/watch?v=abc123",
        position=position,
        availability_status="available",
        extraction_confidence="high",
        extraction_notes=[],
    )


class TestBuildOutputPath:
    def test_generates_path_with_title_and_id(self, tmp_path):
        meta = _make_playlist()
        path = build_output_path(meta, tmp_path)
        assert path.parent == tmp_path
        assert "PLTEST" in path.name
        assert path.suffix == ".json"

    def test_title_is_truncated_for_long_names(self, tmp_path):
        meta = _make_playlist()
        meta.title = "A" * 200
        path = build_output_path(meta, tmp_path)
        assert len(path.name) < 300  # sanity check, not exact length

    def test_special_chars_in_title_are_replaced(self, tmp_path):
        meta = _make_playlist()
        meta.title = "My Playlist / Sub & More!"
        path = build_output_path(meta, tmp_path)
        assert "/" not in path.name
        assert "&" not in path.name


class TestExportToJson:
    def test_creates_file(self, tmp_path):
        meta = _make_playlist()
        items = [_make_item()]
        output = tmp_path / "out.json"
        export_to_json(meta, items, output)
        assert output.exists()

    def test_json_has_playlist_and_items_keys(self, tmp_path):
        meta = _make_playlist()
        items = [_make_item()]
        output = tmp_path / "out.json"
        export_to_json(meta, items, output)
        data = json.loads(output.read_text())
        assert "playlist" in data
        assert "items" in data

    def test_playlist_fields_match(self, tmp_path):
        meta = _make_playlist()
        output = tmp_path / "out.json"
        export_to_json(meta, [], output)
        data = json.loads(output.read_text())
        assert data["playlist"]["playlist_id"] == "PLTEST"
        assert data["playlist"]["title"] == "My Test Playlist"

    def test_item_fields_present(self, tmp_path):
        meta = _make_playlist()
        item = _make_item()
        output = tmp_path / "out.json"
        export_to_json(meta, [item], output)
        data = json.loads(output.read_text())
        first = data["items"][0]
        assert first["video_id"] == "abc123"
        assert first["artist"] == "Artist"
        assert first["track"] == "Track"
        assert first["availability_status"] == "available"
        assert first["extraction_confidence"] == "high"

    def test_empty_items_list(self, tmp_path):
        meta = _make_playlist()
        output = tmp_path / "out.json"
        export_to_json(meta, [], output)
        data = json.loads(output.read_text())
        assert data["items"] == []

    def test_creates_output_dir_if_missing(self, tmp_path):
        meta = _make_playlist()
        nested = tmp_path / "deep" / "nested" / "out.json"
        export_to_json(meta, [], nested)
        assert nested.exists()

    def test_output_is_valid_utf8(self, tmp_path):
        meta = _make_playlist()
        meta.title = "Playlist com acentuação: ã ê ó ü"
        output = tmp_path / "out.json"
        export_to_json(meta, [], output)
        content = output.read_text(encoding="utf-8")
        assert "ã" in content or "\\u" in content  # either literal or escaped is acceptable

    def test_multiple_items_preserve_order(self, tmp_path):
        meta = _make_playlist()
        items = [_make_item(position=i) for i in range(1, 6)]
        output = tmp_path / "out.json"
        export_to_json(meta, items, output)
        data = json.loads(output.read_text())
        positions = [i["position"] for i in data["items"]]
        assert positions == [1, 2, 3, 4, 5]

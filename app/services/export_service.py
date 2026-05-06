import json
import re
from pathlib import Path

from app.models.playlist import PlaylistMetadata
from app.models.track_item import TrackItem

_SAFE_FILENAME_RE = re.compile(r"[^\w\-]")


def build_output_path(playlist_meta: PlaylistMetadata, output_dir: Path) -> Path:
    safe_title = _SAFE_FILENAME_RE.sub("_", playlist_meta.title)[:60]
    filename = f"{safe_title}__{playlist_meta.playlist_id}.json"
    return output_dir / filename


def export_to_json(
    playlist_meta: PlaylistMetadata,
    items: list[TrackItem],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "playlist": playlist_meta.to_dict(),
        "items": [item.to_dict() for item in items],
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

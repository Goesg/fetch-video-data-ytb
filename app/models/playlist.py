from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PlaylistMetadata:
    source_url: str
    playlist_id: str
    title: str
    total_items: int
    extracted_at: str

    def to_dict(self) -> dict:
        return asdict(self)

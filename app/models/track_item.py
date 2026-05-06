from dataclasses import dataclass, field, asdict
from typing import Optional, Literal

AvailabilityStatus = Literal["available", "private", "removed", "unavailable", "unknown"]
ExtractionConfidence = Literal["high", "medium", "low"]


@dataclass
class TrackItem:
    video_id: str
    playlist_id: str
    playlist_title: str
    original_title: str
    normalized_title: str
    artist: Optional[str]
    track: Optional[str]
    year: Optional[int]
    uploader: Optional[str]
    channel: Optional[str]
    duration_seconds: Optional[int]
    url: str
    position: int
    availability_status: AvailabilityStatus
    extraction_confidence: ExtractionConfidence
    extraction_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

import pytest
from app.services.metadata_parser import parse_title


class TestParseTitle:
    # --- Standard "Artist - Track" separators ---

    def test_hyphen_separator(self):
        result = parse_title("Pink Floyd - Comfortably Numb")
        assert result.artist == "Pink Floyd"
        assert result.track == "Comfortably Numb"
        assert result.confidence == "high"

    def test_em_dash_separator(self):
        result = parse_title("Radiohead – Karma Police")
        assert result.artist == "Radiohead"
        assert result.track == "Karma Police"
        assert result.confidence == "high"

    def test_pipe_separator(self):
        result = parse_title("The Beatles | Let It Be")
        assert result.artist == "The Beatles"
        assert result.track == "Let It Be"
        assert result.confidence == "high"

    # --- feat / ft handling ---

    def test_feat_in_artist_field(self):
        result = parse_title("Drake feat. Rihanna - Too Good")
        assert result.artist == "Drake feat. Rihanna"
        assert result.track == "Too Good"
        assert result.confidence == "medium"
        assert any("feat" in n for n in result.notes)

    def test_ft_abbreviation(self):
        result = parse_title("Eminem ft. Dido - Stan")
        assert result.artist == "Eminem ft. Dido"
        assert result.track == "Stan"
        assert result.confidence == "medium"

    # --- collab x ---

    def test_collab_x(self):
        result = parse_title("Artist A x Artist B - Track Title")
        assert result.artist == "Artist A x Artist B"
        assert result.track == "Track Title"
        assert result.confidence == "medium"

    # --- No separator ---

    def test_no_separator_returns_low_confidence(self):
        result = parse_title("Just A Song Title With No Separator")
        assert result.artist is None
        assert result.track is None
        assert result.confidence == "low"
        assert any("separator" in n for n in result.notes)

    # --- Noise tag removal ---

    def test_removes_official_video_tag(self):
        result = parse_title("Artist - Track (Official Video)")
        assert result.track == "Track"
        assert result.artist == "Artist"

    def test_removes_official_audio_tag(self):
        result = parse_title("Artist - Track (Official Audio)")
        assert result.track == "Track"

    def test_removes_lyrics_tag(self):
        result = parse_title("Artist - Track [Lyrics]")
        assert result.track == "Track"

    def test_removes_remastered_tag(self):
        result = parse_title("Artist - Track (Remastered 2011)")
        assert result.track == "Track"

    def test_removes_hd_tag(self):
        result = parse_title("Artist - Track [HD]")
        assert result.track == "Track"

    # --- Year extraction ---

    def test_extracts_year_from_title(self):
        result = parse_title("Artist - Track (1994)")
        assert result.year == 1994

    def test_no_year_when_absent(self):
        result = parse_title("Artist - Track")
        assert result.year is None

    def test_no_year_when_ambiguous(self):
        result = parse_title("Artist - Track 1994 2001")
        assert result.year is None
        assert any("multiple year" in n for n in result.notes)

    # --- Original title always preserved ---

    def test_original_title_preserved(self):
        raw = "Artist - Track (Official Video) [HD]"
        result = parse_title(raw)
        assert result.original_title == raw

    # --- Normalized title is lowercase ---

    def test_normalized_title_is_lowercase(self):
        result = parse_title("Artist - Track")
        assert result.normalized_title == result.normalized_title.lower()

    # --- Edge cases ---

    def test_empty_title(self):
        result = parse_title("")
        assert result.artist is None
        assert result.track is None
        assert result.confidence == "low"

    def test_title_with_only_separator(self):
        result = parse_title(" - ")
        assert result.artist is None
        assert result.track is None
        assert result.confidence == "low"

import pytest
from app.utils.validators import is_valid_playlist_url, extract_playlist_id


class TestIsValidPlaylistUrl:
    def test_standard_playlist_url(self):
        url = "https://www.youtube.com/playlist?list=PLAbCdEfGhIjKlMn"
        assert is_valid_playlist_url(url) is True

    def test_playlist_url_with_other_params(self):
        url = "https://www.youtube.com/watch?v=XYZ123&list=PLAbCdEfGhIjKlMn"
        assert is_valid_playlist_url(url) is True

    def test_url_without_list_param(self):
        assert is_valid_playlist_url("https://www.youtube.com/watch?v=abc123") is False

    def test_empty_string(self):
        assert is_valid_playlist_url("") is False

    def test_non_youtube_url(self):
        assert is_valid_playlist_url("https://vimeo.com/playlist/123") is False

    def test_url_without_http(self):
        url = "youtube.com/playlist?list=PLAbCdEfGhIjKlMn"
        assert is_valid_playlist_url(url) is True

    def test_url_without_www(self):
        url = "https://youtube.com/playlist?list=PLAbCdEfGhIjKlMn"
        assert is_valid_playlist_url(url) is True

    def test_plain_text(self):
        assert is_valid_playlist_url("not a url at all") is False


class TestExtractPlaylistId:
    def test_extracts_id_from_standard_url(self):
        url = "https://www.youtube.com/playlist?list=PLAbCdEfGhIjKlMn"
        assert extract_playlist_id(url) == "PLAbCdEfGhIjKlMn"

    def test_extracts_id_from_mixed_params(self):
        url = "https://www.youtube.com/watch?v=XYZ&list=PLTest1234"
        assert extract_playlist_id(url) == "PLTest1234"

    def test_returns_none_for_url_without_list(self):
        assert extract_playlist_id("https://www.youtube.com/watch?v=abc") is None

    def test_returns_none_for_empty_string(self):
        assert extract_playlist_id("") is None

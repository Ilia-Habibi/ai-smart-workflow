import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from music_api import MusicFinder


@pytest.fixture
def finder():
    with patch("music_api.YTMusic") as mock_yt_cls:
        mock_instance = mock_yt_cls.return_value
        finder = MusicFinder()
        finder.yt = mock_instance
        yield finder


def test_find_best_match_song(finder):
    finder.yt.search.return_value = [
        {
            "resultType": "song",
            "videoId": "abc123_",
            "title": "Test Song",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "thumbnails": [{"url": "http://cover"}],
            "duration": "4:20",
        }
    ]

    result = finder.find_best_match("query")
    assert result is not None
    assert result["yt_id"] == "abc123_"
    assert result["artist"] == "Test Artist"
    assert result["album"] == "Test Album"
    assert result["cover_url"] == "http://cover"


def test_find_best_match_video(finder):
    finder.yt.search.return_value = [
        {
            "resultType": "video",
            "videoId": "vid123",
            "title": "Live Performance",
            "artists": [{"name": "Band"}],
            "duration": "5:00",
        }
    ]

    result = finder.find_best_match("query")
    assert result is not None
    assert result["yt_id"] == "vid123"
    assert result["type"] == "video"
    assert result["album"] == "Single"


def test_find_best_match_no_results(finder):
    finder.yt.search.return_value = []
    result = finder.find_best_match("query")
    assert result is None


def test_find_best_match_exception(finder):
    finder.yt.search.side_effect = Exception("API Error")
    result = finder.find_best_match("query")
    assert result is None


def test_find_best_match_skips_invalid_types(finder):
    finder.yt.search.return_value = [
        {"resultType": "playlist", "title": "Mix"},
        {"resultType": "artist", "title": "Artist Page"},
    ]
    result = finder.find_best_match("query")
    assert result is None

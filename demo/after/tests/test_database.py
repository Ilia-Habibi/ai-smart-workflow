import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import DatabaseHandler


@pytest.fixture
def db():
    # Use an in-memory DB for testing
    handler = DatabaseHandler(":memory:")
    yield handler
    handler.close()

def test_create_table(db):
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in db.cursor.fetchall()]
    assert 'tracks' in tables
    assert 'images_log' in tables

def test_add_image_log(db):
    db.add_image_log("test.jpg", "raw text")
    db.cursor.execute("SELECT full_text FROM images_log WHERE filename='test.jpg'")
    assert db.cursor.fetchone()[0] == "raw text"

def test_add_image_log_duplicate(db):
    db.add_image_log("test.jpg", "raw text 1")
    db.add_image_log("test.jpg", "raw text 2") # Should be ignored
    db.cursor.execute("SELECT count(*) FROM images_log WHERE filename='test.jpg'")
    assert db.cursor.fetchone()[0] == 1

def test_add_raw_track(db):
    assert db.add_raw_track("song 1")
    assert not db.add_raw_track("song 1") # duplicate

def test_get_pending_tracks(db):
    db.add_raw_track("song 1")
    db.add_raw_track("song 2")
    pending = db.get_pending_tracks()
    assert len(pending) == 2
    assert pending[0][1] == "song 1"

def test_update_track_info(db):
    db.add_raw_track("song 1")
    track_id = db.get_pending_tracks()[0][0]

    info = {
        'title': 'Song 1',
        'artist': 'Artist 1',
        'album': 'Album 1',
        'yt_id': 'xyz123',
        'cover_url': 'http://url',
        'duration': '3:00'
    }

    assert db.update_track_info(track_id, info)
    db.cursor.execute("SELECT status, yt_id FROM tracks WHERE id=?", (track_id,))
    res = db.cursor.fetchone()
    assert res[0] == 'found'
    assert res[1] == 'xyz123'

def test_update_track_info_duplicate_yt_id(db):
    # Add two tracks
    db.add_raw_track("song 1")
    db.add_raw_track("song 2")
    pending = db.get_pending_tracks()
    id1 = pending[0][0]
    id2 = pending[1][0]

    info = {
        'title': 'Song 1', 'artist': 'Artist 1', 'album': 'Album 1',
        'yt_id': 'xyz123', 'cover_url': 'http://url', 'duration': '3:00'
    }

    db.update_track_info(id1, info)

    # Try to update second track with same yt_id
    assert not db.update_track_info(id2, info) # Should delete duplicate

    db.cursor.execute("SELECT count(*) FROM tracks WHERE id=?", (id2,))
    assert db.cursor.fetchone()[0] == 0 # Was deleted

def test_mark_track_not_found(db):
    db.add_raw_track("song 1")
    track_id = db.get_pending_tracks()[0][0]
    db.mark_track_not_found(track_id)
    db.cursor.execute("SELECT status FROM tracks WHERE id=?", (track_id,))
    assert db.cursor.fetchone()[0] == 'not_found'

def test_get_tracks_to_download(db):
    db.add_raw_track("song 1")
    track_id = db.get_pending_tracks()[0][0]

    info = {
        'title': 'Song 1', 'artist': 'Artist 1', 'album': 'Album 1',
        'yt_id': 'xyz123', 'cover_url': 'http://url', 'duration': '3:00'
    }
    db.update_track_info(track_id, info)

    to_download = db.get_tracks_to_download()
    assert len(to_download) == 1
    assert to_download[0][1] == 'Song 1'

def test_mark_track_downloaded(db):
    db.add_raw_track("song 1")
    track_id = db.get_pending_tracks()[0][0]
    db.mark_track_downloaded(track_id)
    db.cursor.execute("SELECT status FROM tracks WHERE id=?", (track_id,))
    assert db.cursor.fetchone()[0] == 'downloaded'

def test_is_image_processed(db):
    db.add_image_log("test.jpg", "raw text")
    assert db.is_image_processed("test.jpg")
    assert not db.is_image_processed("unknown.jpg")

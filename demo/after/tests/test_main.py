import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import main

@patch('main.os.path.exists')
@patch('main.os.makedirs')
def test_main_creates_dir(mock_makedirs, mock_exists, capsys):
    mock_exists.return_value = False
    main()
    mock_makedirs.assert_called_once_with("input_images")
    captured = capsys.readouterr()
    assert "Directory 'input_images' created" in captured.out

@patch('main.os.path.exists')
@patch('main.os.listdir')
@patch('main.DatabaseHandler')
@patch('main.OCRHandler')
@patch('main.MusicFinder')
@patch('main.Downloader')
def test_main_full_flow(mock_dl, mock_finder, mock_ocr, mock_db, mock_listdir, mock_exists):
    # Mock OS
    mock_exists.return_value = True
    mock_listdir.return_value = ['test1.jpg', 'not_image.txt']
    
    # Mock DB
    db_inst = mock_db.return_value
    db_inst.is_image_processed.return_value = False
    db_inst.get_pending_tracks.return_value = [(1, "raw track")]
    db_inst.update_track_info.return_value = True
    db_inst.get_tracks_to_download.return_value = [(1, "Song", "Artist", "Album", "yt123", "cover")]
    
    # Mock OCR
    ocr_inst = mock_ocr.return_value
    ocr_inst.extract_clean_tracks.return_value = (["raw track"], "full raw track")
    
    # Mock Finder
    finder_inst = mock_finder.return_value
    finder_inst.find_best_match.return_value = {
        'title': 'Song', 'artist': 'Artist', 'album': 'Album'
    }
    
    # Mock Downloader
    dl_inst = mock_dl.return_value
    dl_inst.get_file_info.return_value = 5000000 # ~5MB
    dl_inst.download_audio.return_value = "path/to/mp3"
    
    main()
    
    # Verify calls
    db_inst.add_image_log.assert_called_once_with('test1.jpg', 'full raw track')
    db_inst.add_raw_track.assert_called_once_with('raw track')
    finder_inst.find_best_match.assert_called_once_with('raw track')
    dl_inst.download_audio.assert_called_once_with('yt123', 'Artist - Song')
    dl_inst.add_metadata.assert_called_once()
    db_inst.close.assert_called_once()

@patch('main.os.path.exists')
@patch('main.os.listdir')
@patch('main.DatabaseHandler')
def test_main_skips_processed_image(mock_db, mock_listdir, mock_exists, capsys):
    mock_exists.return_value = True
    mock_listdir.return_value = ['test1.jpg']
    
    db_inst = mock_db.return_value
    db_inst.is_image_processed.return_value = True
    db_inst.get_pending_tracks.return_value = []
    db_inst.get_tracks_to_download.return_value = []
    
    main()
    
    captured = capsys.readouterr()
    assert "Skipping test1.jpg (Already processed)" in captured.out

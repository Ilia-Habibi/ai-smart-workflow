import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from downloader import Downloader

@pytest.fixture
def downloader(tmp_path):
    return Downloader(download_folder=str(tmp_path))

@patch('downloader.yt_dlp.YoutubeDL')
def test_get_file_info_success(mock_ydl, downloader):
    mock_instance = mock_ydl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {
        'formats': [
            {'vcodec': 'none', 'acodec': 'mp4a.40.2', 'filesize': 12345}
        ]
    }
    
    size = downloader.get_file_info("dummy_id")
    assert size == 12345

@patch('downloader.yt_dlp.YoutubeDL')
def test_get_file_info_no_formats(mock_ydl, downloader):
    mock_instance = mock_ydl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {
        'filesize_approx': 5000
    }
    
    size = downloader.get_file_info("dummy_id")
    assert size == 5000

@patch('downloader.subprocess.run')
def test_download_audio_success(mock_run, downloader, tmp_path):
    def side_effect(*args, **kwargs):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        if 'yt-dlp' in args[0]:
            mock_proc.stdout = "http://stream.url"
        elif 'ffmpeg' in args[0]:
            # Simulate file creation > 10KB
            mp3_path = os.path.join(str(tmp_path), "test.mp3")
            with open(mp3_path, 'wb') as f:
                f.write(b'0' * 15000)
        return mock_proc
        
    mock_run.side_effect = side_effect
    
    result = downloader.download_audio("dummy_id", "test")
    assert result is not None
    assert result.endswith("test.mp3")
    assert os.path.exists(result)

@patch('downloader.subprocess.run')
def test_download_audio_fail_stream(mock_run, downloader):
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = ""
    mock_run.return_value = mock_proc
    
    result = downloader.download_audio("dummy_id", "test")
    assert result is None

@patch('downloader.EasyID3')
@patch('downloader.ID3')
@patch('downloader.requests.get')
def test_add_metadata_success(mock_get, mock_id3, mock_easyid3, downloader, tmp_path):
    mp3_path = os.path.join(str(tmp_path), "test.mp3")
    with open(mp3_path, 'w') as f:
        f.write('dummy')
        
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'image data'
    mock_resp.headers = {'Content-Type': 'image/jpeg'}
    mock_get.return_value = mock_resp
    
    result = downloader.add_metadata(mp3_path, "Title", "Artist", "Album", "http://cover")
    assert result == True
    mock_easyid3.assert_called()
    mock_id3.assert_called()

@patch('downloader.EasyID3')
def test_add_metadata_no_cover(mock_easyid3, downloader, tmp_path):
    mp3_path = os.path.join(str(tmp_path), "test.mp3")
    with open(mp3_path, 'w') as f:
        f.write('dummy')
        
    result = downloader.add_metadata(mp3_path, "Title", "Artist", "Album", "")
    assert result == True
    mock_easyid3.assert_called()

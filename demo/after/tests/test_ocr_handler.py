import pytest
import numpy as np
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ocr_handler import OCRHandler

@pytest.fixture
def ocr():
    return OCRHandler(tesseract_path='dummy_path')

@patch('ocr_handler.cv2.imread')
@patch('ocr_handler.cv2.cvtColor')
@patch('ocr_handler.cv2.adaptiveThreshold')
def test_preprocess_image_success(mock_thresh, mock_cvt, mock_imread, ocr):
    # Create a mock 100x100 BGR image
    mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_imread.return_value = mock_img
    
    # Mock return values for subsequent steps
    mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
    mock_thresh.return_value = np.ones((50, 50), dtype=np.uint8)
    
    res = ocr.preprocess_image("dummy.jpg")
    assert res is not None
    mock_imread.assert_called_once_with("dummy.jpg")

@patch('ocr_handler.cv2.imread')
def test_preprocess_image_not_found(mock_imread, ocr):
    mock_imread.return_value = None
    res = ocr.preprocess_image("missing.jpg")
    assert res is None

@patch('ocr_handler.pytesseract.image_to_data')
def test_extract_text_data(mock_image_to_data, ocr):
    with patch.object(ocr, 'preprocess_image', return_value=np.ones((10, 10))):
        mock_image_to_data.return_value = {'text': ['hello']}
        res = ocr.extract_text_data("dummy.jpg")
        assert res == {'text': ['hello']}

def test_extract_text_data_no_image(ocr):
    with patch.object(ocr, 'preprocess_image', return_value=None):
        res = ocr.extract_text_data("dummy.jpg")
        assert res == {}

def test_extract_clean_tracks_basic(ocr):
    data = {
        'text': ['Song', 'Name', '', 'By', 'Artist'],
        'top': [10, 10, 10, 30, 30],
        'height': [10, 10, 10, 10, 10]
    }
    with patch.object(ocr, 'extract_text_data', return_value=data):
        lines, raw = ocr.extract_clean_tracks("dummy.jpg")
        assert len(lines) == 2
        assert lines[0] == "Song Name"
        assert lines[1] == "By Artist"
        assert "Song Name  By Artist" in raw.strip()

def test_extract_clean_tracks_empty(ocr):
    with patch.object(ocr, 'extract_text_data', return_value={}):
        lines, raw = ocr.extract_clean_tracks("dummy.jpg")
        assert len(lines) == 0
        assert raw == ""

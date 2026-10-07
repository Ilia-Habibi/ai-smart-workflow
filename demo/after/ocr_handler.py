"""
OCR Handler Module.

Leverages Tesseract-OCR and OpenCV for robust text extraction.
Key Features:
- Adaptive Thresholding for handling dark mode/low contrast images.
- Intelligent cropping to remove status bars and navigation UI.
- Text grouping logic to combine fragmented lines into coherent track names.
"""

import cv2
import numpy as np
import os
import pytesseract
from typing import Tuple, List, Optional, Any, Dict

class OCRHandler:
    """Handles OCR operations for image processing."""

    def __init__(self, tesseract_path: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe') -> None:
        """Initializes the OCR handler and sets the Tesseract executable path.

        Args:
            tesseract_path (str): The path to the Tesseract executable. Defaults to 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'.
        """
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print(f"Warning: Tesseract functionality might fail. File not found at: {tesseract_path}")
            print("Please ensure Tesseract-OCR is installed and the path is correct.")

    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """Preprocesses the image to improve OCR accuracy.

        Includes cropping, converting to grayscale, checking for dark mode, and thresholding.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Optional[np.ndarray]: The preprocessed binary image, or None if image read failed.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None

        h, w, _ = img.shape

        top_crop = int(w * 0.25)
        bottom_crop = int(h - (w * 0.1))
        left_crop = int(w * 0.15)
        right_crop = int(w - (w * 0.15))
        
        cropped_img = img[top_crop:bottom_crop, left_crop:right_crop]

        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

        if np.mean(gray) < 127:
            gray = cv2.bitwise_not(gray)

        binary = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            31, 15
        )

        return binary

    def extract_text_data(self, image_path: str) -> Dict[str, List[Any]]:
        """Extracts detailed OCR data including line coordinates.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Dict[str, List[Any]]: Dictionary containing Tesseract OCR output data.
        """
        processed_img = self.preprocess_image(image_path)
        if processed_img is None:
            return {}

        data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
        return data

    def extract_clean_tracks(self, image_path: str) -> Tuple[List[str], str]:
        """Extracts text data and groups nearby lines into track details.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Tuple[List[str], str]: A tuple of (list of grouped lines, full raw text).
        """
        data = self.extract_text_data(image_path)
        if not data or 'text' not in data:
            return [], ""

        n_boxes = len(data['text'])
        grouped_lines: List[str] = []
        current_group: List[str] = []
        last_top = 0
        last_height = 0
        
        full_raw_text = ""

        for i in range(n_boxes):
            text = data['text'][i].strip()
            if not text:
                continue

            full_raw_text += text + " "

            top = data['top'][i]
            height = data['height'][i]
            
            if last_top == 0 or (top - last_top) < (last_height * 2.5): 
                current_group.append(text)
            else:
                if current_group:
                    grouped_lines.append(" ".join(current_group))
                current_group = [text]

            last_top = top
            last_height = height

        if current_group:
            grouped_lines.append(" ".join(current_group))

        return grouped_lines, full_raw_text

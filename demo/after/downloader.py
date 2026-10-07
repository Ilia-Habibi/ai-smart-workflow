"""
Audio Downloader & Metadata Tagging Module.

Handles the retrieval of audio streams and file post-processing.
- Uses yt-dlp to extract stream URLs.
- Uses FFmpeg for robust audio conversion (stream -> mp3).
- Applies ID3 tags and Album Art using Mutagen.

Note: Includes error handling for common stream extraction failures.
"""

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import os
import requests
import subprocess
import yt_dlp
from typing import Optional

class Downloader:
    """Manages audio downloading and tagging."""

    def __init__(self, download_folder: str = "downloads") -> None:
        """Initializes the downloader and creates the download directory.

        Args:
            download_folder (str): Directory where downloaded files are saved. Defaults to "downloads".
        """
        self.download_folder = download_folder
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

    def get_file_info(self, yt_id: str) -> int:
        """Gets the file size (in bytes) of the best available audio format.

        Args:
            yt_id (str): The YouTube video ID.

        Returns:
            int: The estimated file size in bytes, or 0 if not found.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={yt_id}', download=False)
                
                if info and 'formats' in info:
                    audio_formats = [f for f in info['formats'] if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                    
                    if audio_formats:
                        best_audio = audio_formats[-1]
                        return best_audio.get('filesize') or best_audio.get('filesize_approx') or 0
                
                if info:
                    return info.get('filesize') or info.get('filesize_approx') or 0
                return 0
        except Exception:
            return 0

    def download_audio(self, yt_id: str, filename: str) -> Optional[str]:
        """Downloads audio using yt-dlp to get stream URL and ffmpeg to convert.

        Args:
            yt_id (str): The YouTube video ID.
            filename (str): The base filename (without extension).

        Returns:
            Optional[str]: The path to the downloaded mp3 file, or None if failed.
        """
        final_mp3_path = os.path.join(self.download_folder, f"{filename}.mp3")
        video_url = f"https://www.youtube.com/watch?v={yt_id}"

        print(f"Resolving stream URL for {yt_id}...")

        cmd_get_url = ["yt-dlp", "-f", "bestaudio/best", "-g", video_url]

        try:
            process = subprocess.run(cmd_get_url, capture_output=True, text=True, check=True, encoding='utf-8')
            stream_url = process.stdout.strip()
            
            if not stream_url:
                print("Error: Could not retrieve stream URL (empty output).")
                return None

            print("Stream URL found. Starting download with FFmpeg...")

            cmd_ffmpeg = [
                "ffmpeg", 
                "-y", 
                "-i", stream_url,
                "-vn", 
                "-ar", "44100", 
                "-ac", "2", 
                "-b:a", "192k", 
                "-f", "mp3", 
                final_mp3_path
            ]
            
            ffmpeg_process = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)
            
            if ffmpeg_process.returncode != 0:
                print(f"FFmpeg Error: {ffmpeg_process.stderr}")
                return None
            
            if os.path.exists(final_mp3_path) and os.path.getsize(final_mp3_path) > 10240:
                return final_mp3_path
            else:
                print("FFmpeg finished but file is missing or too small.")
                return None

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            if e.stderr:
                print(f"Details: {e.stderr}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def add_metadata(self, filepath: str, title: str, artist: str, album: str, cover_url: str) -> bool:
        """Adds ID3 tags and cover image to the MP3 file.

        Args:
            filepath (str): Path to the mp3 file.
            title (str): Track title.
            artist (str): Track artist.
            album (str): Album name.
            cover_url (str): URL for the album cover image.

        Returns:
            bool: True if metadata added successfully, False otherwise.
        """
        try:
            try:
                audio = EasyID3(filepath)
            except:
                audio = EasyID3()
                audio.save(filepath)
            
            audio['title'] = title
            audio['artist'] = artist
            audio['album'] = album
            audio.save()

            if cover_url:
                response = requests.get(cover_url, timeout=10)
                if response.status_code == 200:
                    mime_type = response.headers.get('Content-Type', 'image/jpeg') 
                    
                    audio_id3 = ID3(filepath)
                    audio_id3.add(APIC(
                        encoding=3, 
                        mime=mime_type, 
                        type=3, 
                        desc=u'Cover',
                        data=response.content
                    ))
                    audio_id3.save()
            
            print(f"Metadata added to {filepath}")
            return True

        except Exception as e:
            print(f"Error tagging {filepath}: {e}")
            return False

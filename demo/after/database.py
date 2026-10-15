"""Database Management Module.

Handles all SQLite interactions for the application.
Responsibilities:
- Schema initialization (tracks table, image processing logs).
- Deduplication logic (preventing duplicate processing of the same image or track).
- State management for tracks (pending -> searched -> downloaded).
"""

import sqlite3
from typing import Any


class DatabaseHandler:
    """Handles SQLite database connections and queries.

    Attributes:
        conn (sqlite3.Connection): SQLite connection object.
        cursor (sqlite3.Cursor): Database cursor for executing queries.
    """

    def __init__(self, db_name: str = "playlist.db") -> None:
        """Initializes the database connection and creates tables if missing.

        Args:
            db_name (str): The name of the database file. Defaults to "playlist.db".
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self) -> None:
        """Creates the necessary database tables.

        Creates 'tracks' table for storing song metadata and 'images_log'
        for tracking processed images.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT UNIQUE,
                song_name TEXT,
                artist_name TEXT,
                album TEXT,
                yt_id TEXT,
                cover_url TEXT,
                duration TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                full_text TEXT
            )
        """)
        self.conn.commit()

    def add_image_log(self, filename: str, full_text: str) -> None:
        """Logs the image and its full text.

        If the filename already exists, it will skip logging to avoid duplicates.

        Args:
            filename (str): The name of the image file.
            full_text (str): The raw text extracted from the image.
        """
        try:
            self.cursor.execute("INSERT INTO images_log (filename, full_text) VALUES (?, ?)", (filename, full_text))
            self.conn.commit()
            print(f"Image logged: {filename}")
        except sqlite3.IntegrityError:
            print(f"Image log already exists for: {filename}")

    def add_raw_track(self, raw_text: str) -> bool:
        """Adds raw text to the database.

        Args:
            raw_text (str): The raw text of the track.

        Returns:
            bool: True if added successfully, False if it is a duplicate.
        """
        try:
            self.cursor.execute("INSERT INTO tracks (raw_text) VALUES (?)", (raw_text,))
            self.conn.commit()
            print(f"Added raw track: {raw_text}")
            return True
        except sqlite3.IntegrityError:
            return False

    def get_pending_tracks(self) -> list[tuple[int, str]]:
        """Retrieves a list of tracks that have not been searched yet.

        Returns:
            List[Tuple[int, str]]: A list of tuples containing track ID and raw text.
        """
        self.cursor.execute("SELECT id, raw_text FROM tracks WHERE status = 'pending'")
        return self.cursor.fetchall()

    def update_track_info(self, track_id: int, info: dict[str, Any]) -> bool:
        """Updates track information after finding it in the API.

        Also checks for duplicate tracks (duplicate yt_id).
        If a duplicate is found, this row is deleted.

        Args:
            track_id (int): The internal ID of the track.
            info (Dict[str, Any]): A dictionary containing track metadata.

        Returns:
            bool: True if updated, False if deleted as duplicate.
        """
        yt_id = info.get('yt_id')
        if not yt_id:
            print(f"Missing valid yt_id for track ID {track_id}")
            return False

        self.cursor.execute("SELECT id FROM tracks WHERE yt_id = ? AND id != ?", (yt_id, track_id))
        duplicate = self.cursor.fetchone()

        if duplicate:
            print(f"Duplicate song found for ID {track_id} (matches existing ID {duplicate[0]}). Deleting duplicate entry.")
            self.cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
            self.conn.commit()
            return False

        self.cursor.execute("""
            UPDATE tracks
            SET song_name = ?,
                artist_name = ?,
                album = ?,
                yt_id = ?,
                cover_url = ?,
                duration = ?,
                status = 'found'
            WHERE id = ?
        """, (
            info.get('title', ''),
            info.get('artist', ''),
            info.get('album', 'Single'),
            yt_id,
            info.get('cover_url', ''),
            info.get('duration', ''),
            track_id
        ))
        self.conn.commit()
        print(f"Updated track {track_id}: {info.get('title', '')} - {yt_id}")
        return True

    def mark_track_not_found(self, track_id: int) -> None:
        """Marks a track as not found to prevent further searches.

        Args:
            track_id (int): The internal ID of the track.
        """
        self.cursor.execute("UPDATE tracks SET status = 'not_found' WHERE id = ?", (track_id,))
        self.conn.commit()

    def get_tracks_to_download(self) -> list[tuple[int, str, str, str, str, str]]:
        """Retrieves a list of tracks ready for download.

        Returns:
            List[Tuple[int, str, str, str, str, str]]: A list of track information tuples.
        """
        self.cursor.execute("""
            SELECT id, song_name, artist_name, album, yt_id, cover_url
            FROM tracks
            WHERE status = 'found'
        """)
        return self.cursor.fetchall()

    def mark_track_downloaded(self, track_id: int) -> None:
        """Marks a track as downloaded.

        Args:
            track_id (int): The internal ID of the track.
        """
        self.cursor.execute("UPDATE tracks SET status = 'downloaded' WHERE id = ?", (track_id,))
        self.conn.commit()

    def is_image_processed(self, filename: str) -> bool:
        """Checks if this image has been processed before.

        Args:
            filename (str): The name of the image file.

        Returns:
            bool: True if processed, False otherwise.
        """
        self.cursor.execute("SELECT id FROM images_log WHERE filename = ?", (filename,))
        return self.cursor.fetchone() is not None

    def close(self) -> None:
        """Closes the database connection."""
        self.conn.close()

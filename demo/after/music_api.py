"""Music API Wrapper.

Interface for the ytmusicapi library to search and retrieve metadata.
Focuses on finding the best match (Official Song or High Quality Video) based on
title and artist queries.
"""

from typing import Optional, Dict, Any, List
from ytmusicapi import YTMusic

class MusicFinder:
    """Handles interaction with the YouTube Music API."""

    def __init__(self) -> None:
        """Initializes the MusicFinder with YTMusic."""
        self.yt = YTMusic()

    def find_best_match(self, query: str) -> Optional[Dict[str, Any]]:
        """Searches YouTube Music and finds the best match.

        Checks both official songs and videos to also find remixes and unofficial covers.

        Args:
            query (str): The search query (artist and song name).

        Returns:
            Optional[Dict[str, Any]]: A dictionary of metadata if found, otherwise None.
        """
        try:
            results: List[Dict[str, Any]] = self.yt.search(query)
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            return None

        if not results:
            return None

        for item in results:
            if item.get('resultType') in ['song', 'video']:
                
                artists = []
                if 'artists' in item and isinstance(item['artists'], list):
                    artists = [a.get('name', '') for a in item['artists'] if 'name' in a]
                artist_text = ", ".join(artists)

                album = "Single"
                if 'album' in item and item['album'] and 'name' in item['album']:
                    album = item['album']['name']

                cover = ""
                if 'thumbnails' in item and isinstance(item['thumbnails'], list) and item['thumbnails']:
                    cover = item['thumbnails'][-1].get('url', '')

                return {
                    'yt_id': item.get('videoId', ''),
                    'title': item.get('title', ''),
                    'artist': artist_text,
                    'album': album,
                    'cover_url': cover,
                    'duration': item.get('duration', ''),
                    'type': item.get('resultType', '')
                }
        
        return None

if __name__ == "__main__":
    finder = MusicFinder()
    print("Testing search...")
    test_query = "man delam nemikhast shayea"
    result = finder.find_best_match(test_query)
    
    if result:
        print("Found:")
        print(f"Title: {result['title']}")
        print(f"Artist: {result['artist']}")
        print(f"Type: {result['type'].upper()}")
        print(f"ID: {result['yt_id']}")
    else:
        print("Nothing found.")

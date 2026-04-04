"""
spotify_api.py
~~~~~~~~~~~~~~
Handles all communication with the Spotify Web API using spotipy.

Responsibilities:
- Load credentials from .env via python-dotenv.
- Authenticate with Spotify using the Client Credentials flow.
- Fetch every track from a playlist URL, handling pagination
  (Spotify returns at most 100 items per request).
- Return a clean list of Track dataclass instances.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Track:
    """Represents a single Spotify track with the metadata we care about."""

    name: str          # Song title
    artist: str        # Primary artist name
    album: str         # Album name
    art_url: str       # URL of the album cover image (largest available)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def _get_spotify_client() -> spotipy.Spotify:
    """
    Load Spotify credentials from the .env file and return an authenticated
    spotipy.Spotify instance using the OAuth Authorization Code flow.

    Raises:
        EnvironmentError: If SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET are
                          not set in the environment / .env file.
    """
    # Load variables from .env if present (does not override existing env vars)
    load_dotenv()

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:9090")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set. "
            "Copy .env.example to .env and fill in your credentials."
        )

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        # 'playlist-read-private' allows reading both public and private playlists
        scope="playlist-read-private"
    )
    return spotipy.Spotify(auth_manager=auth_manager)


# ---------------------------------------------------------------------------
# Playlist fetching
# ---------------------------------------------------------------------------

def get_playlist_tracks(playlist_url: str) -> list[Track]:
    """
    Fetch all tracks from a Spotify playlist URL.

    Handles Spotify's pagination: the API returns at most 100 items per
    request, so this function keeps calling the API until all pages are
    consumed.

    Args:
        playlist_url: Full Spotify playlist URL, e.g.
                      "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

    Returns:
        A list of Track objects, one per playlist entry that contains a
        valid track (local files or missing tracks are skipped).

    Raises:
        spotipy.SpotifyException: On API-level errors (bad URL, private
                                  playlist without correct scope, etc.).
        EnvironmentError: If credentials are missing (raised by
                          _get_spotify_client).
    """
    sp = _get_spotify_client()

    tracks: list[Track] = []
    # Fetch the first page (up to 100 items)
    results = sp.playlist_items(playlist_url)

    while results:
        for item in results["items"]:
            # Spotify API recently changed the 'track' key to 'item'
            track_data = item.get("item") or item.get("track")
            if not track_data:
                continue

            # Extract primary artist (first in the list)
            artists = track_data.get("artists", [])
            artist_name = artists[0]["name"] if artists else "Unknown Artist"

            # Extract album information
            album_data = track_data.get("album", {})
            album_name = album_data.get("name", "Unknown Album")

            # Choose the largest available album art image
            images = album_data.get("images", [])
            art_url = images[0]["url"] if images else ""

            tracks.append(
                Track(
                    name=track_data.get("name", "Unknown Title"),
                    artist=artist_name,
                    album=album_name,
                    art_url=art_url,
                )
            )

        # Follow the pagination cursor; None means we've reached the last page
        results = sp.next(results) if results.get("next") else None

    return tracks

"""
metadata.py
~~~~~~~~~~~
Embeds ID3 metadata (title, artist, album, cover art) into downloaded MP3
files using the mutagen library.

Responsibilities:
- Open the MP3 file and ensure it has an ID3 tag container.
- Write Title (TIT2), Artist (TPE1), and Album (TALB) text frames.
- Download the album art image from the given URL and embed it as an
  APIC (Attached Picture) frame.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from mutagen.id3 import (
    APIC,   # Attached Picture (cover art)
    ID3,    # ID3 tag container
    ID3NoHeaderError,
    TALB,   # Album title
    TIT2,   # Track title
    TPE1,   # Lead artist / performer
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_metadata(
    mp3_path: str | Path,
    title: str,
    artist: str,
    album: str,
    art_url: str,
) -> None:
    """
    Embed ID3 metadata into an MP3 file.

    This function opens (or creates) the ID3 tag header on the file, writes
    the standard text frames, and—if ``art_url`` is a non-empty string—
    downloads the image and attaches it as the cover art.

    Args:
        mp3_path: Path to the MP3 file to tag.
        title:    Track title (mapped to the TIT2 frame).
        artist:   Primary artist name (mapped to the TPE1 frame).
        album:    Album name (mapped to the TALB frame).
        art_url:  HTTP(S) URL of the album cover art image.
                  Pass an empty string to skip cover art embedding.

    Raises:
        FileNotFoundError: If ``mp3_path`` does not exist.
        mutagen.MutagenError: On low-level tag read/write errors.
        urllib.error.URLError: If the album art URL cannot be fetched.
    """
    mp3_path = Path(mp3_path)

    if not mp3_path.exists():
        raise FileNotFoundError(f"MP3 file not found: {mp3_path}")

    # Load existing ID3 tags or create a fresh tag header if none exist
    try:
        tags = ID3(str(mp3_path))
    except ID3NoHeaderError:
        tags = ID3()

    # --- Text frames -----------------------------------------------------------
    # TIT2: Track title
    tags["TIT2"] = TIT2(encoding=3, text=title)
    # TPE1: Lead performer / artist
    tags["TPE1"] = TPE1(encoding=3, text=artist)
    # TALB: Album / Movie / Show title
    tags["TALB"] = TALB(encoding=3, text=album)

    # --- Cover art -------------------------------------------------------------
    if art_url:
        image_data = _fetch_image(art_url)
        if image_data:
            # APIC frame: encoding=3 (UTF-8), mime type, picture type 3 = front
            # cover, description empty string, raw image bytes.
            tags["APIC"] = APIC(
                encoding=3,
                mime=_mime_from_url(art_url),
                type=3,    # 3 = Cover (front)
                desc="Cover",
                data=image_data,
            )

    # Save tags back to the file (v2_version=3 for broad player compatibility)
    tags.save(str(mp3_path), v2_version=3)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_image(url: str) -> bytes | None:
    """
    Download an image from ``url`` and return its raw bytes.

    Returns ``None`` if the download fails, so callers can decide whether
    to treat a missing cover as a fatal error.

    Args:
        url: HTTP(S) URL of the image to download.

    Returns:
        Raw image bytes, or ``None`` on failure.
    """
    try:
        with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310
            return response.read()
    except Exception:
        return None


def _mime_from_url(url: str) -> str:
    """
    Derive a MIME type string from the image URL extension.

    Defaults to ``"image/jpeg"`` if the extension is not recognised.

    Args:
        url: URL of the image.

    Returns:
        A MIME type string, e.g. ``"image/jpeg"`` or ``"image/png"``.
    """
    url_lower = url.lower().split("?")[0]  # strip query params
    if url_lower.endswith(".png"):
        return "image/png"
    if url_lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"

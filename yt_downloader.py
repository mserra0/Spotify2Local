"""
yt_downloader.py
~~~~~~~~~~~~~~~~
Handles searching for tracks on YouTube and downloading them as MP3 files
using yt-dlp.

Responsibilities:
- Sanitize file names to remove characters that are illegal on common
  operating systems (Windows, macOS, Linux).
- Skip the download if the target MP3 already exists (idempotent).
- Configure yt-dlp to extract the best audio and convert it to MP3.
- Return the full path of the downloaded file so callers can tag it.
"""

from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# File-name sanitization
# ---------------------------------------------------------------------------

# Characters that are forbidden in file names on Windows, macOS, or Linux.
_ILLEGAL_CHARS_RE = re.compile(r'[<>:"/\\|?*]')


def sanitize_filename(name: str) -> str:
    """
    Remove characters that are illegal in file names on major operating
    systems and strip leading/trailing whitespace.

    Illegal characters removed: ``< > : " / \\ | ? *``

    Args:
        name: The raw string to sanitize (e.g. a track title).

    Returns:
        A sanitized string safe to use as a file name.

    Examples:
        >>> sanitize_filename('AC/DC: Highway to Hell')
        'ACDC Highway to Hell'
        >>> sanitize_filename('What "is" this?')
        'What is this'
    """
    sanitized = _ILLEGAL_CHARS_RE.sub("", name)
    return sanitized.strip()


# ---------------------------------------------------------------------------
# Downloading
# ---------------------------------------------------------------------------

def download_track(
    track_name: str,
    artist: str,
    output_dir: str | Path = "downloads",
) -> str | None:
    """
    Search YouTube for ``"{artist} {track_name} official audio"`` and
    download the first result as an MP3 file.

    The function is *idempotent*: if an MP3 with the expected file name
    already exists in ``output_dir`` it is returned immediately without
    re-downloading.

    Args:
        track_name: Title of the track (e.g. ``"Bohemian Rhapsody"``).
        artist:     Primary artist name (e.g. ``"Queen"``).
        output_dir: Directory where MP3 files are saved.
                    Defaults to ``"downloads"`` in the current working dir.

    Returns:
        The absolute path to the downloaded (or already existing) MP3 file,
        or ``None`` if the download failed.
    """
    # Lazy import so that projects that don't need yt-dlp can still import
    # the sanitize_filename helper without paying the yt-dlp import cost.
    import yt_dlp  # noqa: PLC0415

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Build a safe file name from artist + track name
    safe_name = sanitize_filename(f"{artist} - {track_name}")
    expected_mp3 = output_path / f"{safe_name}.mp3"

    # Skip if already downloaded
    if expected_mp3.exists():
        return str(expected_mp3)

    # Build the YouTube search query
    search_query = f"ytsearch1:{artist} {track_name} official audio"

    # yt-dlp options:
    #   - format: best available audio
    #   - postprocessors: convert to MP3 via ffmpeg
    #   - outtmpl: output file name template (without extension)
    #   - quiet / no_warnings: suppress console noise (rich handles output)
    ydl_opts: dict = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # yt-dlp appends the correct extension automatically
        "outtmpl": str(output_path / f"{safe_name}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        # Do not write any extra metadata/thumbnail files
        "writethumbnail": False,
        "writeinfojson": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
    except yt_dlp.utils.DownloadError as exc:
        # Surface the error to the caller rather than swallowing it silently
        raise RuntimeError(f"yt-dlp failed to download '{track_name}': {exc}") from exc

    # Verify the file was actually created after download
    if expected_mp3.exists():
        return str(expected_mp3)

    return None

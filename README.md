# Spotify2Local

Turn any Spotify playlist into an offline MP3 library with embedded metadata (title, artist, album, cover art).

## Features

- Fetches tracks from a Spotify playlist
- Searches and downloads audio from YouTube as MP3
- Embeds ID3 metadata and album art into each file
- Shows live progress and per-track failures in the terminal
- Skips tracks already downloaded (idempotent behavior)

## Requirements

- Python 3.11+
- `ffmpeg` (required by `yt-dlp` to convert audio to MP3)
- Spotify Developer credentials:
  - `SPOTIPY_CLIENT_ID`
  - `SPOTIPY_CLIENT_SECRET`

## Installation

### 1) Clone the repository

```bash
git clone https://github.com/mserra0/Spotify2Local.git
cd Spotify2Local
```

### 2) Install dependencies

#### Option A: with `uv` (recommended if you use it)

```bash
uv sync
```

#### Option B: with `pip`

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 3) Install `ffmpeg`

Make sure `ffmpeg` is available in your PATH.

- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS (Homebrew): `brew install ffmpeg`
- Windows: install FFmpeg and add it to PATH

## Spotify API Setup

1. Go to the Spotify Developer Dashboard: <https://developer.spotify.com/dashboard>
2. Create an app.
3. Copy your Client ID and Client Secret.
4. Create a `.env` file from the template:

```bash
cp .env.example .env
```

5. Fill in values in `.env`:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id_here
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret_here
```

## Usage

Run the CLI:

```bash
spotify2local
```

or:

```bash
python main.py
```

When prompted, paste a Spotify playlist URL (for example):

```text
https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

Downloaded files are saved in:

```text
downloads/
```

## How It Works

1. Loads Spotify credentials from `.env`
2. Fetches all playlist tracks (with pagination)
3. For each track:
   - Searches YouTube (`artist + track + official audio`)
   - Downloads and converts to MP3
   - Writes ID3 tags and cover art
4. Prints a summary of successes/failures

## Troubleshooting

- **`SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set`**
  - Ensure `.env` exists and contains valid values.
- **`yt-dlp` download/conversion issues**
  - Verify internet access and that `ffmpeg` is installed.
- **Playlist fetch errors**
  - Check the playlist URL and ensure it is accessible with app credentials.
- **Some tracks fail**
  - This can happen when no suitable YouTube match is found. The tool continues with remaining tracks.

## Notes

- This project is intended for personal/offline use.
- Ensure your usage complies with Spotify, YouTube, and local copyright laws.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

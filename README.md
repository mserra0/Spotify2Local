<div align="center">

# 🎵 Spotify2Local

**Turn any Spotify playlist into an organized, high-quality offline audio library.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Textual](https://img.shields.io/badge/UI-Textual-green?logo=terminal&logoColor=white)](https://textual.textualize.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#-features) • [Installation](#-installation) • [Setup](#-setup) • [Usage](#-usage) • [Limitations](#-limitations)

</div>

---

## ✨ Features

- **🚀 Concurrent Downloads:** Download up to 4 tracks simultaneously for maximum speed.
- **🖥️ Modern TUI:** A sophisticated terminal interface built with Textual, featuring a searchable playlist menu and real-time progress bars.
- **📂 Automatic Organization:** Tracks are automatically saved into folders named after their playlists.
- **🏷️ Intelligent Tagging:** Automatically embeds ID3 metadata (Title, Artist, Album) and high-resolution cover art into every MP3.
- **🔍 Smart Search:** Finds the best audio match on YouTube using advanced search queries.

---

## 🛠️ Installation

This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Spotify2Local.git
   cd Spotify2Local
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

---

## 🔑 Setup (Spotify API)

To use this tool, you must create a Spotify Developer Application.

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Click **Create App**:
   - **App name:** `Spotify2Local`
   - **Redirect URI:** `http://127.0.0.1:9090` (⚠️ **Important:** Must match exactly, no trailing slash).
3. Open **Settings** and copy your **Client ID** and **Client Secret**.
4. Create a `.env` file in the project root:
   ```bash
   SPOTIPY_CLIENT_ID="your_id_here"
   SPOTIPY_CLIENT_SECRET="your_secret_here"
   SPOTIPY_REDIRECT_URI="http://127.0.0.1:9090"
   ```

---

## 🚀 Usage

Launch the interactive TUI:

```bash
uv run main.py
```

### ⌨️ Controls
- **Arrows / Type:** Search and navigate your playlists.
- **Enter:** Select the highlighted playlist and start downloading.
- **Type '0':** Switch to manual URL entry mode.
- **Esc:** Exit or go back.

---

## ⚠️ Limitations

Please read these before using the tool:

1. **User Authentication Required:** Due to recent Spotify API changes, you must authenticate as a user. You can only view and download playlists that are in your library (owned or followed).
2. **Editorial Playlists:** Spotify restricts third-party access to official editorial playlists (e.g., *Top 50 - Global*). If you encounter a `403 Forbidden` error, it is likely an API restriction on that specific playlist.
3. **YouTube Matching:** This tool finds audio by searching YouTube. While highly accurate, the audio quality depends on the availability of "Official Audio" videos on YouTube.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

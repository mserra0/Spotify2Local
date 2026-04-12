<p align="center">
  <img src="assets/banner.png" alt="Spotify2Local Banner" width="100%">
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11%2B-14354C?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/Managed%20by-uv-18181B?style=for-the-badge&color=A855F7" alt="Managed by uv">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-18181B?style=for-the-badge&color=FBBF24" alt="License: MIT">
  </a>
</p>


<p align="center">
  <a href="#features">
    <img src="https://img.shields.io/badge/Features-18181B?style=for-the-badge" alt="Features">
  </a>
  <a href="#installation">
    <img src="https://img.shields.io/badge/Installation-18181B?style=for-the-badge" alt="Installation">
  </a>
  <a href="#configuration">
    <img src="https://img.shields.io/badge/Config-18181B?style=for-the-badge" alt="Configuration">
  </a>
  <a href="#usage">
    <img src="https://img.shields.io/badge/Usage-18181B?style=for-the-badge" alt="Usage">
  </a>
  <a href="#contributing">
    <img src="https://img.shields.io/badge/Contributing-18181B?style=for-the-badge" alt="Contributing">
  </a>
</p>

Spotify2Local is a zero-friction terminal utility that bridges your Spotify library with your local storage. Built with a responsive TUI, it automatically resolves tracks, fetches the highest quality audio via YouTube, and precisely tags your files with ID3 metadata—all without the setup headache.

![Demo](assets/demo.gif)

## Features

- **Stupid-simple setup:** Works flawlessly out of the box with sensible defaults, while exposing deep configuration options for power users who want control.
- **Flawless local libraries:** Your music player will thank you. Automatically embeds pristine ID3 tags and high-res cover art for a perfectly organized archive.
- **Studio-grade audio:** Usig a smart-matching heuristics automatically bypass messy music videos and live performances to secure the highest-quality official tracks.
- **Modern TUI** No massive list of CLI flags to memorize. Just launch the TUI, search with your keyboard, and watch the progress bars fly.

## Installation

Spotify2Local uses [`uv`](https://github.com/astral-sh/uv) for fast, reliable dependency management. 

Clone the repository and sync the environment:

```bash
git clone [https://github.com/mserra0/Spotify2Local.git](https://github.com/mserra0/Spotify2Local.git)
cd Spotify2Local
uv sync
````

## Configuration

Before running the application, you need to provide your Spotify API credentials.

1.  Create an application in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2.  Set your redirect URI to `http://127.0.0.1:9090`.
3.  Copy the `.env.example` file to `.env` and apply your credentials. ALL DONE!

<!-- end list -->

```bash
cp .env.example .env
```

```env
SPOTIPY_CLIENT_ID="your_client_id"
SPOTIPY_CLIENT_SECRET="your_client_secret"
SPOTIPY_REDIRECT_URI="[http://127.0.0.1:9090](http://127.0.0.1:9090)"
```

## Usage

Launch the interactive interface:

```bash
uv run main.py
```

### Controls

| Key | Action |
| :--- | :--- |
| `↑` / `↓` | Navigate playlists |
| `Enter` | Download selected playlist |
| `0` | Enter a Spotify URL manually |
| `Esc` | Go back or exit |


> [!IMPORTANT]
> - **Library Requirement:** The tool can only process playlists saved to your authenticated account. To download a public playlist, simply open it in Spotify, click the `...` menu, and select **Add to Your Library** before running the tool.
> - **Editorial Restrictions:** Spotify restricts direct API access to certain official editorial playlists, which may result in a `403 Forbidden` error. **The fix:** Create a new personal playlist, copy all the tracks from the editorial playlist into it, and download your personal playlist instead.

## Contributing

We love community contributions. If you'd like to help improve Spotify2Local, whether it's fixing a bug or adding a new TUI feature, please review our [Contributing Guide](CONTRIBUTING.md) for instructions on setting up your local environment and submitting a pull request.

## Acknowledgements ❤️

This project stands on the shoulders of giants. A special thanks to the maintainers of the following open-source tools:

  - **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** For handling the heavy lifting of smart audio matching, downloading, and network reliability from YouTube.
  - **[Textual](https://github.com/textualize/textual) & [Rich](https://github.com/textualize/rich):** For powering the beautiful, responsive terminal user interface.
  - **[vhs](https://github.com/charmbracelet/vhs):** For generating the high-quality terminal recording used in this documentation.

## License

[MIT](https://www.google.com/search?q=LICENSE)

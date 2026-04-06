from __future__ import annotations
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from textual.app import App, ComposeResult
from textual.widgets import Input, ListView, ListItem, Footer, Label, Static, ProgressBar, Button
from textual.containers import Vertical, Horizontal, Container
from textual.binding import Binding
from textual.screen import Screen
from textual.worker import Worker, WorkerState
from rich.text import Text
import pyfiglet

from . import spotify_api
from . import yt_downloader
from . import metadata

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("downloads")
MAX_WORKERS = 4

# ---------------------------------------------------------------------------
# Shared Widgets
# ---------------------------------------------------------------------------

class Banner(Static):
    """A custom banner with Figlet ASCII art and a color gradient."""
    def compose(self) -> ComposeResult:
        fig = pyfiglet.Figlet(font='slant')
        ascii_art = fig.renderText('Spotify2Local')
        lines = ascii_art.splitlines()
        styled_text = Text()
        for i, line in enumerate(lines):
            color = "#1DB954" if i < len(lines) // 2 else "#1ED760"
            styled_text.append(line + "\n", style=f"bold {color}")
        yield Label(styled_text, id="app-title")
        yield Label("[dim]Turn any Spotify playlist into an offline audio library.[/dim]", id="app-subtitle")

# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class PlaylistItem(ListItem):
    """A single playlist in the list."""
    def __init__(self, playlist: spotify_api.PlaylistInfo) -> None:
        super().__init__()
        self.playlist = playlist

    def compose(self) -> ComposeResult:
        yield Label(f"[bold cyan]{self.playlist.name}[/bold cyan]")
        yield Label(f"[dim]{self.playlist.track_count} tracks[/dim]", classes="track-count")

class SelectionScreen(Screen[spotify_api.PlaylistInfo | str]):
    """The main playlist selection screen."""
    
    BINDINGS = [
        Binding("escape", "app.quit", "Exit"),
        Binding("enter", "select", "Select"),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
    ]

    def __init__(self, playlists: list[spotify_api.PlaylistInfo]) -> None:
        super().__init__()
        self.all_playlists = playlists

    def compose(self) -> ComposeResult:
        yield Vertical(
            Banner(),
            Input(placeholder="Search your playlists...", id="search-input"),
            ListView(id="playlist-list"),
            Static("Enter: Select | Esc: Exit | 0: Enter URL Manually", id="help-text"),
            id="container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.update_list("")

    def on_key(self, event: Binding) -> None:
        try:
            list_view = self.query_one(ListView)
            if event.key == "up":
                list_view.action_cursor_up()
                event.stop()
            elif event.key == "down":
                list_view.action_cursor_down()
                event.stop()
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        search_term = event.value.lower()
        if search_term == "0":
            self.dismiss("manual")
            return
        self.update_list(search_term)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        list_view = self.query_one(ListView)
        if list_view.highlighted_child:
            self.dismiss(list_view.highlighted_child.playlist)

    def update_list(self, filter_text: str) -> None:
        list_view = self.query_one(ListView)
        list_view.clear()
        starts_with = []
        contains = []
        for pl in self.all_playlists:
            name_lower = pl.name.lower()
            if not filter_text or name_lower.startswith(filter_text):
                starts_with.append(pl)
            elif filter_text in name_lower:
                contains.append(pl)
        for pl in (starts_with + contains):
            list_view.append(PlaylistItem(pl))
        if list_view.children:
            list_view.index = 0

    def action_select(self) -> None:
        list_view = self.query_one(ListView)
        if list_view.highlighted_child:
            self.dismiss(list_view.highlighted_child.playlist)

class ManualUrlScreen(Screen[str]):
    """Screen for entering a manual Spotify URL."""
    def compose(self) -> ComposeResult:
        yield Vertical(
            Banner(),
            Label("[bold cyan]Enter Spotify Playlist URL:[/bold cyan]"),
            Input(placeholder="https://open.spotify.com/playlist/...", id="manual-url-input"),
            Static("Enter: Download | Esc: Back to Selection", id="help-text"),
            id="container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.dismiss(event.value.strip())

    def on_key(self, event: Binding) -> None:
        if event.key == "escape":
            self.dismiss("")

class DownloadScreen(Screen):
    """Shows the progress of downloading a playlist."""

    BINDINGS = [
        Binding("enter", "back", "Back to Selection", show=False),
        Binding("escape", "back", "Back", show=False),
    ]

    def __init__(self, playlist_url: str) -> None:
        super().__init__()
        self.playlist_url = playlist_url
        self.tracks: list[spotify_api.Track] = []
        self.playlist_name: str = ""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Banner(),
            Label("[yellow]Preparing download...", id="status-label"),
            ProgressBar(total=100, show_percentage=True, id="download-progress"),
            ListView(id="log-view"),
            Button("Back to Selection", id="back-btn", variant="primary"),
            id="container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#log-view").can_focus = False
        self.query_one("#back-btn").display = False
        self.run_worker(self.start_pipeline, thread=True)

    def start_pipeline(self) -> None:
        try:
            self.app.call_from_thread(self.update_status, "[yellow]Fetching tracks from Spotify...[/yellow]")
            self.playlist_name, self.tracks = spotify_api.get_playlist_tracks(self.playlist_url)
            
            if not self.tracks:
                self.app.call_from_thread(self.update_status, "[red]Playlist is empty.[/red]")
                self.app.call_from_thread(self.show_back_button)
                return

            self.app.call_from_thread(self.update_status, f"[green]Downloading [bold]{len(self.tracks)}[/bold] tracks from [bold]{self.playlist_name}[/bold][/green]")
            self.app.call_from_thread(self.setup_progress, len(self.tracks))

            safe_name = yt_downloader.sanitize_filename(self.playlist_name)
            playlist_dir = OUTPUT_DIR / safe_name
            playlist_dir.mkdir(parents=True, exist_ok=True)

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {
                    executor.submit(self.download_and_tag, track, playlist_dir): track 
                    for track in self.tracks
                }
                
                for future in as_completed(futures):
                    success, track, error = future.result()
                    self.app.call_from_thread(self.log_result, success, track, error)
            
            self.app.call_from_thread(self.update_status, f"[bold green]Done![/bold green] Files saved to {playlist_dir.name}")
            self.app.call_from_thread(self.show_back_button)

        except Exception as exc:
            self.app.call_from_thread(self.handle_error, exc)
            self.app.call_from_thread(self.show_back_button)

    def update_status(self, text: str) -> None:
        self.query_one("#status-label", Label).update(text)

    def setup_progress(self, total: int) -> None:
        prog = self.query_one("#download-progress", ProgressBar)
        prog.total = total
        prog.progress = 0

    def log_result(self, success: bool, track: spotify_api.Track, error: str) -> None:
        log = self.query_one("#log-view", ListView)
        if success:
            log.append(ListItem(Label(f"[green]✓[/green] {track.artist} - {track.name}")))
        else:
            log.append(ListItem(Label(f"[red]✗ {track.artist} - {track.name}[/red]: {error}")))
        self.query_one("#download-progress", ProgressBar).advance(1)
        log.scroll_end()

    def handle_error(self, exc: Exception) -> None:
        from spotipy.exceptions import SpotifyException
        status = self.query_one("#status-label", Label)
        log = self.query_one("#log-view", ListView)
        if isinstance(exc, SpotifyException) and exc.http_status == 403:
            status.update("[bold red]Access Forbidden (403)[/bold red]")
            log.append(ListItem(Label("[red]Spotify restricted access to this playlist.[/red]")))
        else:
            status.update(f"[bold red]Error:[/bold red] {exc}")

    def show_back_button(self) -> None:
        btn = self.query_one("#back-btn", Button)
        btn.display = True
        btn.focus()

    def download_and_tag(self, track: spotify_api.Track, playlist_dir: Path) -> tuple[bool, spotify_api.Track, str]:
        try:
            mp3_path = yt_downloader.download_track(track.name, track.artist, playlist_dir)
            if not mp3_path: return False, track, "No file path"
            metadata.embed_metadata(Path(mp3_path), track.name, track.artist, track.album, track.art_url)
            return True, track, ""
        except Exception as e:
            return False, track, str(e)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.dismiss()

    def action_back(self) -> None:
        """Handle Enter/Esc keys to return if the download is finished."""
        if self.query_one("#back-btn").display:
            self.dismiss()

class Spotify2LocalApp(App):
    """The full Spotify2Local TUI application."""
    
    CSS_PATH = "App.css"
    playlists: list[spotify_api.PlaylistInfo] = []
    
    def on_mount(self) -> None:
        self.run_worker(self.load_initial_data, thread=True)

    def load_initial_data(self) -> None:
        try:
            self.playlists = spotify_api.get_user_playlists()
            self.call_from_thread(self.show_selection)
        except Exception as e:
            self.call_from_thread(self.notify, f"Could not fetch playlists: {e}", severity="error")
            self.call_from_thread(self.show_selection)

    def show_selection(self) -> None:
        self.push_screen(SelectionScreen(self.playlists), self.handle_selection)

    def handle_selection(self, result: spotify_api.PlaylistInfo | str | None) -> None:
        if result == "manual":
            self.push_screen(ManualUrlScreen(), self.handle_manual_url)
        elif isinstance(result, spotify_api.PlaylistInfo):
            self.push_screen(DownloadScreen(result.url), self.handle_download_finished)
        elif result is None:
            self.exit()

    def handle_manual_url(self, url: str | None) -> None:
        if url:
            self.push_screen(DownloadScreen(url), self.handle_download_finished)
        else:
            self.show_selection()

    def handle_download_finished(self, _) -> None:
        self.show_selection()

if __name__ == "__main__":
    app = Spotify2LocalApp()
    app.run()

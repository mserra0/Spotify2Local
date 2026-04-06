from textual.app import App, ComposeResult
from textual.widgets import Input, ListView, ListItem, Footer, Label, Static
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from rich.text import Text
import pyfiglet
import spotify_api

class Banner(Static):
    """A custom banner with Figlet ASCII art and a color gradient."""
    def compose(self) -> ComposeResult:
        # Generate Figlet ASCII art
        fig = pyfiglet.Figlet(font='slant')
        ascii_art = fig.renderText('Spotify2Local')
        
        # Apply a green gradient to the ASCII art manually
        lines = ascii_art.splitlines()
        styled_text = Text()
        
        for i, line in enumerate(lines):
            # Calculate color interpolation from #1DB954 to #1ED760
            # For simplicity in terminal, we can use a simpler approach or a few steps
            color = "#1DB954" if i < len(lines) // 2 else "#1ED760"
            styled_text.append(line + "\n", style=f"bold {color}")
        
        yield Label(styled_text, id="app-title")
        yield Label("[dim]Turn any Spotify playlist into an offline audio library.[/dim]", id="app-subtitle")

class PlaylistItem(ListItem):
    """A single playlist in the list."""
    def __init__(self, playlist: spotify_api.PlaylistInfo) -> None:
        super().__init__()
        self.playlist = playlist

    def compose(self) -> ComposeResult:
        yield Label(f"[bold cyan]{self.playlist.name}[/bold cyan]")
        yield Label(f"[dim]{self.playlist.track_count} tracks[/dim]", classes="track-count")

class PlaylistSelector(App[spotify_api.PlaylistInfo | str | None]):
    """A searchable TUI for selecting a Spotify playlist."""

    CSS_PATH = "App.css"

    BINDINGS = [
        Binding("escape", "quit", "Exit"),
        Binding("enter", "select", "Select"),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
    ]

    def __init__(self, playlists: list[spotify_api.PlaylistInfo]) -> None:
        super().__init__()
        self.all_playlists = playlists
        self.filtered_playlists = playlists

    def compose(self) -> ComposeResult:
        with Vertical(id="container"):
            yield Banner()
            yield Input(placeholder="Type to search your playlists...", id="search-input")
            yield ListView(id="playlist-list")
            yield Static("Enter: Select | Esc: Exit | 0: Enter URL Manually", id="help-text")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.update_list("")

    def on_key(self, event: Binding) -> None:
        """Proxy arrow keys to the ListView even when Input is focused."""
        list_view = self.query_one(ListView)
        if event.key == "up":
            list_view.action_cursor_up()
            event.stop()
        elif event.key == "down":
            list_view.action_cursor_down()
            event.stop()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter the list based on search input."""
        search_term = event.value.lower()
        if search_term == "0":
            # Special case for manual URL entry
            self.exit("manual")
            return
        self.update_list(search_term)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key being pressed in the search input."""
        list_view = self.query_one(ListView)
        if list_view.highlighted_child:
            self.exit(list_view.highlighted_child.playlist)

    def update_list(self, filter_text: str) -> None:
        list_view = self.query_one(ListView)
        list_view.clear()
        
        # Split playlists into "starts with" and "contains" for better sorting
        starts_with = []
        contains = []
        
        for pl in self.all_playlists:
            name_lower = pl.name.lower()
            if not filter_text:
                starts_with.append(pl)
            elif name_lower.startswith(filter_text):
                starts_with.append(pl)
            elif filter_text in name_lower:
                contains.append(pl)
        
        # Combine them: starts-with matches come first
        sorted_results = starts_with + contains
        
        for pl in sorted_results:
            list_view.append(PlaylistItem(pl))
        
        # Force the highlight to the first item
        if list_view.children:
            list_view.index = 0
        else:
            list_view.index = None

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of a playlist."""
        if isinstance(event.item, PlaylistItem):
            self.exit(event.item.playlist)

    def action_select(self) -> None:
        """Trigger selection on Enter."""
        list_view = self.query_one(ListView)
        if list_view.highlighted_child:
            self.exit(list_view.highlighted_child.playlist)

def select_playlist(playlists: list[spotify_api.PlaylistInfo]) -> spotify_api.PlaylistInfo | str | None:
    """Run the TUI and return the selected playlist or 'manual'."""
    app = PlaylistSelector(playlists)
    return app.run()

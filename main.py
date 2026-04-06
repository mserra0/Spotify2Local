"""
main.py
~~~~~~~
Entry point for the Spotify2Local CLI tool.

Workflow:
1. Print a welcome banner using rich.
2. Prompt the user for a Spotify playlist URL.
3. Fetch all tracks from the playlist via spotify_api.
4. For each track:
   a. Download the audio as MP3 via yt_downloader.
   b. Embed ID3 metadata and cover art via metadata.
5. Show a live progress bar and per-track status using rich.
   Failures are displayed in red but do not stop the loop.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from spotipy.exceptions import SpotifyException

import metadata
import spotify_api
import yt_downloader
import tui

from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("downloads")
MAX_WORKERS = 4  # Number of simultaneous downloads

# ---------------------------------------------------------------------------
# Rich console (shared across the module)
# ---------------------------------------------------------------------------

console = Console()


# ---------------------------------------------------------------------------
# Track processing worker
# ---------------------------------------------------------------------------

def process_track(track: spotify_api.Track, playlist_dir: Path) -> tuple[bool, spotify_api.Track, Exception | None]:
    """
    Download and tag a single track. Returns (success, track, exception).
    """
    try:
        # Step 1: Download audio from YouTube
        mp3_path = yt_downloader.download_track(
            track_name=track.name,
            artist=track.artist,
            output_dir=playlist_dir,
        )

        if mp3_path is None:
            return False, track, RuntimeError("Download returned no file path.")

        # Step 2: Embed ID3 metadata
        metadata.embed_metadata(
            mp3_path=mp3_path,
            title=track.name,
            artist=track.artist,
            album=track.album,
            art_url=track.art_url,
        )

        return True, track, None

    except Exception as exc:  # noqa: BLE001
        return False, track, exc


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run the Spotify2Local CLI.

    Orchestrates the full download-and-tag pipeline with a rich terminal UI.
    """
    while True:
        # ── Gather playlists ──────────────────────────────────────────────────
        console.print("\n[yellow]Fetching your Spotify playlists…[/yellow]")
        try:
            user_playlists = spotify_api.get_user_playlists()
        except Exception as exc:  # noqa: BLE001
            console.print(f"[bold red]Failed to fetch your playlists:[/bold red] {exc}")
            return

        playlist_url = ""
        if not user_playlists:
            console.print("[yellow]No playlists found in your account.[/yellow]")
            playlist_url = Prompt.ask("[bold cyan]Enter Spotify Playlist URL manually[/bold cyan]").strip()
        else:
            # Use the new sophisticated TUI for selection
            result = tui.select_playlist(user_playlists)
            
            if result == "manual":
                playlist_url = Prompt.ask("[bold cyan]Enter Spotify Playlist URL manually[/bold cyan]").strip()
            elif isinstance(result, spotify_api.PlaylistInfo):
                playlist_url = result.url
                console.print(f"[green]Selected: [bold]{result.name}[/bold][/green]")
            else:
                # User quit or cancelled
                console.print("[dim]Exiting...[/dim]")
                break

        if not playlist_url:
            break

        # ── Fetch track list ──────────────────────────────────────────────────
        console.print("\n[yellow]Fetching playlist tracks from Spotify…[/yellow]")
        try:
            playlist_name, tracks = spotify_api.get_playlist_tracks(playlist_url)
        except SpotifyException as exc:
            if exc.http_status == 403:
                console.print(Panel(
                    "[bold red]Access Forbidden (403)[/bold red]\n\n"
                    "Spotify has restricted access to this playlist. This usually happens because:\n"
                    "1. [bold]Editorial Restrictions:[/bold] Spotify has restricted third-party access to official \n"
                    "   editorial playlists (like 'Top 50') for newer Application IDs.\n"
                    "2. [bold]Private Playlist:[/bold] You might not have permission to view this specific playlist.\n"
                    "3. [bold]Developer Mode:[/bold] Your Spotify App is in 'Development Mode' and this user \n"
                    "   has not been whitelisted in the Spotify Dashboard.",
                    title="[bold red]Spotify API Error[/bold red]",
                    border_style="red",
                    padding=(1, 2)
                ))
            else:
                console.print(f"[bold red]Spotify API Error ({exc.http_status}):[/bold red] {exc.msg}")
            
            if Prompt.ask("\n[bold cyan]Try another playlist?[/bold cyan]", choices=["y", "n"], default="y") == "y":
                continue
            else:
                break
        except EnvironmentError as exc:
            console.print(f"[bold red]Configuration error:[/bold red] {exc}")
            break
        except Exception as exc:  # noqa: BLE001
            console.print(f"[bold red]Failed to fetch playlist:[/bold red] {exc}")
            if Prompt.ask("\n[bold cyan]Try again?[/bold cyan]", choices=["y", "n"], default="y") == "y":
                continue
            else:
                break

        if not tracks:
            console.print("[yellow]Playlist is empty or could not be read.[/yellow]")
            if Prompt.ask("\n[bold cyan]Try another?[/bold cyan]", choices=["y", "n"], default="y") == "y":
                continue
            else:
                break

        total = len(tracks)
        console.print(f"[green]Found [bold]{total}[/bold] track(s) in [bold]{playlist_name}[/bold]. Starting concurrent download…[/green]\n")

        # Ensure output directory exists (playlist-specific subfolder)
        safe_playlist_name = yt_downloader.sanitize_filename(playlist_name)
        playlist_dir = OUTPUT_DIR / safe_playlist_name
        playlist_dir.mkdir(parents=True, exist_ok=True)

        # ── Progress bar ──────────────────────────────────────────────────────
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False,
        )

        success_count = 0
        failure_count = 0

        with progress:
            task_id = progress.add_task("[cyan]Downloading tracks…", total=total)

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit all tracks to the pool
                future_to_track = {
                    executor.submit(process_track, track, playlist_dir): track
                    for track in tracks
                }

                for future in as_completed(future_to_track):
                    success, track, exc = future.result()

                    if success:
                        success_count += 1
                    else:
                        failure_count += 1
                        progress.console.print(
                            f"  [bold red]✗[/bold red] "
                            f"[red]{track.artist} – {track.name}[/red]: {exc}"
                        )

                    # Update the progress bar
                    progress.advance(task_id)
                    progress.update(
                        task_id,
                        description=f"[cyan]Completed {success_count + failure_count}/{total} tracks"
                    )

    # ── Summary ───────────────────────────────────────────────────────────
        console.print()
        console.print(
            Panel.fit(
                f"[bold green]Done![/bold green]\n"
                f"[green]✓ {success_count} track(s) downloaded successfully.[/green]\n"
                f"[red]✗ {failure_count} track(s) failed.[/red]\n"
                f"[dim]Files saved to: {playlist_dir.resolve()}[/dim]",
                border_style="green" if failure_count == 0 else "yellow",
            )
        )

        if Prompt.ask("\n[bold cyan]Would you like to download another playlist?[/bold cyan]", choices=["y", "n"], default="n") == "n":
            break


if __name__ == "__main__":
    main()

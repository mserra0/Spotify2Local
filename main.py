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
from rich.prompt import Prompt

import metadata
import spotify_api
import yt_downloader

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("downloads")

# ---------------------------------------------------------------------------
# Rich console (shared across the module)
# ---------------------------------------------------------------------------

console = Console()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run the Spotify2Local CLI.

    Orchestrates the full download-and-tag pipeline with a rich terminal UI.
    """
    # ── Welcome banner ────────────────────────────────────────────────────
    console.print(
        Panel.fit(
            "[bold green]Spotify2Local[/bold green]\n"
            "[dim]Turn any Spotify playlist into an offline audio library.[/dim]",
            border_style="green",
        )
    )

    # ── Gather input ──────────────────────────────────────────────────────
    playlist_url = Prompt.ask(
        "[bold cyan]Enter Spotify Playlist URL[/bold cyan]"
    ).strip()

    if not playlist_url:
        console.print("[bold red]No URL provided. Exiting.[/bold red]")
        return

    # ── Fetch track list ──────────────────────────────────────────────────
    console.print("\n[yellow]Fetching playlist tracks from Spotify…[/yellow]")
    try:
        tracks = spotify_api.get_playlist_tracks(playlist_url)
    except EnvironmentError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        return
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Failed to fetch playlist:[/bold red] {exc}")
        return

    if not tracks:
        console.print("[yellow]Playlist is empty or could not be read.[/yellow]")
        return

    total = len(tracks)
    console.print(f"[green]Found [bold]{total}[/bold] track(s). Starting download…[/green]\n")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
        task_id = progress.add_task("[cyan]Downloading…", total=total)

        for track in tracks:
            # Update the progress description with the current track
            progress.update(
                task_id,
                description=f"[cyan]{track.artist} – {track.name}[/cyan]",
            )

            try:
                # Step 1: Download audio from YouTube
                mp3_path = yt_downloader.download_track(
                    track_name=track.name,
                    artist=track.artist,
                    output_dir=OUTPUT_DIR,
                )

                if mp3_path is None:
                    raise RuntimeError("Download returned no file path.")

                # Step 2: Embed ID3 metadata
                metadata.embed_metadata(
                    mp3_path=mp3_path,
                    title=track.name,
                    artist=track.artist,
                    album=track.album,
                    art_url=track.art_url,
                )

                success_count += 1

            except Exception as exc:  # noqa: BLE001
                # Print a red error message but continue to the next track
                failure_count += 1
                progress.console.print(
                    f"  [bold red]✗[/bold red] "
                    f"[red]{track.artist} – {track.name}[/red]: {exc}"
                )

            finally:
                # Always advance the progress bar
                progress.advance(task_id)

    # ── Summary ───────────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel.fit(
            f"[bold green]Done![/bold green]\n"
            f"[green]✓ {success_count} track(s) downloaded successfully.[/green]\n"
            f"[red]✗ {failure_count} track(s) failed.[/red]\n"
            f"[dim]Files saved to: {OUTPUT_DIR.resolve()}[/dim]",
            border_style="green" if failure_count == 0 else "yellow",
        )
    )


if __name__ == "__main__":
    main()

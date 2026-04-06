"""
main.py
~~~~~~~
Entry point for the Spotify2Local TUI application.
"""

from src.tui import Spotify2LocalApp

def main() -> None:
    """
    Run the Spotify2Local TUI.
    """
    app = Spotify2LocalApp()
    app.run()

if __name__ == "__main__":
    main()

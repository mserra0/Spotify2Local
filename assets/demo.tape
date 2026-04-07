Output demo.gif

# Ensure the package manager is available
Require uv

# Terminal aesthetics for a premium look
Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 800
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful
Set BorderRadius 10
Set Padding 20
Set PlaybackSpeed 1.0
Set Margin 20
Set MarginFill "#674EFF"
Set BorderRadius 10

# Hide the initial prompt clearing for a cleaner start
Hide
Type "clear"
Enter
Show

# 1. Start the application
Sleep 1s
Type "uv run main.py"
Sleep 500ms
Enter

# 2. Wait for the Textual UI to load and fetch playlists
Sleep 1.5s

# 3. Simulate searching for a specific playlist
Type "Debí tirar"
Sleep 1.5s
Backspace 10
Sleep 2s

# 4. Navigate the playlist menu
Down 1
Sleep 500ms
Down 1
Sleep 500ms
Down 1
Sleep 500ms
Up 1
Sleep 500ms
Up 1
Sleep 500ms

# 5. Select the playlist and start downloading
Enter

# 6. Let the visualizer and progress bars run so the user sees the concurrent downloads
Sleep 3.7s

# 7. Exit the application
Escape
Sleep 2s

# Contributing to Spotify2Local

First off, thank you for considering contributing to Spotify2Local. 

We want to keep this tool fast, reliable, and incredibly simple to use. Whether you are fixing a bug, adding a new feature to the TUI, or improving the documentation, your help is appreciated.

## The Golden Rule

Before writing any code for a major new feature, please **open an issue first** to discuss it. This ensures your time isn't wasted on a feature that might fall outside the scope of the project.

## Local Development Setup

Spotify2Local uses [`uv`](https://github.com/astral-sh/uv) to keep dependency management fast and isolated.

1. **Fork the repository** to your own GitHub account.
2. **Clone your fork** locally:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Spotify2Local.git](https://github.com/YOUR_USERNAME/Spotify2Local.git)
   cd Spotify2Local
   ```
3. **Sync the environment:**
   ```bash
   uv sync
   ```
4. **Set up your environment variables:** Copy the `.env.example` to `.env` and add your Spotify Developer credentials so you can test the application locally.
   ```bash
   cp .env.example .env
   ```

## Workflow

We follow a standard GitHub Flow workflow.

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```
2. Make your changes and test them locally by running the TUI:
   ```bash
   uv run main.py
   ```
3. Commit your changes with a clear, descriptive commit message.
4. Push the branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a **Pull Request** against the `main` branch of this repository.

## Code Style & Standards

To maintain the quality and readability of the codebase, please adhere to the following guidelines:

- **Type Hints:** This project requires Python 3.11+. Please use strict type hinting for all new functions and methods.
- **The TUI:** We use `Textual` and `Rich`. If you are adding UI elements, ensure they remain responsive and follow the existing dark-mode terminal aesthetic. Avoid adding unnecessary visual clutter.
- **Keep it fast:** If you are modifying the downloading or matching logic, ensure it does not introduce blocking operations that freeze the UI.

> [!NOTE]
> **Testing API Limits:** If you are working on the audio fetching mechanics, please test responsibly. Rapid, repeated calls to the Spotify API or YouTube extraction endpoints during development can result in temporary IP bans.

## Reporting Bugs

If you find a bug but don't have the time to fix it yourself, please open an issue. Include:
- Your operating system and terminal emulator.
- The exact command you ran.
- The traceback or error message.
- Steps to reproduce the issue.

---
*Thank you for helping make Spotify2Local better.*

# Contributing to Spotify2Local

Thank you for your interest in contributing to **Spotify2Local**! We appreciate your help in making this tool even better.

## 🚀 How to Contribute

### 1. Reporting Bugs
- Check the [Issues](https://github.com/yourusername/Spotify2Local/issues) to see if the bug has already been reported.
- If not, open a new issue with a clear description, steps to reproduce, and any relevant logs or screenshots.

### 2. Requesting Features
- Open an issue and label it as a "feature request."
- Describe the feature you'd like to see and why it would be useful.

### 3. Submitting Pull Requests
1. **Fork** the repository and create your branch from `main`.
2. **Install** the development dependencies using `uv sync`.
3. **Make** your changes, ensuring you follow the project's coding style (PEP 8).
4. **Test** your changes to ensure they don't introduce regressions.
5. **Commit** your changes with a clear and concise message.
6. **Submit** your pull request for review.

## 🛠️ Development Setup

1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and Setup:**
   ```bash
   git clone https://github.com/yourusername/Spotify2Local.git
   cd Spotify2Local
   uv sync
   ```

3. **Running the TUI in Debug Mode:**
   ```bash
   uv run textual run --dev main.py
   ```

## 📜 Code of Conduct
Please be respectful and helpful in all your interactions. Our goal is to maintain a positive and welcoming community.

## 💎 License
By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

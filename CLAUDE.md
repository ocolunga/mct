# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mct (macOS Configuration Tools) is a CLI tool for managing macOS settings. It uses Typer for the CLI framework and subprocess calls to `defaults` for modifying macOS preferences.

## Development Commands

```bash
# Install dependencies (uses uv)
uv pip install -e ".[dev]"

# Run the CLI
uv run mct --help

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
uv run ruff format src/
```

## Architecture

The CLI follows a command-group pattern using Typer:

- `src/mct/cli.py` - Main entry point, creates the Typer app and registers command groups
- `src/mct/commands/` - Each file exports a `typer.Typer()` instance that gets added via `app.add_typer()`
  - `dock.py` - Dock settings (size, auto-hide, lock)
  - `keyboard.py` - Keyboard settings (key hold/repeat)
  - `system.py` - System settings (Touch ID for sudo)

### Adding New Commands

1. For a new command in an existing group, add a function decorated with `@<group>_app.command()` in the appropriate file
2. For a new command group, create a new file in `commands/`, export a `typer.Typer()` instance, and register it in `cli.py` with `app.add_typer()`

### macOS Settings Pattern

Commands modify settings via `subprocess.run()` calling `defaults write/read`. Many dock commands require `killall Dock` afterward to apply changes.

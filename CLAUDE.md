# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mct (macOS Configuration Tools) is a declarative CLI tool for managing macOS settings, inspired by nix-darwin. It uses Typer for the CLI framework and subprocess calls to `defaults` for modifying macOS preferences.

## Development Commands

```bash
# Install dependencies (uses uv)
uv sync --group dev

# Run the CLI
uv run mct --help

# Type checking (ty)
uv run ty check src/

# Linting and formatting (ruff)
uv run ruff check src/
uv run ruff format src/
```

## Architecture

### Core Modules

- `src/mct/cli.py` - Main entry point, registers command groups and declarative commands (apply, export, diff, init, settings)
- `src/mct/config.py` - Configuration management: YAML loading/saving, settings registry, diff computation
- `src/mct/defaults.py` - Low-level helper for macOS `defaults` read/write/delete operations

### Command Groups

Each file in `src/mct/commands/` exports a `typer.Typer()` instance registered in `cli.py`:
- `dock.py` - Dock settings (size, auto-hide, lock)
- `finder.py` - Finder settings (extensions, hidden files, path bar, view style)
- `keyboard.py` - Keyboard settings (key hold/repeat)
- `screenshot.py` - Screenshot settings (location, format, shadow)
- `system.py` - System settings (Touch ID for sudo)

### Settings Registry

All declarative settings are defined in `config.py` in the `SETTINGS` dict. Each setting specifies:
- `domain`: The macOS defaults domain (e.g., `com.apple.dock`)
- `key`: The defaults key
- `value_type`: Type hint (`bool`, `int`, `float`, `string`)
- `restart_app`: App to restart after changing (e.g., `Dock`, `Finder`)

### Adding New Settings

1. Add the setting to `SETTINGS` dict in `config.py`
2. Optionally add an imperative command in the appropriate `commands/*.py` file

### Config File

Users can define desired state in `~/.config/mct/config.yaml`:
```yaml
dock:
  size: 48
  autohide: true
finder:
  show_extensions: true
  show_path_bar: true
```

Then apply with `mct apply` or preview changes with `mct diff`.

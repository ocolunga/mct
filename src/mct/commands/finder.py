"""Finder settings management."""

from typing import Optional

import typer

from ..defaults import read, write, restart_app

finder_app = typer.Typer()

ON_VALUES = ("on", "true", "1", "yes")
OFF_VALUES = ("off", "false", "0", "no")


def parse_bool(value: str) -> bool | None:
    """Parse a boolean string value."""
    if value.lower() in ON_VALUES:
        return True
    if value.lower() in OFF_VALUES:
        return False
    return None


@finder_app.command()
def extensions(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set showing all file extensions."""
    if value is None:
        current = read("NSGlobalDomain", "AppleShowAllExtensions")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("NSGlobalDomain", "AppleShowAllExtensions", parsed, "bool")
    restart_app("Finder")
    typer.echo(f"File extensions {'shown' if parsed else 'hidden'}")


@finder_app.command()
def hidden(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set showing hidden files (dotfiles)."""
    if value is None:
        current = read("com.apple.finder", "AppleShowAllFiles")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.finder", "AppleShowAllFiles", parsed, "bool")
    restart_app("Finder")
    typer.echo(f"Hidden files {'shown' if parsed else 'hidden'}")


@finder_app.command()
def pathbar(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set showing path bar at bottom."""
    if value is None:
        current = read("com.apple.finder", "ShowPathbar")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.finder", "ShowPathbar", parsed, "bool")
    restart_app("Finder")
    typer.echo(f"Path bar {'shown' if parsed else 'hidden'}")


@finder_app.command()
def statusbar(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set showing status bar at bottom."""
    if value is None:
        current = read("com.apple.finder", "ShowStatusBar")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.finder", "ShowStatusBar", parsed, "bool")
    restart_app("Finder")
    typer.echo(f"Status bar {'shown' if parsed else 'hidden'}")


VIEW_STYLES = {
    "icon": "icnv",
    "list": "Nlsv",
    "column": "clmv",
    "gallery": "glyv",
}
VIEW_STYLES_REVERSE = {v: k for k, v in VIEW_STYLES.items()}


@finder_app.command()
def view(style: Optional[str] = typer.Argument(None, help="icon/list/column/gallery")):
    """Get or set default Finder view style."""
    if style is None:
        current = read("com.apple.finder", "FXPreferredViewStyle")
        name = VIEW_STYLES_REVERSE.get(current, current or "icon")
        typer.echo(name)
        return

    if style.lower() not in VIEW_STYLES:
        typer.echo(f"Error: use {', '.join(VIEW_STYLES.keys())}")
        raise typer.Exit(1)

    write("com.apple.finder", "FXPreferredViewStyle", VIEW_STYLES[style.lower()], "string")
    restart_app("Finder")
    typer.echo(f"Default view set to {style.lower()}")


SETTINGS_MAP = {
    "extensions": ("NSGlobalDomain", "AppleShowAllExtensions", "bool", True),
    "hidden": ("com.apple.finder", "AppleShowAllFiles", "bool", False),
    "pathbar": ("com.apple.finder", "ShowPathbar", "bool", False),
    "statusbar": ("com.apple.finder", "ShowStatusBar", "bool", False),
    "view": ("com.apple.finder", "FXPreferredViewStyle", "string", "icnv"),
}


@finder_app.command()
def reset(setting: Optional[str] = typer.Argument(None, help="Setting to reset (or omit for all)")):
    """Reset Finder settings to macOS defaults."""
    if setting is None:
        for name, (domain, key, vtype, default) in SETTINGS_MAP.items():
            write(domain, key, default, vtype)
            display = default if vtype != "bool" else ("on" if default else "off")
            typer.echo(f"  {name}: reset to {display}")
        restart_app("Finder")
        typer.echo("All Finder settings reset")
        return

    if setting not in SETTINGS_MAP:
        typer.echo(f"Error: unknown setting '{setting}'")
        typer.echo(f"Available: {', '.join(SETTINGS_MAP.keys())}")
        raise typer.Exit(1)

    domain, key, vtype, default = SETTINGS_MAP[setting]
    write(domain, key, default, vtype)
    restart_app("Finder")
    display = default if vtype != "bool" else ("on" if default else "off")
    typer.echo(f"Finder {setting} reset to {display}")

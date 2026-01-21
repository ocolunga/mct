"""Dock settings management."""

from typing import Optional

import typer

from ..defaults import read, write, restart_app

dock_app = typer.Typer()

# Valid values for on/off commands
ON_VALUES = ("on", "true", "1", "yes")
OFF_VALUES = ("off", "false", "0", "no")


def parse_bool(value: str) -> bool | None:
    """Parse a boolean string value."""
    if value.lower() in ON_VALUES:
        return True
    if value.lower() in OFF_VALUES:
        return False
    return None


@dock_app.command()
def size(value: Optional[int] = typer.Argument(None, help="Size (32-128)")):
    """Get or set dock icon size."""
    if value is None:
        current = read("com.apple.dock", "tilesize")
        typer.echo(current if current else "64 (default)")
        return

    if not 32 <= value <= 128:
        typer.echo("Error: size must be between 32 and 128")
        raise typer.Exit(1)

    write("com.apple.dock", "tilesize", value, "int")
    restart_app("Dock")
    typer.echo(f"Dock size set to {value}")


@dock_app.command()
def autohide(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set dock auto-hide."""
    if value is None:
        current = read("com.apple.dock", "autohide")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.dock", "autohide", parsed, "bool")
    restart_app("Dock")
    typer.echo(f"Dock auto-hide {'enabled' if parsed else 'disabled'}")


@dock_app.command()
def locked(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set dock size lock."""
    if value is None:
        current = read("com.apple.dock", "size-immutable")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.dock", "size-immutable", parsed, "bool")
    restart_app("Dock")
    typer.echo(f"Dock size {'locked' if parsed else 'unlocked'}")


@dock_app.command()
def magnification(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set dock magnification."""
    if value is None:
        current = read("com.apple.dock", "magnification")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.dock", "magnification", parsed, "bool")
    restart_app("Dock")
    typer.echo(f"Dock magnification {'enabled' if parsed else 'disabled'}")


@dock_app.command()
def recents(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set showing recent apps in dock."""
    if value is None:
        current = read("com.apple.dock", "show-recents")
        typer.echo("on" if current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.dock", "show-recents", parsed, "bool")
    restart_app("Dock")
    typer.echo(f"Recent apps {'shown' if parsed else 'hidden'}")


POSITIONS = ("left", "bottom", "right")


@dock_app.command()
def position(value: Optional[str] = typer.Argument(None, help="left/bottom/right")):
    """Get or set dock position."""
    if value is None:
        current = read("com.apple.dock", "orientation")
        typer.echo(current if current else "bottom")
        return

    if value.lower() not in POSITIONS:
        typer.echo(f"Error: use {', '.join(POSITIONS)}")
        raise typer.Exit(1)

    write("com.apple.dock", "orientation", value.lower(), "string")
    restart_app("Dock")
    typer.echo(f"Dock position set to {value.lower()}")


SETTINGS_MAP = {
    "size": ("com.apple.dock", "tilesize", "int", 64),
    "autohide": ("com.apple.dock", "autohide", "bool", False),
    "locked": ("com.apple.dock", "size-immutable", "bool", False),
    "magnification": ("com.apple.dock", "magnification", "bool", False),
    "recents": ("com.apple.dock", "show-recents", "bool", True),
    "position": ("com.apple.dock", "orientation", "string", "bottom"),
}


@dock_app.command()
def reset(setting: Optional[str] = typer.Argument(None, help="Setting to reset (or omit for all)")):
    """Reset dock settings to macOS defaults."""
    if setting is None:
        # Reset all
        for name, (domain, key, vtype, default) in SETTINGS_MAP.items():
            write(domain, key, default, vtype)
            typer.echo(f"  {name}: reset to {default}")
        restart_app("Dock")
        typer.echo("All dock settings reset")
        return

    if setting not in SETTINGS_MAP:
        typer.echo(f"Error: unknown setting '{setting}'")
        typer.echo(f"Available: {', '.join(SETTINGS_MAP.keys())}")
        raise typer.Exit(1)

    domain, key, vtype, default = SETTINGS_MAP[setting]
    write(domain, key, default, vtype)
    restart_app("Dock")
    typer.echo(f"Dock {setting} reset to {default}")

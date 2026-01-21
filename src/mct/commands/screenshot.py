"""Screenshot settings management."""

from pathlib import Path
from typing import Optional

import typer

from ..defaults import read, write, restart_app

screenshot_app = typer.Typer()

ON_VALUES = ("on", "true", "1", "yes")
OFF_VALUES = ("off", "false", "0", "no")
FORMATS = ("png", "jpg", "gif", "pdf", "tiff")


def parse_bool(value: str) -> bool | None:
    """Parse a boolean string value."""
    if value.lower() in ON_VALUES:
        return True
    if value.lower() in OFF_VALUES:
        return False
    return None


@screenshot_app.command()
def location(path: Optional[str] = typer.Argument(None, help="Directory path")):
    """Get or set screenshot save location."""
    if path is None:
        current = read("com.apple.screencapture", "location")
        typer.echo(current if current else "~/Desktop (default)")
        return

    expanded = Path(path).expanduser().resolve()

    if not expanded.exists():
        typer.echo(f"Error: directory does not exist: {expanded}")
        raise typer.Exit(1)

    if not expanded.is_dir():
        typer.echo(f"Error: not a directory: {expanded}")
        raise typer.Exit(1)

    write("com.apple.screencapture", "location", str(expanded), "string")
    restart_app("SystemUIServer")
    typer.echo(f"Screenshot location set to {expanded}")


@screenshot_app.command()
def format(fmt: Optional[str] = typer.Argument(None, help="png/jpg/gif/pdf/tiff")):
    """Get or set screenshot file format."""
    if fmt is None:
        current = read("com.apple.screencapture", "type")
        typer.echo(current if current else "png (default)")
        return

    if fmt.lower() not in FORMATS:
        typer.echo(f"Error: use {', '.join(FORMATS)}")
        raise typer.Exit(1)

    write("com.apple.screencapture", "type", fmt.lower(), "string")
    restart_app("SystemUIServer")
    typer.echo(f"Screenshot format set to {fmt.lower()}")


@screenshot_app.command()
def shadow(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set window shadow in screenshots."""
    if value is None:
        # disable-shadow=true means shadow is OFF
        disabled = read("com.apple.screencapture", "disable-shadow")
        typer.echo("off" if disabled else "on")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    # Invert: shadow on = disable-shadow false
    write("com.apple.screencapture", "disable-shadow", not parsed, "bool")
    restart_app("SystemUIServer")
    typer.echo(f"Window shadow {'enabled' if parsed else 'disabled'}")


@screenshot_app.command()
def thumbnail(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set floating thumbnail after capture."""
    if value is None:
        current = read("com.apple.screencapture", "show-thumbnail")
        # Default is on if not set
        typer.echo("on" if current is None or current else "off")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    write("com.apple.screencapture", "show-thumbnail", parsed, "bool")
    restart_app("SystemUIServer")
    typer.echo(f"Floating thumbnail {'enabled' if parsed else 'disabled'}")


SETTINGS_MAP = {
    "location": ("com.apple.screencapture", "location", "string", str(Path.home() / "Desktop")),
    "format": ("com.apple.screencapture", "type", "string", "png"),
    "shadow": ("com.apple.screencapture", "disable-shadow", "bool", False),  # False = shadow ON
    "thumbnail": ("com.apple.screencapture", "show-thumbnail", "bool", True),
}


@screenshot_app.command()
def reset(setting: Optional[str] = typer.Argument(None, help="Setting to reset (or omit for all)")):
    """Reset screenshot settings to macOS defaults."""
    if setting is None:
        for name, (domain, key, vtype, default) in SETTINGS_MAP.items():
            write(domain, key, default, vtype)
            if name == "shadow":
                display = "on"  # disable-shadow=false means shadow is ON
            elif vtype == "bool":
                display = "on" if default else "off"
            else:
                display = default
            typer.echo(f"  {name}: reset to {display}")
        restart_app("SystemUIServer")
        typer.echo("All screenshot settings reset")
        return

    if setting not in SETTINGS_MAP:
        typer.echo(f"Error: unknown setting '{setting}'")
        typer.echo(f"Available: {', '.join(SETTINGS_MAP.keys())}")
        raise typer.Exit(1)

    domain, key, vtype, default = SETTINGS_MAP[setting]
    write(domain, key, default, vtype)
    restart_app("SystemUIServer")

    if setting == "shadow":
        display = "on"
    elif vtype == "bool":
        display = "on" if default else "off"
    else:
        display = default
    typer.echo(f"Screenshot {setting} reset to {display}")

"""Screenshot settings management."""

from pathlib import Path

import typer

from ..defaults import read, write, restart_app

screenshot_app = typer.Typer()

FORMATS = ["png", "jpg", "gif", "pdf", "tiff"]


@screenshot_app.command()
def location(
    path: str = typer.Argument(None, help="Directory path for screenshots"),
):
    """Set or show the screenshot save location."""
    if path is None:
        current = read("com.apple.screencapture", "location")
        if current:
            typer.echo(f"Screenshot location: {current}")
        else:
            typer.echo("Screenshot location: ~/Desktop (default)")
        return

    # Expand ~ and resolve path
    expanded = Path(path).expanduser().resolve()

    if not expanded.exists():
        typer.echo(f"Error: Directory does not exist: {expanded}")
        raise typer.Exit(1)

    if not expanded.is_dir():
        typer.echo(f"Error: Path is not a directory: {expanded}")
        raise typer.Exit(1)

    write("com.apple.screencapture", "location", str(expanded), "string")
    restart_app("SystemUIServer")
    typer.echo(f"Screenshot location set to: {expanded}")


@screenshot_app.command()
def format(
    fmt: str = typer.Argument(None, help=f"Format: {', '.join(FORMATS)}"),
):
    """Set or show the screenshot file format."""
    if fmt is None:
        current = read("com.apple.screencapture", "type")
        typer.echo(f"Screenshot format: {current or 'png (default)'}")
        return

    if fmt.lower() not in FORMATS:
        typer.echo(f"Invalid format. Choose from: {', '.join(FORMATS)}")
        raise typer.Exit(1)

    write("com.apple.screencapture", "type", fmt.lower(), "string")
    restart_app("SystemUIServer")
    typer.echo(f"Screenshot format set to: {fmt.lower()}")


@screenshot_app.command()
def shadow(
    enable: bool = typer.Option(None, "--enable/--disable", help="Enable or disable window shadow"),
):
    """Enable or disable window shadow in screenshots."""
    if enable is None:
        # Note: disable-shadow=true means shadow is disabled
        current = read("com.apple.screencapture", "disable-shadow")
        status = "disabled" if current else "enabled"
        typer.echo(f"Window shadow is currently {status}")
        return

    # Invert because the setting is "disable-shadow"
    write("com.apple.screencapture", "disable-shadow", not enable, "bool")
    restart_app("SystemUIServer")
    status = "enabled" if enable else "disabled"
    typer.echo(f"Window shadow is now {status}")


@screenshot_app.command()
def thumbnail(
    enable: bool = typer.Option(None, "--enable/--disable", help="Enable or disable floating thumbnail"),
):
    """Enable or disable the floating thumbnail after capture."""
    if enable is None:
        current = read("com.apple.screencapture", "show-thumbnail")
        # Default is true if not set
        status = "enabled" if current is None or current else "disabled"
        typer.echo(f"Floating thumbnail is currently {status}")
        return

    write("com.apple.screencapture", "show-thumbnail", enable, "bool")
    restart_app("SystemUIServer")
    status = "enabled" if enable else "disabled"
    typer.echo(f"Floating thumbnail is now {status}")


@screenshot_app.command()
def reset(
    location: bool = typer.Option(False, "-l", "--location", help="Reset screenshot location"),
    fmt: bool = typer.Option(False, "-f", "--format", help="Reset screenshot format"),
    shadow: bool = typer.Option(False, "-s", "--shadow", help="Reset window shadow"),
    thumbnail: bool = typer.Option(False, "-t", "--thumbnail", help="Reset floating thumbnail"),
    all: bool = typer.Option(False, "-a", "--all", help="Reset all screenshot settings"),
):
    """Reset screenshot settings to defaults."""
    if not any([location, fmt, shadow, thumbnail, all]):
        typer.echo("Error: Must specify at least one flag or -a for all")
        raise typer.Exit(1)

    if location or all:
        write("com.apple.screencapture", "location", str(Path.home() / "Desktop"), "string")
        typer.echo("Screenshot location: reset to ~/Desktop")

    if fmt or all:
        write("com.apple.screencapture", "type", "png", "string")
        typer.echo("Screenshot format: reset to png")

    if shadow or all:
        write("com.apple.screencapture", "disable-shadow", False, "bool")
        typer.echo("Window shadow: reset to enabled")

    if thumbnail or all:
        write("com.apple.screencapture", "show-thumbnail", True, "bool")
        typer.echo("Floating thumbnail: reset to enabled")

    restart_app("SystemUIServer")

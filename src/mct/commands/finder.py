"""Finder settings management."""

import typer

from ..defaults import read, write, restart_app

finder_app = typer.Typer()


@finder_app.command()
def extensions(
    show: bool = typer.Option(None, "--show/--hide", help="Show or hide file extensions"),
):
    """Show or hide all file extensions."""
    if show is None:
        current = read("NSGlobalDomain", "AppleShowAllExtensions")
        status = "shown" if current else "hidden"
        typer.echo(f"File extensions are currently {status}")
        return

    write("NSGlobalDomain", "AppleShowAllExtensions", show, "bool")
    restart_app("Finder")
    status = "shown" if show else "hidden"
    typer.echo(f"File extensions are now {status}")


@finder_app.command()
def hidden(
    show: bool = typer.Option(None, "--show/--hide", help="Show or hide hidden files"),
):
    """Show or hide hidden files (dotfiles)."""
    if show is None:
        current = read("com.apple.finder", "AppleShowAllFiles")
        status = "shown" if current else "hidden"
        typer.echo(f"Hidden files are currently {status}")
        return

    write("com.apple.finder", "AppleShowAllFiles", show, "bool")
    restart_app("Finder")
    status = "shown" if show else "hidden"
    typer.echo(f"Hidden files are now {status}")


@finder_app.command()
def pathbar(
    show: bool = typer.Option(None, "--show/--hide", help="Show or hide path bar"),
):
    """Show or hide the path bar at the bottom of Finder windows."""
    if show is None:
        current = read("com.apple.finder", "ShowPathbar")
        status = "shown" if current else "hidden"
        typer.echo(f"Path bar is currently {status}")
        return

    write("com.apple.finder", "ShowPathbar", show, "bool")
    restart_app("Finder")
    status = "shown" if show else "hidden"
    typer.echo(f"Path bar is now {status}")


@finder_app.command()
def statusbar(
    show: bool = typer.Option(None, "--show/--hide", help="Show or hide status bar"),
):
    """Show or hide the status bar at the bottom of Finder windows."""
    if show is None:
        current = read("com.apple.finder", "ShowStatusBar")
        status = "shown" if current else "hidden"
        typer.echo(f"Status bar is currently {status}")
        return

    write("com.apple.finder", "ShowStatusBar", show, "bool")
    restart_app("Finder")
    status = "shown" if show else "hidden"
    typer.echo(f"Status bar is now {status}")


VIEW_STYLES = {
    "icon": "icnv",
    "list": "Nlsv",
    "column": "clmv",
    "gallery": "glyv",
}
VIEW_STYLES_REVERSE = {v: k for k, v in VIEW_STYLES.items()}


@finder_app.command()
def view(
    style: str = typer.Argument(
        None, help="View style: icon, list, column, gallery"
    ),
):
    """Set the default Finder view style."""
    if style is None:
        current = read("com.apple.finder", "FXPreferredViewStyle")
        style_name = VIEW_STYLES_REVERSE.get(current, current)
        typer.echo(f"Default view style: {style_name}")
        return

    if style not in VIEW_STYLES:
        typer.echo(f"Invalid view style. Choose from: {', '.join(VIEW_STYLES.keys())}")
        raise typer.Exit(1)

    write("com.apple.finder", "FXPreferredViewStyle", VIEW_STYLES[style], "string")
    restart_app("Finder")
    typer.echo(f"Default view style set to: {style}")


@finder_app.command()
def reset(
    extensions: bool = typer.Option(False, "-e", "--extensions", help="Reset file extensions visibility"),
    hidden: bool = typer.Option(False, "-h", "--hidden", help="Reset hidden files visibility"),
    pathbar: bool = typer.Option(False, "-p", "--pathbar", help="Reset path bar visibility"),
    statusbar: bool = typer.Option(False, "-s", "--statusbar", help="Reset status bar visibility"),
    view: bool = typer.Option(False, "-v", "--view", help="Reset default view style"),
    all: bool = typer.Option(False, "-a", "--all", help="Reset all Finder settings"),
):
    """Reset Finder settings to defaults."""
    if not any([extensions, hidden, pathbar, statusbar, view, all]):
        typer.echo("Error: Must specify at least one flag or -a for all")
        raise typer.Exit(1)

    if extensions or all:
        write("NSGlobalDomain", "AppleShowAllExtensions", True, "bool")
        typer.echo("File extensions: reset to shown")

    if hidden or all:
        write("com.apple.finder", "AppleShowAllFiles", False, "bool")
        typer.echo("Hidden files: reset to hidden")

    if pathbar or all:
        write("com.apple.finder", "ShowPathbar", False, "bool")
        typer.echo("Path bar: reset to hidden")

    if statusbar or all:
        write("com.apple.finder", "ShowStatusBar", False, "bool")
        typer.echo("Status bar: reset to hidden")

    if view or all:
        write("com.apple.finder", "FXPreferredViewStyle", "icnv", "string")
        typer.echo("Default view: reset to icon")

    restart_app("Finder")

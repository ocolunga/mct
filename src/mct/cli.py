import importlib.metadata

import typer

from .commands.dock import dock_app
from .commands.finder import finder_app
from .commands.keyboard import keyboard_app
from .commands.screenshot import screenshot_app
from .commands.system import system_app
from .config import (
    CONFIG_PATH,
    SETTINGS,
    apply_config,
    compute_diff,
    flatten_config,
    load_config,
    read_current_state,
    save_config,
    unflatten_config,
)

app = typer.Typer()
app.add_typer(dock_app, name="dock", help="Manage dock settings")
app.add_typer(finder_app, name="finder", help="Manage Finder settings")
app.add_typer(keyboard_app, name="keyboard", help="Manage keyboard settings")
app.add_typer(screenshot_app, name="screenshot", help="Manage screenshot settings")
app.add_typer(system_app, name="system", help="Manage system settings")


def _version_callback(value: bool):
    if value:
        version = importlib.metadata.version("mct")
        typer.echo(f"mct version: {version}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show the version and exit.", callback=_version_callback
    )
):
    """macOS Configuration Tools - Manage macOS system settings declaratively."""
    pass


@app.command()
def apply(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would change without applying"),
    config_file: str = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Apply settings from config file to the system."""
    path = config_file if config_file else CONFIG_PATH

    if config_file:
        from pathlib import Path
        path = Path(config_file)
        if not path.exists():
            typer.echo(f"Error: Config file not found: {path}")
            raise typer.Exit(1)
        import yaml
        with open(path) as f:
            config = yaml.safe_load(f) or {}
    else:
        config = load_config()

    if not config:
        typer.echo(f"No config file found at {CONFIG_PATH}")
        typer.echo("Run 'mct export' to create one from current settings")
        raise typer.Exit(1)

    flat_config = flatten_config(config)

    # Filter to only known settings
    valid_config = {k: v for k, v in flat_config.items() if k in SETTINGS}
    unknown_keys = set(flat_config.keys()) - set(SETTINGS.keys())

    if unknown_keys:
        typer.echo(f"Warning: Unknown settings will be ignored: {', '.join(sorted(unknown_keys))}")

    diffs = apply_config(valid_config, dry_run=dry_run)

    if not diffs:
        typer.echo("System is already in sync with config")
        return

    if dry_run:
        typer.echo("Changes that would be applied:")
    else:
        typer.echo("Applied changes:")

    for diff in diffs:
        current = diff.current if diff.current is not None else "(not set)"
        typer.echo(f"  {diff.key}: {current} -> {diff.desired}")

    if dry_run:
        typer.echo(f"\nRun without --dry-run to apply {len(diffs)} change(s)")


@app.command()
def export(
    output: str = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
    save: bool = typer.Option(False, "--save", "-s", help=f"Save to {CONFIG_PATH}"),
):
    """Export current system settings to YAML."""
    import yaml

    current_state = read_current_state()
    config = unflatten_config(current_state)

    yaml_output = yaml.dump(config, default_flow_style=False, sort_keys=False)

    if save:
        save_config(config)
        typer.echo(f"Config saved to {CONFIG_PATH}")
    elif output:
        from pathlib import Path
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(yaml_output)
        typer.echo(f"Config exported to {output}")
    else:
        typer.echo(yaml_output)


@app.command()
def diff(
    config_file: str = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Show differences between config file and current system state."""
    if config_file:
        from pathlib import Path
        path = Path(config_file)
        if not path.exists():
            typer.echo(f"Error: Config file not found: {path}")
            raise typer.Exit(1)
        import yaml
        with open(path) as f:
            config = yaml.safe_load(f) or {}
    else:
        config = load_config()

    if not config:
        typer.echo(f"No config file found at {CONFIG_PATH}")
        typer.echo("Run 'mct export --save' to create one")
        raise typer.Exit(1)

    flat_config = flatten_config(config)
    valid_config = {k: v for k, v in flat_config.items() if k in SETTINGS}

    diffs = compute_diff(valid_config)

    if not diffs:
        typer.echo("System is in sync with config")
        return

    typer.echo(f"Found {len(diffs)} difference(s):\n")
    for d in diffs:
        current = d.current if d.current is not None else "(not set)"
        typer.echo(f"  {d.key}:")
        typer.echo(f"    current: {current}")
        typer.echo(f"    config:  {d.desired}")
        typer.echo()


@app.command()
def settings():
    """List all available settings."""
    typer.echo("Available settings:\n")

    # Group by category
    categories: dict[str, list[str]] = {}
    for key in sorted(SETTINGS.keys()):
        category = key.split(".")[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(key)

    for category, keys in categories.items():
        typer.echo(f"{category}:")
        for key in keys:
            setting = SETTINGS[key]
            typer.echo(f"  {key}: {setting.description}")
        typer.echo()


@app.command()
def init():
    """Create a starter config file with common settings."""
    if CONFIG_PATH.exists():
        if not typer.confirm(f"Config already exists at {CONFIG_PATH}. Overwrite?"):
            raise typer.Exit(0)

    starter_config = {
        "dock": {
            "size": 48,
            "autohide": False,
            "show_recents": False,
        },
        "finder": {
            "show_extensions": True,
            "show_hidden": False,
            "show_path_bar": True,
        },
        "screenshot": {
            "format": "png",
            "disable_shadow": True,
        },
        "keyboard": {
            "press_and_hold": False,
        },
    }

    save_config(starter_config)
    typer.echo(f"Created starter config at {CONFIG_PATH}")
    typer.echo("Edit the file, then run 'mct apply' to apply settings")


def main():
    app()


if __name__ == "__main__":
    main()

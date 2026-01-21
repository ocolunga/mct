"""Keyboard settings management."""

from typing import Optional

import typer

from ..defaults import read, write

keyboard_app = typer.Typer()

ON_VALUES = ("on", "true", "1", "yes")
OFF_VALUES = ("off", "false", "0", "no")


def parse_bool(value: str) -> bool | None:
    """Parse a boolean string value."""
    if value.lower() in ON_VALUES:
        return True
    if value.lower() in OFF_VALUES:
        return False
    return None


@keyboard_app.command()
def repeat(value: Optional[str] = typer.Argument(None, help="on/off")):
    """Get or set key repeat (off = press-and-hold for accents)."""
    if value is None:
        # ApplePressAndHoldEnabled=true means repeat is OFF (accents ON)
        press_hold = read("NSGlobalDomain", "ApplePressAndHoldEnabled")
        typer.echo("off" if press_hold else "on")
        return

    parsed = parse_bool(value)
    if parsed is None:
        typer.echo("Error: use 'on' or 'off'")
        raise typer.Exit(1)

    # Invert: repeat on = press-and-hold off
    write("NSGlobalDomain", "ApplePressAndHoldEnabled", not parsed, "bool")
    if parsed:
        typer.echo("Key repeat enabled (press-and-hold for accents disabled)")
    else:
        typer.echo("Key repeat disabled (press-and-hold for accents enabled)")
    typer.echo("Note: restart apps to apply")


SETTINGS_MAP = {
    "repeat": ("NSGlobalDomain", "ApplePressAndHoldEnabled", "bool", True),  # True = repeat OFF
}


@keyboard_app.command()
def reset(setting: Optional[str] = typer.Argument(None, help="Setting to reset (or omit for all)")):
    """Reset keyboard settings to macOS defaults."""
    if setting is None:
        for name, (domain, key, vtype, default) in SETTINGS_MAP.items():
            write(domain, key, default, vtype)
            # Default is press-and-hold ON (repeat OFF)
            typer.echo(f"  {name}: reset to off (press-and-hold enabled)")
        typer.echo("All keyboard settings reset")
        typer.echo("Note: restart apps to apply")
        return

    if setting not in SETTINGS_MAP:
        typer.echo(f"Error: unknown setting '{setting}'")
        typer.echo(f"Available: {', '.join(SETTINGS_MAP.keys())}")
        raise typer.Exit(1)

    domain, key, vtype, default = SETTINGS_MAP[setting]
    write(domain, key, default, vtype)
    typer.echo(f"Keyboard {setting} reset to off (press-and-hold enabled)")
    typer.echo("Note: restart apps to apply")

"""Configuration management for declarative macOS settings."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import defaults


CONFIG_PATH = Path.home() / ".config" / "mct" / "config.yaml"


@dataclass
class Setting:
    """Represents a macOS setting that can be read/written."""

    domain: str
    key: str
    value_type: str  # 'bool', 'int', 'float', 'string'
    restart_app: str | None = None  # App to restart after changing
    description: str = ""


# Registry of all supported settings
# Format: config_key -> Setting
SETTINGS: dict[str, Setting] = {
    # Dock settings
    "dock.size": Setting(
        domain="com.apple.dock",
        key="tilesize",
        value_type="int",
        restart_app="Dock",
        description="Dock icon size (32-128)",
    ),
    "dock.autohide": Setting(
        domain="com.apple.dock",
        key="autohide",
        value_type="bool",
        restart_app="Dock",
        description="Auto-hide the Dock",
    ),
    "dock.size_immutable": Setting(
        domain="com.apple.dock",
        key="size-immutable",
        value_type="bool",
        restart_app="Dock",
        description="Lock Dock size",
    ),
    "dock.magnification": Setting(
        domain="com.apple.dock",
        key="magnification",
        value_type="bool",
        restart_app="Dock",
        description="Enable Dock magnification",
    ),
    "dock.largesize": Setting(
        domain="com.apple.dock",
        key="largesize",
        value_type="int",
        restart_app="Dock",
        description="Magnified icon size (16-128)",
    ),
    "dock.orientation": Setting(
        domain="com.apple.dock",
        key="orientation",
        value_type="string",
        restart_app="Dock",
        description="Dock position: left, bottom, right",
    ),
    "dock.mineffect": Setting(
        domain="com.apple.dock",
        key="mineffect",
        value_type="string",
        restart_app="Dock",
        description="Minimize effect: genie, scale, suck",
    ),
    "dock.minimize_to_application": Setting(
        domain="com.apple.dock",
        key="minimize-to-application",
        value_type="bool",
        restart_app="Dock",
        description="Minimize windows into application icon",
    ),
    "dock.show_recents": Setting(
        domain="com.apple.dock",
        key="show-recents",
        value_type="bool",
        restart_app="Dock",
        description="Show recent applications in Dock",
    ),
    "dock.static_only": Setting(
        domain="com.apple.dock",
        key="static-only",
        value_type="bool",
        restart_app="Dock",
        description="Show only open applications",
    ),
    # Finder settings
    "finder.show_extensions": Setting(
        domain="NSGlobalDomain",
        key="AppleShowAllExtensions",
        value_type="bool",
        restart_app="Finder",
        description="Show all file extensions",
    ),
    "finder.show_hidden": Setting(
        domain="com.apple.finder",
        key="AppleShowAllFiles",
        value_type="bool",
        restart_app="Finder",
        description="Show hidden files",
    ),
    "finder.show_path_bar": Setting(
        domain="com.apple.finder",
        key="ShowPathbar",
        value_type="bool",
        restart_app="Finder",
        description="Show path bar at bottom",
    ),
    "finder.show_status_bar": Setting(
        domain="com.apple.finder",
        key="ShowStatusBar",
        value_type="bool",
        restart_app="Finder",
        description="Show status bar at bottom",
    ),
    "finder.default_view": Setting(
        domain="com.apple.finder",
        key="FXPreferredViewStyle",
        value_type="string",
        restart_app="Finder",
        description="Default view: icnv, Nlsv, clmv, glyv",
    ),
    "finder.search_scope": Setting(
        domain="com.apple.finder",
        key="FXDefaultSearchScope",
        value_type="string",
        restart_app="Finder",
        description="Search scope: SCcf (current folder), SCsp (previous scope), SCev (entire Mac)",
    ),
    "finder.empty_trash_warning": Setting(
        domain="com.apple.finder",
        key="WarnOnEmptyTrash",
        value_type="bool",
        restart_app="Finder",
        description="Warn before emptying trash",
    ),
    "finder.new_window_target": Setting(
        domain="com.apple.finder",
        key="NewWindowTarget",
        value_type="string",
        restart_app="Finder",
        description="New window target: PfHm (Home), PfDe (Desktop), PfDo (Documents), PfLo (other)",
    ),
    # Screenshot settings
    "screenshot.location": Setting(
        domain="com.apple.screencapture",
        key="location",
        value_type="string",
        restart_app="SystemUIServer",
        description="Screenshot save location",
    ),
    "screenshot.format": Setting(
        domain="com.apple.screencapture",
        key="type",
        value_type="string",
        restart_app="SystemUIServer",
        description="Screenshot format: png, jpg, gif, pdf, tiff",
    ),
    "screenshot.disable_shadow": Setting(
        domain="com.apple.screencapture",
        key="disable-shadow",
        value_type="bool",
        restart_app="SystemUIServer",
        description="Disable window shadow in screenshots",
    ),
    "screenshot.include_date": Setting(
        domain="com.apple.screencapture",
        key="include-date",
        value_type="bool",
        restart_app="SystemUIServer",
        description="Include date in screenshot filename",
    ),
    "screenshot.show_thumbnail": Setting(
        domain="com.apple.screencapture",
        key="show-thumbnail",
        value_type="bool",
        restart_app="SystemUIServer",
        description="Show floating thumbnail after capture",
    ),
    # Keyboard settings
    "keyboard.press_and_hold": Setting(
        domain="NSGlobalDomain",
        key="ApplePressAndHoldEnabled",
        value_type="bool",
        restart_app=None,
        description="Enable press-and-hold for accents (false = key repeat)",
    ),
    "keyboard.key_repeat_rate": Setting(
        domain="NSGlobalDomain",
        key="KeyRepeat",
        value_type="int",
        restart_app=None,
        description="Key repeat rate (lower = faster, 1-15)",
    ),
    "keyboard.initial_key_repeat": Setting(
        domain="NSGlobalDomain",
        key="InitialKeyRepeat",
        value_type="int",
        restart_app=None,
        description="Delay before key repeat starts (lower = faster, 10-120)",
    ),
    # Trackpad settings
    "trackpad.tap_to_click": Setting(
        domain="com.apple.AppleMultitouchTrackpad",
        key="Clicking",
        value_type="bool",
        restart_app=None,
        description="Enable tap to click",
    ),
    "trackpad.natural_scrolling": Setting(
        domain="NSGlobalDomain",
        key="com.apple.swipescrolldirection",
        value_type="bool",
        restart_app=None,
        description="Natural scrolling direction",
    ),
    "trackpad.tracking_speed": Setting(
        domain="NSGlobalDomain",
        key="com.apple.trackpad.scaling",
        value_type="float",
        restart_app=None,
        description="Tracking speed (0.0-3.0)",
    ),
    # Menu bar settings
    "menubar.autohide": Setting(
        domain="NSGlobalDomain",
        key="_HIHideMenuBar",
        value_type="bool",
        restart_app="SystemUIServer",
        description="Auto-hide menu bar",
    ),
    "menubar.show_background": Setting(
        domain="NSGlobalDomain",
        key="NSStatusBarShowsMenuBarBackground",
        value_type="bool",
        restart_app="SystemUIServer",
        description="Show menu bar background (Tahoe)",
    ),
    # Mission Control settings
    "mission_control.auto_rearrange": Setting(
        domain="com.apple.dock",
        key="mru-spaces",
        value_type="bool",
        restart_app="Dock",
        description="Automatically rearrange Spaces based on recent use",
    ),
    "mission_control.group_by_app": Setting(
        domain="com.apple.dock",
        key="expose-group-apps",
        value_type="bool",
        restart_app="Dock",
        description="Group windows by application",
    ),
    # Accessibility settings
    "accessibility.reduce_transparency": Setting(
        domain="com.apple.universalaccess",
        key="reduceTransparency",
        value_type="bool",
        restart_app=None,
        description="Reduce transparency (helps with Liquid Glass)",
    ),
    "accessibility.reduce_motion": Setting(
        domain="com.apple.universalaccess",
        key="reduceMotion",
        value_type="bool",
        restart_app=None,
        description="Reduce motion effects",
    ),
}


@dataclass
class ConfigDiff:
    """Represents differences between current state and config."""

    key: str
    current: Any
    desired: Any
    setting: Setting


def load_config() -> dict[str, Any]:
    """Load configuration from YAML file.

    Returns:
        Nested dict of configuration values
    """
    if not CONFIG_PATH.exists():
        return {}

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to YAML file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def flatten_config(config: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested config dict to dot-notation keys.

    Example: {'dock': {'size': 48}} -> {'dock.size': 48}
    """
    result = {}
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_config(value, full_key))
        else:
            result[full_key] = value
    return result


def unflatten_config(flat: dict[str, Any]) -> dict[str, Any]:
    """Unflatten dot-notation keys to nested dict.

    Example: {'dock.size': 48} -> {'dock': {'size': 48}}
    """
    result: dict[str, Any] = {}
    for key, value in flat.items():
        parts = key.split(".")
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def read_current_state() -> dict[str, Any]:
    """Read all supported settings from the system."""
    state = {}
    for key, setting in SETTINGS.items():
        value = defaults.read(setting.domain, setting.key)
        if value is not None:
            # Convert to proper type based on setting definition
            if setting.value_type == "bool":
                # macOS returns 0/1 for bools
                value = bool(value) if isinstance(value, int) else value
            state[key] = value
    return state


def compute_diff(config: dict[str, Any]) -> list[ConfigDiff]:
    """Compute differences between config and current system state.

    Args:
        config: Flattened config dict

    Returns:
        List of ConfigDiff for settings that differ
    """
    diffs = []
    current_state = read_current_state()

    for key, desired in config.items():
        if key not in SETTINGS:
            continue

        setting = SETTINGS[key]
        current = current_state.get(key)

        if current != desired:
            diffs.append(
                ConfigDiff(key=key, current=current, desired=desired, setting=setting)
            )

    return diffs


def apply_setting(key: str, value: Any) -> str | None:
    """Apply a single setting.

    Returns:
        App name that needs restart, or None
    """
    if key not in SETTINGS:
        raise ValueError(f"Unknown setting: {key}")

    setting = SETTINGS[key]
    defaults.write(setting.domain, setting.key, value, setting.value_type)
    return setting.restart_app


def apply_config(config: dict[str, Any], dry_run: bool = False) -> list[ConfigDiff]:
    """Apply configuration to the system.

    Args:
        config: Flattened config dict
        dry_run: If True, don't actually apply changes

    Returns:
        List of changes that were (or would be) applied
    """
    diffs = compute_diff(config)

    if dry_run:
        return diffs

    apps_to_restart: set[str] = set()

    for diff in diffs:
        restart_app = apply_setting(diff.key, diff.desired)
        if restart_app:
            apps_to_restart.add(restart_app)

    # Restart affected apps
    for app in apps_to_restart:
        defaults.restart_app(app)

    return diffs

"""Helper module for macOS defaults commands."""

import subprocess
from typing import Any


class DefaultsError(Exception):
    """Error when reading/writing macOS defaults."""

    pass


def read(domain: str, key: str) -> Any:
    """Read a value from macOS defaults.

    Args:
        domain: The defaults domain (e.g., 'com.apple.dock')
        key: The key to read

    Returns:
        The value, or None if not found

    Raises:
        DefaultsError: If there's an error reading the value
    """
    try:
        result = subprocess.run(
            ["defaults", "read", domain, key],
            capture_output=True,
            text=True,
            check=True,
        )
        value = result.stdout.strip()

        # Try to parse as int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass

        # Handle boolean strings
        if value in ("1", "true", "yes"):
            return True
        if value in ("0", "false", "no"):
            return False

        return value
    except subprocess.CalledProcessError:
        return None


def read_global(key: str) -> Any:
    """Read a value from global defaults (-g)."""
    return read("-g", key)


def write(domain: str, key: str, value: Any, value_type: str | None = None) -> None:
    """Write a value to macOS defaults.

    Args:
        domain: The defaults domain (e.g., 'com.apple.dock')
        key: The key to write
        value: The value to write
        value_type: Optional type hint ('bool', 'int', 'float', 'string')

    Raises:
        DefaultsError: If there's an error writing the value
    """
    cmd = ["defaults", "write", domain, key]

    if value_type == "bool" or isinstance(value, bool):
        cmd.extend(["-bool", "true" if value else "false"])
    elif value_type == "int" or isinstance(value, int):
        cmd.extend(["-int", str(value)])
    elif value_type == "float" or isinstance(value, float):
        cmd.extend(["-float", str(value)])
    else:
        cmd.append(str(value))

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise DefaultsError(f"Failed to write {domain} {key}: {e.stderr}") from e


def write_global(key: str, value: Any, value_type: str | None = None) -> None:
    """Write a value to global defaults (-g)."""
    write("-g", key, value, value_type)


def delete(domain: str, key: str) -> None:
    """Delete a key from macOS defaults."""
    try:
        subprocess.run(
            ["defaults", "delete", domain, key],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        pass  # Key might not exist


def restart_app(app_name: str) -> None:
    """Restart an application to apply changes.

    Args:
        app_name: The application name (e.g., 'Dock', 'Finder', 'SystemUIServer')
    """
    try:
        subprocess.run(
            ["killall", app_name],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        pass  # App might not be running

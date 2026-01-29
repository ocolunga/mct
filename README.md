# macOS Configuration Tools (mct)

A personal collection of CLI tools for managing macOS settings through a simple, intuitive interface.

## Features

Currently implemented:

### General
- Check version: `mct --version` or `mct -v` - Display the installed version

### Dock Management
- Set dock size: `mct dock size <value>` (32-128)
- Show current dock size: `mct dock size`
- Auto-hide controls:
  - `mct dock hide` - Enable auto-hide
  - `mct dock show` - Disable auto-hide
- Size lock controls:
  - `mct dock lock` - Lock dock size
  - `mct dock unlock` - Unlock dock size
- Reset options:
  - `mct dock reset -s` - Reset size to default (64)
  - `mct dock reset -h` - Reset auto-hide to default (disabled)
  - `mct dock reset -l` - Reset size lock to default (unlocked)
  - `mct dock reset -a` - Reset all dock settings
  
### Keyboard Management
- Key repeat controls:
  - `mct keyboard hold` - Enable press-and-hold for accented characters
  - `mct keyboard repeat` - Enable key repeat (disables accents)
- Reset options:
  - `mct keyboard reset -h` - Reset key hold to default (enabled)
  - `mct keyboard reset -a` - Reset all keyboard settings

### System Management
- Touch ID for sudo:
  - `mct system touchid` - Enable Touch ID authentication for sudo with interactive backup management
  - `mct system reset -t` - Reset Touch ID sudo configuration from backup
  - `mct system reset -a` - Reset all system settings to defaults

Planned features:
- Configuration file support (`~/.config/mct/config.toml`) for:
  - Setting default values for commands
  - Storing preferred configurations
  - Batch applying multiple settings at once
  - Example configuration:
    ```toml
    [dock]
    default_size = 48
    auto_hide = true
    size_locked = false

    [keyboard]
    key_hold = true

    [system]
    touch_id_sudo = true
    ```
- More dock management options
- System preferences management
- And more...

## Installation

### Using Homebrew (recommended)
```bash
# Add the tap repository
brew tap ocolunga/macos-config-tools

# Install macos-config-tools
brew install macos-config-tools
```

### Using pip
```bash
pip install macos-config-tools
```

### Using uv
```bash
uv tool install macos-config-tools
```

### From source
```bash
git clone https://github.com/ocolunga/mct.git
cd mct
uv sync
uv run mct --help
```

## Usage Examples

```bash
# Show help
mct --help
mct dock --help
mct keyboard --help
mct system --help

# Check version
mct --version

# Dock Examples
mct dock size 48          # Set dock size to 48
mct dock size            # Show current dock size
mct dock hide           # Enable auto-hide
mct dock show           # Disable auto-hide
mct dock lock           # Lock dock size
mct dock unlock         # Unlock dock size
mct dock reset -s -h    # Reset both size and auto-hide

# Keyboard Examples
mct keyboard hold      # Enable press-and-hold for accents
mct keyboard repeat    # Enable key repeat (disable accents)
mct keyboard reset -a  # Reset all keyboard settings

# System Examples
mct system touchid           # Enable Touch ID for sudo with interactive backup
mct system reset -t         # Reset Touch ID sudo configuration from backup
mct system reset -a         # Reset all system settings to defaults
```

Note: Some commands may require restarting applications to take effect.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

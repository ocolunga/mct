import subprocess
import typer

system_app = typer.Typer()


def print_file_contents(file_path):
    """Print the contents of a file."""
    try:
        result = subprocess.run(
            ["sudo", "cat", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
        typer.echo("\nFile contents:")
        typer.echo("=" * 50)
        typer.echo(result.stdout)
        typer.echo("=" * 50)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error reading file: {e}", err=True)


@system_app.command()
def touchid():
    """Enable Touch ID authentication for sudo commands."""
    try:
        # Show initial warning and get confirmation
        typer.echo("\n⚠️  This operation will:")
        typer.echo("  1. Check if Touch ID is already enabled")
        typer.echo(
            "  2. Add a new authentication line to /etc/pam.d/sudo if needed"
        )
        typer.echo("  3. Create or update a backup of the original file")
        typer.echo("  4. Require sudo privileges to make these changes")

        if not typer.confirm("\nDo you want to proceed?", default=False):
            typer.echo("Operation cancelled")
            return

        # Check if the line already exists
        result = subprocess.run(
            ["grep", "auth sufficient pam_tid.so", "/etc/pam.d/sudo"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            typer.echo("Touch ID for sudo is already enabled")
            return

        # Check if backup exists
        backup_exists = (
            subprocess.run(
                ["test", "-f", "/etc/pam.d/sudo.bak"],
                capture_output=True,
            ).returncode
            == 0
        )

        if backup_exists:
            while True:
                typer.echo(
                    "\n⚠️  A backup file already exists at /etc/pam.d/sudo.bak"
                )
                typer.echo("\nPlease choose an option:")
                typer.echo("0 - Do nothing and exit")
                typer.echo("1 - View the backup file contents")
                typer.echo("2 - Continue (will replace existing backup)")
                typer.echo("3 - Restore backup and then enable Touch ID")

                choice = typer.prompt(
                    "\nEnter your choice (0-3)", type=int, default=0
                )

                if choice == 0:
                    typer.echo("Operation cancelled")
                    return
                elif choice == 1:
                    print_file_contents("/etc/pam.d/sudo.bak")
                    continue
                elif choice == 2:
                    # Create a new backup of the current file
                    subprocess.run(
                        [
                            "sudo",
                            "cp",
                            "/etc/pam.d/sudo",
                            "/etc/pam.d/sudo.bak",
                        ],
                        check=True,
                    )
                    break
                elif choice == 3:
                    # Restore backup first
                    subprocess.run(
                        [
                            "sudo",
                            "cp",
                            "/etc/pam.d/sudo.bak",
                            "/etc/pam.d/sudo",
                        ],
                        check=True,
                    )
                    typer.echo("✓ Original sudo PAM file has been restored")
                    break
                else:
                    typer.echo("Invalid choice, please try again")
                    continue
        else:
            # Create a backup of the original file
            subprocess.run(
                ["sudo", "cp", "/etc/pam.d/sudo", "/etc/pam.d/sudo.bak"],
                check=True,
            )

        # Add the line at the top of the sudo PAM file using a temporary file
        subprocess.run(
            [
                "sudo",
                "sh",
                "-c",
                'echo "auth sufficient pam_tid.so" | cat - /etc/pam.d/sudo > /tmp/sudo.pam && sudo mv /tmp/sudo.pam /etc/pam.d/sudo',
            ],
            check=True,
        )
        typer.echo("✓ Touch ID for sudo has been enabled")
        typer.echo("✓ Original file backed up as /etc/pam.d/sudo.bak")

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error enabling Touch ID for sudo: {e}", err=True)
        raise typer.Exit(1)


@system_app.command()
def reset(
    touchid: bool = typer.Option(
        False, "-t", "--touchid", help="Reset Touch ID sudo configuration"
    ),
    all: bool = typer.Option(
        False, "-a", "--all", help="Reset all system settings to defaults"
    ),
):
    """Reset system settings. Must specify -t (touchid) or -a (all)."""
    if not any([touchid, all]):
        typer.echo("Error: Must specify either -t (touchid) or -a (all)")
        raise typer.Exit(1)

    try:
        if touchid or all:
            # Show warning and get confirmation first
            typer.echo("\n⚠️  This operation will:")
            typer.echo("  1. Remove Touch ID authentication from sudo")
            typer.echo("  2. Require sudo privileges to make these changes")

            if not typer.confirm("\nDo you want to proceed?", default=False):
                typer.echo("Operation cancelled")
                return

            # Check if Touch ID is enabled
            result = subprocess.run(
                ["grep", "auth sufficient pam_tid.so", "/etc/pam.d/sudo"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                typer.echo("Touch ID is not enabled in sudo configuration")
                return

            while True:
                typer.echo("\nPlease choose an option:")
                typer.echo("0 - Do nothing and exit")
                typer.echo("1 - View the backup file contents")
                typer.echo("2 - Restore from stored backup")

                choice = typer.prompt(
                    "\nEnter your choice (0-2)", type=int, default=0
                )

                if choice == 0:
                    typer.echo("Operation cancelled")
                    return
                elif choice == 1:
                    # Check if backup exists
                    result = subprocess.run(
                        ["test", "-f", "/etc/pam.d/sudo.bak"],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode != 0:
                        typer.echo(
                            "No backup file found at /etc/pam.d/sudo.bak"
                        )
                        return

                    print_file_contents("/etc/pam.d/sudo.bak")
                    continue
                elif choice == 2:
                    # Check if backup exists
                    result = subprocess.run(
                        ["test", "-f", "/etc/pam.d/sudo.bak"],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode != 0:
                        typer.echo(
                            "No backup file found at /etc/pam.d/sudo.bak"
                        )
                        return

                    # Restore the backup file
                    subprocess.run(
                        [
                            "sudo",
                            "cp",
                            "/etc/pam.d/sudo.bak",
                            "/etc/pam.d/sudo",
                        ],
                        check=True,
                    )
                    typer.echo(
                        "✓ Touch ID sudo configuration has been reset from backup"
                    )
                    break
                else:
                    typer.echo("Invalid choice, please try again")
                    continue

        if all:
            # Add more system settings here as they are implemented
            pass

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error resetting system settings: {e}", err=True)
        raise typer.Exit(1)

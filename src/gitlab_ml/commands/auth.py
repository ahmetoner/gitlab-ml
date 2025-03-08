from typing import Optional

import typer
from gitlab_ml.api.client import get_gitlab_client
from gitlab_ml.config import Config, load_config, save_config
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Authentication and access control")
console = Console()


@app.command("login")
def login(
    token: str = typer.Option(
        ...,
        "--token",
        "-t",
        help="GitLab personal access token",
        prompt="Enter your GitLab personal access token",
        hide_input=True,
    ),
    url: str = typer.Option(
        "https://gitlab.com",
        "--url",
        "-u",
        help="GitLab instance URL",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Default GitLab project (group/project)",
    ),
) -> None:
    """Configure GitLab authentication."""
    config = load_config()

    # Update configuration
    config.gitlab.token = token
    config.gitlab.url = url
    if project:
        config.gitlab.default_project = project

    # Test connection
    client = get_gitlab_client(config)
    try:
        user = client.client.user
        console.print(f"✓ Successfully authenticated as [green]{user.username}[/]")
    except Exception as e:
        console.print(f"[red]Authentication failed: {e}[/]")
        raise typer.Exit(1)

    # Save configuration
    save_config(config)
    console.print("\nConfiguration saved!")


@app.command("status")
def status() -> None:
    """Show current authentication status."""
    config = load_config()
    client = get_gitlab_client(config)

    try:
        user = client.client.user
        table = Table("Setting", "Value")
        table.add_row("GitLab URL", config.gitlab.url)
        table.add_row("Username", user.username)
        table.add_row("Email", user.email)
        table.add_row("Default Project", config.gitlab.default_project or "Not set")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Not authenticated: {e}[/]")
        raise typer.Exit(1)


@app.command("logout")
def logout(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear authentication configuration."""
    if not force:
        confirm = typer.confirm("Are you sure you want to clear authentication?")
        if not confirm:
            raise typer.Abort()

    config = load_config()
    config.gitlab.token = ""
    save_config(config)

    console.print("Authentication configuration cleared.")


@app.command("set-project")
def set_project(
    project: str = typer.Argument(
        ...,
        help="GitLab project path (group/project)",
    ),
) -> None:
    """Set the default GitLab project."""
    config = load_config()

    # Update project
    config.gitlab.default_project = project

    # Test project access if authenticated
    if config.gitlab.token:
        client = get_gitlab_client(config)
        try:
            project_info = client.project
            console.print(
                f"✓ Successfully set default project to [green]{project}[/]\n"
                f"Project URL: {project_info.web_url}"
            )
        except Exception as e:
            console.print(f"[yellow]Warning: Could not verify project access: {e}[/]")
            console.print(f"Set default project to: {project}")
    else:
        console.print(f"Set default project to: {project}")

    # Save configuration
    save_config(config)


@app.command("clear-project")
def clear_project(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear the default project setting."""
    if not force:
        confirm = typer.confirm("Are you sure you want to clear the default project?")
        if not confirm:
            raise typer.Abort()

    config = load_config()
    config.gitlab.default_project = None
    save_config(config)

    console.print("Default project cleared.")

from typing import Optional

import typer
from rich.console import Console
from rich.traceback import install

from gitlab_ml.commands import auth, models
from gitlab_ml.config import load_config
from gitlab_ml.utils.logger import setup_logging

# Install rich traceback handler
install(show_locals=True)

# Initialize typer app and console
app = typer.Typer(
    name="gitlab-ml",
    help="CLI tool for managing machine learning models in GitLab's Model Registry",
    add_completion=True,
)
console = Console()

# Add command groups
app.add_typer(models.app, name="models", help="Manage ML models in GitLab registry")
app.add_typer(auth.app, name="auth", help="Authentication and access control")


def version_callback(value: bool):
    """Print version information."""
    if value:
        from gitlab_ml import __version__
        console.print(f"gitlab-ml version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[str] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    GitLab ML CLI - Manage machine learning models in GitLab's Model Registry.
    """
    # Setup logging
    setup_logging(verbose)
    
    # Load configuration
    ctx.obj = load_config(config)


if __name__ == "__main__":
    app() 
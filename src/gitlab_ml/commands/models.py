from pathlib import Path
from typing import List, Optional

import typer
from gitlab_ml.api.client import get_gitlab_client
from gitlab_ml.api.models import ModelRegistry
from gitlab_ml.utils.logger import get_logger
from gitlab_ml.utils.version import validate_version
from rich.console import Console
from rich.table import Table

logger = get_logger(__name__)

app = typer.Typer(help="Manage ML models in GitLab registry")
console = Console()


@app.command("list")
def list_models(
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format (table/json/yaml)"
    ),
) -> None:
    """List all models in the registry."""
    client = get_gitlab_client()
    registry = ModelRegistry(client)
    
    models = registry.list_models()
    
    if format == "json":
        console.print_json(data=[model.dict() for model in models])
        return
    elif format == "yaml":
        import yaml
        console.print(yaml.dump([model.dict() for model in models]))
        return
    
    # Default table output
    table = Table(
        "Name",
        "Latest Version",
        "Total Versions",
        "Latest Update",
        title="GitLab ML Models"
    )
    
    for model in models:
        latest_version = model.latest_version or "N/A"
        version_count = len(model.versions)
        latest_update = model.versions[-1].created_at.strftime("%Y-%m-%d %H:%M") if model.versions else "N/A"
        
        table.add_row(
            model.name,
            latest_version,
            str(version_count),
            latest_update,
        )
    
    if not models:
        console.print("[yellow]No models found[/]")
    else:
        console.print(table)


@app.command("create")
def create_model(
    name: str = typer.Argument(..., help="Name of the model"),
    description: str = typer.Option("", "--description", "-d", help="Model description"),
    tags: List[str] = typer.Option([], "--tag", "-t", help="Tags for the model"),
) -> None:
    """Create a new model in the registry."""
    client = get_gitlab_client()
    registry = ModelRegistry(client)
    
    model = registry.create_model(name=name, description=description, tags=tags)
    console.print(f"✨ Created model: {model.name}")


@app.command("upload")
def upload_model(
    name: str = typer.Argument(..., help="Name of the model"),
    path: Path = typer.Argument(..., help="Path to model file or directory"),
    version: str = typer.Option(..., "--version", "-v", help="Version number (semver)"),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Version message"),
) -> None:
    """Upload a new version of a model."""
    # Validate path exists
    if not path.exists():
        console.print(f"[red]Error: File not found: {path}[/]")
        raise typer.Exit(1)
    
    # Show what we're uploading
    if path.is_dir():
        files = list(path.rglob('*'))
        file_count = sum(1 for f in files if f.is_file())
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        console.print(
            f"Uploading directory '{path}' "
            f"({file_count} files, {total_size / 1024 / 1024:.1f} MB)"
        )
    else:
        size = path.stat().st_size
        console.print(
            f"Uploading file '{path}' ({size / 1024 / 1024:.1f} MB)"
        )
    
    # Validate version format
    try:
        validate_version(version)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)
    
    client = get_gitlab_client()
    registry = ModelRegistry(client)
    
    try:
        model_version = registry.upload_version(
            model_name=name,
            version=version,
            path=path,
            message=message,
        )
        if path.is_dir():
            console.print(f"📤 Uploaded {len(model_version.artifacts)} files")
            console.print(f"✨ Created version {model_version.version} of {name}")
        else:
            console.print(f"✨ Created version {model_version.version} of {name}")
    except Exception as e:
        console.print(f"[red]Error uploading model: {e}[/]")
        raise typer.Exit(1)


@app.command("download")
def download_model(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name of the model"),
    version: str = typer.Option(..., "--version", "-v", help="Version to download"),
    output: Optional[Path] = typer.Option(
        "downloads", "--output", "-o", help="Output directory"
    ),
) -> None:
    """Download a specific version of a model."""
    client = get_gitlab_client()
    registry = ModelRegistry(client)
    
    try:
        # First check if model exists
        models = registry.list_models()
        model = next((m for m in models if m.name == name), None)
        if not model:
            available_models = [m.name for m in models]
            console.print(f"[red]Error: Model '{name}' not found[/]")
            if available_models:
                console.print("\nAvailable models:")
                for m in sorted(available_models):
                    console.print(f"  - {m}")
            raise typer.Exit(1)
        
        # Then check if version exists
        if not any(v.version == version for v in model.versions):
            available_versions = [v.version for v in model.versions]
            console.print(f"[red]Error: Version '{version}' not found for model '{name}'[/]")
            if available_versions:
                console.print("\nAvailable versions:")
                for v in sorted(available_versions):
                    console.print(f"  - {v}")
            raise typer.Exit(1)
        
        # Download the version
        path = registry.download_version(
            model_name=name,
            version=version,
            output_dir=output,
        )
        console.print(f"📥 Downloaded {name} {version} to {path}")
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error downloading model: {str(e)}[/]")
        raise typer.Exit(1)


@app.command("delete")
def delete_model(
    name: str = typer.Argument(..., help="Name of the model"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompt"
    ),
) -> None:
    """Delete a model from the registry."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete {name}?")
        if not confirm:
            raise typer.Abort()
    
    client = get_gitlab_client()
    registry = ModelRegistry(client)
    
    try:
        registry.delete_model(name)
        console.print(f"🗑️  Deleted model: {name}")
    except ValueError as e:
        console.print(f"[red]{str(e)}[/]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred while deleting model '{name}'[/]")
        logger.error(f"Unexpected error during model deletion: {e}")
        raise typer.Exit(2) 
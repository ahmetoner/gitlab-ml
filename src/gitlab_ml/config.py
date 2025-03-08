from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GitLabConfig(BaseSettings):
    """GitLab connection configuration."""
    url: str = Field(
        default="https://gitlab.com",
        description="GitLab instance URL",
    )
    token: Optional[str] = Field(
        default=None,
        description="GitLab personal access token",
        env="GITLAB_ML_TOKEN",
    )
    default_project: Optional[str] = Field(
        default=None,
        description="Default GitLab project (group/project)",
        env="GITLAB_ML_PROJECT",
    )
    api_version: str = Field(
        default="v4",
        description="GitLab API version",
    )

    @field_validator("token")
    def validate_token_if_needed(cls, v: Optional[str]) -> Optional[str]:
        """Validate token only when it's provided."""
        if v is not None and not v.strip():
            return None
        return v

    model_config = SettingsConfigDict(
        env_prefix="GITLAB_ML_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def ensure_token(self) -> str:
        """Ensure token is available or raise an error."""
        if not self.token:
            raise ValueError(
                "GitLab token is required. Please run 'gitlab-ml auth login' to configure authentication."
            )
        return self.token


class Config(BaseSettings):
    """Main application configuration."""
    gitlab: GitLabConfig = Field(default_factory=GitLabConfig)
    config_path: Optional[Path] = None

    model_config = SettingsConfigDict(
        env_prefix="GITLAB_ML_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    xdg_config_home = Path.home() / ".config"
    return xdg_config_home / "gitlab-ml" / "config.yml"


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file and environment variables."""
    config_file = Path(config_path) if config_path else get_default_config_path()
    
    # Initialize with default values
    config = Config()
    
    if config_file.exists():
        with config_file.open() as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config = Config.model_validate(yaml_config)
    
    config.config_path = config_file
    return config


def save_config(config: Config) -> None:
    """Save configuration to file."""
    if not config.config_path:
        config.config_path = get_default_config_path()
    
    config.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with config.config_path.open("w") as f:
        yaml.dump(
            config.model_dump(exclude={"config_path"}),
            f,
            default_flow_style=False,
        ) 
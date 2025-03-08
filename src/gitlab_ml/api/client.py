from typing import Optional

import gitlab
import typer
from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError
from gitlab_ml.config import Config, load_config
from gitlab_ml.utils.logger import get_logger

logger = get_logger(__name__)


class GitLabClient:
    """GitLab API client wrapper."""
    
    def __init__(self, config: Config) -> None:
        """Initialize GitLab client with configuration."""
        self.config = config
        self._client: Optional[Gitlab] = None
    
    @property
    def client(self) -> Gitlab:
        """Get or create GitLab client instance."""
        if self._client is None:
            try:
                # Ensure token is available
                token = self.config.gitlab.ensure_token()
                
                self._client = gitlab.Gitlab(
                    url=self.config.gitlab.url,
                    private_token=token,
                )
                self._client.auth()
            except GitlabAuthenticationError:
                logger.error("Failed to authenticate with GitLab")
                raise typer.Exit(1)
            except ValueError as e:
                logger.error(str(e))
                raise typer.Exit(1)
        return self._client
    
    @property
    def project(self):
        """Get the configured GitLab project."""
        if not self.config.gitlab.default_project:
            logger.error("No default project configured")
            raise typer.Exit(1)
        
        try:
            return self.client.projects.get(self.config.gitlab.default_project)
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            raise typer.Exit(1)


_client_instance: Optional[GitLabClient] = None


def get_gitlab_client(config: Optional[Config] = None) -> GitLabClient:
    """Get or create a GitLab client instance."""
    global _client_instance
    
    if _client_instance is None:
        if config is None:
            config = load_config()
        _client_instance = GitLabClient(config)
    
    return _client_instance 
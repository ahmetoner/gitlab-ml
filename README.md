# GitLab ML CLI

A command-line interface tool for managing machine learning models in GitLab's Model Registry. This tool provides a seamless experience for ML teams to version, track, and deploy their models using GitLab's infrastructure.

## Features

- **Model Registry Management**:
  - Create, delete, and list models
  - Manage model metadata and tags
  - Track model lineage and dependencies
- **Model Versioning**:
  - Upload new model versions with semantic versioning
  - Download specific versions for deployment
- **Access Control**:
  - GitLab authentication and authorization

## Installation

### Using pip

```bash
pip install gitlab-ml
```

### Using Poetry

```bash
poetry add gitlab-ml
```

### From Source

```bash
git clone https://gitlab.com/ahmetoner/gitlab-ml.git
cd gitlab-ml
poetry install
```

## Configuration

### Configuration File

Create a configuration file at `~/.config/gitlab-ml/config.yml`:

```yaml
gitlab:
  # GitLab instance URL
  url: "https://gitlab.com"
  
  # Personal access token with api scope
  token: "your-personal-access-token"
  
  # Default project for model registry
  default_project: "group/project"
```

### Environment Variables

Alternative to config file, you can use environment variables:

```bash
# Required settings
export GITLAB_ML_TOKEN="your-personal-access-token"
export GITLAB_ML_URL="https://gitlab.com"
export GITLAB_ML_PROJECT="group/project"
```

## Usage

### Model Management

```bash
# List all models with different output formats
gitlab-ml models list
gitlab-ml models list --format json
gitlab-ml models list --format yaml

# Create a new model
gitlab-ml models create my-model \
    --description "My ML model"

# Delete a model (with confirmation)
gitlab-ml models delete my-model

# Force delete without confirmation
gitlab-ml models delete my-model --force
```

### Version Management

```bash
# Upload a new model version
gitlab-ml models upload my-model 1.0.0 ./model.pkl

# Upload a directory of model artifacts
gitlab-ml models upload my-model 1.0.0 ./model_dir

# Download a specific version
gitlab-ml models download my-model 1.0.0 \
    --output ./models/
```

## Development

1. Clone the repository:

   ```bash
   git clone https://gitlab.com/ahmetoner/gitlab-ml.git
   cd gitlab-ml
   ```

2. Install development dependencies:

   ```bash
   poetry install --with dev
   ```

3. Activate virtual environment:

   ```bash
   poetry shell
   ```

4. Run tests:

   ```bash
   # Run all tests
   poetry run pytest
   
   # Run with coverage
   poetry run pytest --cov=gitlab_ml
   
   # Run specific test file
   poetry run pytest tests/test_models.py
   ```

5. Code formatting and linting:

   ```bash
   # Format code
   poetry run black .
   poetry run isort .
   
   # Run linters
   poetry run mypy .
   poetry run ruff .
   ```

## Troubleshooting

### Common Issues

1. Authentication Errors

   ```
   Error: GitLab authentication failed
   ```

   - Verify your token has the correct permissions (api scope)
   - Check if token is expired
   - Ensure GitLab URL is correct

2. Project Access

   ```
   Error: Project not found or no access
   ```

   - Verify project path is correct
   - Check if you have sufficient permissions
   - Ensure project exists and is accessible

3. Upload Failures

   ```
   Error: Failed to upload model version
   ```

   - Check file permissions
   - Verify disk space
   - Ensure version follows semver format

## API Documentation

### Python API

```python
from pathlib import Path
from gitlab_ml.api.client import get_gitlab_client, GitLabClient
from gitlab_ml.api.models import ModelRegistry

# Initialize client with custom URL and token
client = GitLabClient(
    url="https://gitlab.com",
    token="glpat-xxxxxxxxxxxx",
    default_project="group/project"
)
registry = ModelRegistry(client)

# Or use environment variables
import os
os.environ["GITLAB_ML_URL"] = "https://gitlab.com"
os.environ["GITLAB_ML_TOKEN"] = "glpat-xxxxxxxxxxxx"
os.environ["GITLAB_ML_PROJECT"] = "group/project"
client = get_gitlab_client()
registry = ModelRegistry(client)

# List models
models = registry.list_models()

# Upload model
registry.upload_version(
    model_name="my-model",
    version="1.0.0",
    path=Path("./model.pkl")
)

# Download model
registry.download_version(
    model_name="ml-model-new",
    version="1.2.2",
    output_dir=Path("./downloaded_model")
)
```

### REST API Integration

The CLI integrates with GitLab's REST and GraphQL APIs. For custom integrations, refer to:

- [GitLab REST API Documentation](https://docs.gitlab.com/ee/api/)
- [GitLab GraphQL API Documentation](https://docs.gitlab.com/ee/api/graphql/)

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a merge request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

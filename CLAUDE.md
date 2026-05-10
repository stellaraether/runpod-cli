# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RunPod CLI is a Python command-line tool for interacting with RunPod serverless endpoints, specifically:
- `google-nano-banana-2-edit` for image editing
- `google-veo3-1-fast-i2v` for image-to-video generation

## Common Commands

### Development

```bash
# Install in editable mode
pip install -e .

# Run the CLI locally
python3 -m runpod_cli --help
runpod --help

# Run a specific command
runpod image edit -p "make the person smile" -i https://example.com/photo.jpg
runpod video generate -p "a cat walking" -i https://example.com/cat.jpg
```

### Testing

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_smoke.py

# Run with coverage
pytest --cov=runpod_cli --cov-report=xml
```

### Linting and Formatting

```bash
# Format code
black runpod_cli/
isort --profile black runpod_cli/

# Lint
flake8 --max-line-length=120 runpod_cli/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Build and Release

```bash
# Build package
python -m build

# Check package
twine check dist/*
```

## Architecture

### Entry Points

- `runpod_cli/__main__.py` enables `python -m runpod_cli`
- `setup.py` registers the `runpod` console script pointing to `runpod_cli.cli:cli`

### Core Modules

- `runpod_cli/cli.py` - Defines the Click CLI groups (`image`, `video`, `job`) and commands. Also contains `handle_errors` decorator for consistent error formatting.
- `runpod_cli/client.py` - `RunPodClient` wraps the RunPod serverless API (`/runsync`, `/run`, `/status`, `/cancel`).
- `runpod_cli/config.py` - `Config` class manages the YAML config file at `~/.config/runpod-cli/config.yml` (stores API key and optional default endpoint IDs).

### Command Structure

```
runpod configure              # Store API key
runpod image edit             # Edit images (default endpoint: google-nano-banana-2-edit)
runpod video generate         # Generate video from image (default endpoint: google-veo3-1-fast-i2v)
runpod job submit/status/cancel  # Async job management for any endpoint
```

Job submit accepts inline JSON or `@file.json`:
```bash
runpod job submit my-endpoint-id '{"prompt": "hello"}'
runpod job submit my-endpoint-id @input.json
```

### Error Handling

All commands use the `@handle_errors` decorator in `cli.py`. It catches `requests.HTTPError` and prints the response body, then aborts with `click.Abort()`.

### Shared Context

Commands receive a Click `Context` whose `obj` dict lazily holds:
- `client` — a `RunPodClient` instance (requires configured API key)
- `config` — a `Config` instance
- `config_path` — optional override from `--config`

Use `_get_client(ctx)` and `_get_config(ctx)` in new commands rather than instantiating directly.

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `test.yml` - Runs on PRs and main: build check, pre-commit, tests across Python 3.8-3.12, coverage upload.
- `auto-release.yml` - Runs on main push: tags a release from `runpod_cli/__init__.py` `__version__`, creates GitHub release, publishes to PyPI via `PYPI_API_TOKEN` secret.
- `check-version-bump.yml` - Ensures version bump PRs only touch allowed files (`__init__.py`, `cli.py`, `setup.py`, `pyproject.toml`, `CLAUDE.md`, `.gitignore`, `tests/`, workflow files).

## Configuration

The CLI stores its config at `~/.config/runpod-cli/config.yml`. The `configure` command writes the API key there with `0o600` permissions. The config path can be overridden with `--config` on any command.

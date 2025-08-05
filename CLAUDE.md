# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Parolo is a version-controlled prompt system for LLM workflows. It automatically versions prompts when content changes and supports Jinja2 templating. The system stores prompts in a configurable directory structure with versioned files.

## Architecture

The core system consists of:
- `parolo/core.py`: Contains the main `Prompt` class with static methods for prompt management
- `parolo/__init__.py`: Exports the `Prompt` class
- `main.py`: Example usage demonstrating the API

### Key Components

- **Prompt Storage**: Prompts are stored in `~/.parolo/prompts/` by default (configurable via `PAROLO_HOME` environment variable)
- **Versioning**: Uses SHA-256 hashing to detect changes and create new versions automatically
- **File Structure**: Each prompt gets a directory with `versions/` subdirectory containing:
  - `v0001.txt`, `v0002.txt`, etc. (prompt content)
  - `v0001.json`, `v0002.json`, etc. (metadata: hash, timestamp, size, custom metadata)
  - `latest.txt` (current version content)
- **Metadata**: Git-like metadata system storing hash, timestamp, size, line count, previous hash, and custom metadata

## Common Commands

### Development Setup
```bash
# Create virtual environment (if not exists)
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install pytest build
```

### Testing
```bash
# Run all tests
pytest tests

# Run specific test file
pytest tests/test_prompt.py

# Run tests with verbose output
pytest -v tests
```

### Building
```bash
# Build the package (includes testing)
./build_package.sh

# Manual build process
python -m build
```

### Package Management
The project uses `uv` for dependency management and virtual environments. Dependencies are specified in `pyproject.toml`.

## Development Notes

- The `Prompt` class uses class methods and maintains a class-level `base_dir` attribute
- Hash comparison prevents duplicate versions when prompt content is unchanged
- Tests use `tmp_path` fixtures for isolated file system testing
- The build script automatically runs tests before building and cleans previous builds

## API Methods

### Core Methods
- `Prompt.create(name, prompt, metadata=None)` - Create/update a prompt with optional metadata
- `Prompt.get_prompt(name, version="latest")` - Retrieve prompt content for a specific version
- `Prompt.format_prompt(prompt_name, version="latest", **kwargs)` - Get and format prompt with variables
- `Prompt.list_versions(name, show_metadata=False)` - List all versions with optional metadata display
- `Prompt.overview()` - Get overview of all prompt collections

### Metadata Methods
- `Prompt.get_metadata(name, version)` - Get metadata for a specific version
- `Prompt.show_version_info(name, version)` - Display detailed version information
- `Prompt.log(name, limit=10)` - Show version history like git log

### Configuration
- `Prompt.set_base_dir(path)` - Set custom storage location
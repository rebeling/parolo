# Parolo

A version-controlled prompt system for LLM workflows. It enables you to:
- **Automatically version prompts:** Each change creates a new version (e.g., `v0001.txt`, `v0002.txt`, etc.)
- **Maintain organized prompt storage:** Prompts are stored in a configurable location.

---

## Installation

```bash
uv pip install parolo
```

## Quick Start

```py
from parolo import Prompt

# Create a simple prompt
Prompt.create(name="summarize", prompt="Summarize this in three bullet points.")

# Create another version with different content
Prompt.create(name="summarize", prompt="Provide a concise summary in bullet points.")

# List all versions for a prompt
versions = Prompt.list_versions("summarize")
print(versions)  # ['v0001.txt', 'v0002.txt']

Prompt.create(name="greet", prompt="Hello, world!", metadata={"author": "demo", "type": "greeting"})

# Get overview of all prompts
overview = Prompt.overview()
print(overview)  # {'summarize': 2, 'greet': 1}
```

### Configuration

By default, prompts are stored in `~/.parolo/prompts/`. You can customize this in several ways:

```python
# Method 1: Using set_base_dir()
Prompt.set_base_dir("./project-prompts")

# Method 2: Environment variable
# export PAROLO_HOME="./project-prompts"
```


### Advanced Usage

Use Python string formatting for prompts with support for metadata and easy runtime content injection.

```py
from parolo import Prompt

# Example of a complex multiline prompt
EXAMPLE_PROMPT = """Review the following Python code for data handling, performance, and clarity.

Focus on:
- Data validation and safety
- Efficiency for large datasets
- Code readability

Keep response under {max_tokens} tokens.

Code:
{code}
"""

# Create prompts for different use cases
Prompt.create(
    name="code_review_template",
    prompt=EXAMPLE_PROMPT,
    metadata={"author": "team", "type": "code_review", "complexity": "high"}
)

# Retrieve and use the stored prompt using Prompt methods
latest_prompt = Prompt.get_prompt("code_review_template")

# Use the prompt with actual code
sample_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
"""

# Format the prompt with the code using the built-in method
formatted_prompt = Prompt.format_prompt("code_review_template", code=sample_code, max_tokens=300)
print(formatted_prompt)

# Or get a specific version
version_prompt = Prompt.get_prompt("code_review_template", version="v0001")

# Get and format a specific version
formatted_v1 = Prompt.format_prompt("code_review_template", version="v0001", code=sample_code, max_tokens=300)

# Example usage in an application
def review_code(code: str, version: str = "latest") -> str:
    """Review code using the stored prompt template"""
    prompt = Prompt.format_prompt("code_review_template", version=version, code=code, max_tokens=300)
    # Send to your LLM API here
    return prompt

# Use in your application
result = review_code(sample_code)

# Or use a specific version for reproducibility
result_v1 = review_code(sample_code, version="v0001")
```

### Metadata and Version History

Parolo stores rich metadata with each version, similar to git commits:

```python
from parolo import Prompt

# Create prompt with custom metadata
Prompt.create(
    name="code_review",
    prompt="Review the following code for security issues:\n\n{code}",
    metadata={"author": "security_team", "category": "security", "priority": "high"}
)

# List versions with metadata
Prompt.list_versions("code_review", show_metadata=True)

# Show version history (like git log)
Prompt.log("code_review")

# Get detailed version information
Prompt.show_version_info("code_review", "v0001")

# Retrieve metadata programmatically
metadata = Prompt.get_metadata("code_review", "v0001")
print(metadata["hash"])  # SHA-256 hash
print(metadata["timestamp"])  # ISO format timestamp
print(metadata["metadata"])  # Custom metadata
```

### File Structure with Metadata

```
~/.parolo/prompts/
├── code_review/
│   ├── latest.txt
│   └── versions/
│       ├── v0001.txt           # Prompt content
│       ├── v0001.json          # Metadata (hash, timestamp, etc.)
│       ├── v0002.txt
│       └── v0002.json
```

Each `.json` file contains:
- `hash`: SHA-256 hash of the prompt content
- `timestamp`: ISO format creation timestamp
- `version`: Version identifier (e.g., "v0001")
- `size`: Size in bytes
- `line_count`: Number of lines
- `previous_hash`: Hash of the previous version
- `metadata`: Custom metadata provided by user

## Features

- **Automatic Versioning:** Only creates new versions when content actually changes (using SHA-256 hashing)
- **Rich Metadata:** Stores timestamp, hash, size, and custom metadata with each version
- **Version History:** Git-like log functionality to view version history
- **Latest File:** Always maintains a `latest.txt` file with the current version
- **Organized Storage:** Clean directory structure for easy browsing
- **Simple API:** Intuitive class-based interface with static methods
- **Flexible Configuration:** Customizable storage location

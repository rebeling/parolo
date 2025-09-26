# Parolo

A tiny, file-based prompt store with automatic versioning.
Simple defaults, zero infra, backward compatible with the original Prompt class.

* Stores the current prompt in latest.txt
* Creates immutable versions under versions/vNNNN.txt (+ vNNNN.json metadata)
* Atomic writes so readers never see partial files
* Optional function API with Jinja2 rendering
* Works out of the box on a single machine or shared volume

```python
from parolo import prompts, Prompt  # new + old

# New, namespaced API
prompts.save("greeting", "Hello {{name}}!")
print(prompts.render("greeting", name="Matthias"))

# Old class API (back-compat, str.format)
Prompt.create("legacy", "Hi {name}")
print(Prompt.format_prompt("legacy", name="Matthias"))
```

---

## Installation

```bash
uv pip install parolo
```
By default, parolo stores data in ~/.parolo/prompts/.
Override with PAROLO_HOME=/path/to/dir.

Or in code: from parolo import set_base_dir; set_base_dir("/path/to/dir")

---

## Listing & history

```python
from parolo import prompts

# All prompts (quick stats)
print(prompts.list())
# → [{'name': 'email_refund', 'versions': 3, 'has_latest': True, 'latest_version': 'v0003', ...}, ...]

# All versions for one prompt (filenames)
print(prompts.versions("email_refund"))
# → ['v0001.txt', 'v0002.txt', 'v0003.txt']

# With metadata (timestamp, hash, size, detected Jinja variables)
print(prompts.versions("email_refund", with_meta=True))
# → [{'file':'v0003.txt','version':'v0003','timestamp':'...','hash':'...','size':123,'line_count':3,'jinja_variables':['customer','order_id']}, ...]

# Metadata for one version
print(prompts.meta("email_refund", "v0001"))
```

---

## Hot reload (agents)

Poll the file’s mtime token; reload when it changes.

```python
import time
from parolo import token, get

name = "email_refund"
t = token(name)
tmpl = get(name)

while True:
    time.sleep(1.0)
    nt = token(name)
    if nt != t:
        t = nt
        tmpl = get(name)  # reload latest.txt
        # update your in-memory template
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

#!/bin/bash
set -e

echo "🧪 [parolo] Ensuring virtual environment exists..."

# Only create the virtual environment if it doesn't already exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment at: .venv"
    uv venv
fi

echo "✅ Activating .venv"
source .venv/bin/activate

echo "⬇️ Installing required dev tools: pytest, build"
uv pip install pytest build > /dev/null

uv run ruff check . --fix

echo "🔍 Running tests..."
pytest tests || { echo '❌ Tests failed'; exit 1; }

echo "🧼 Cleaning previous builds..."
rm -rf dist/ build/ parolo.egg-info/

echo "🚧 Building the package..."
python -m build

echo "✅ Build complete! Distribution artifacts in ./dist/"

twine upload dist/*

echo "✅ Uploaded to pypi."

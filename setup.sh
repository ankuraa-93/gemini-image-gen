#!/bin/bash
set -e

TOOLKIT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Gemini Image Gen — Setup ==="
echo ""

# Check Python version
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        minor=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.9+ is required but not found."
    echo "Install it from https://www.python.org/downloads/"
    exit 1
fi

echo "Using Python: $PYTHON_CMD ($($PYTHON_CMD --version))"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
$PYTHON_CMD -m pip install --quiet google-genai Pillow python-dotenv

# Verify imports actually work (catches mismatched pip/python installs)
if ! $PYTHON_CMD -c "from google import genai; from PIL import Image; from dotenv import load_dotenv" 2>/dev/null; then
    echo ""
    echo "Warning: Packages installed but imports failed."
    echo "This usually means pip installed to a different Python than '$PYTHON_CMD'."
    echo "Debug with:"
    echo "  $PYTHON_CMD -c \"import sys; print(sys.executable)\""
    echo "  $PYTHON_CMD -m pip show google-genai"
    echo ""
fi

# Create .env if it doesn't exist
if [ ! -f "$TOOLKIT_DIR/.env" ]; then
    cp "$TOOLKIT_DIR/.env.example" "$TOOLKIT_DIR/.env"
    echo ""
    echo "Created .env file. Add your Gemini API key:"
    echo "  $TOOLKIT_DIR/.env"
    echo ""
    echo "Get a key at: https://aistudio.google.com/apikey"
else
    echo ".env already exists — skipping."
fi

# Create output directories
mkdir -p "$TOOLKIT_DIR/styles" "$TOOLKIT_DIR/outputs"

# Set up Claude Code skill
echo ""
echo "=== Claude Code Skill Setup ==="
echo ""

GLOBAL_COMMANDS="$HOME/.claude/commands"
if [ -d "$HOME/.claude" ]; then
    mkdir -p "$GLOBAL_COMMANDS"
    cp "$TOOLKIT_DIR/image-gen.md" "$GLOBAL_COMMANDS/image-gen.md"
    echo "Installed skill to: $GLOBAL_COMMANDS/image-gen.md"
    echo "You can now use /image-gen in any Claude Code session."
else
    echo "Claude Code config directory not found (~/.claude)."
    echo "To install the skill manually, copy image-gen.md to .claude/commands/:"
    echo "  mkdir -p ~/.claude/commands"
    echo "  cp $TOOLKIT_DIR/image-gen.md ~/.claude/commands/"
fi

# Set env var hint
echo ""
echo "=== Optional: Set Toolkit Path ==="
echo ""
echo "Add this to your shell profile (~/.zshrc or ~/.bashrc):"
echo "  export GEMINI_IMAGE_GEN_HOME=\"$TOOLKIT_DIR\""
echo ""
echo "=== Setup Complete ==="

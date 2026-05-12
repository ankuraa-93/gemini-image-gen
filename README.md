# Gemini Image Gen for Claude Code

AI-assisted image generation using Google's Gemini, orchestrated by Claude Code. Turn simple descriptions into polished images through intelligent prompt crafting, style management, and iterative refinement.

## What This Does

This isn't just a Gemini API wrapper. The Claude Code skill layer adds:

- **Prompt enhancement** — Describe what you want in plain English; Claude crafts detailed, optimized prompts for Gemini
- **Session management** — Multi-turn conversations with Gemini for iterative refinement (adjust colors, move elements, change style)
- **Style extraction** — Feed in a reference image and extract its complete visual style for reuse
- **Style library** — 50+ pre-built style prompts (3D rendered, watercolor, pixel art, vintage, etc.)
- **Output validation** — Claude reviews generated images and suggests improvements
- **Auto model detection** — Gemini deprecates models frequently; the toolkit auto-detects the latest available model so you never hit "model not found"

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/ankuraa-93/gemini-image-gen.git ~/gemini-image-gen
cd ~/gemini-image-gen
./setup.sh
```

The setup script installs Python dependencies, creates your `.env` file, and copies the skill to `~/.claude/commands/`.

### 2. Add your API key

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey), then add it to your `.env`:

```
GEMINI_API_KEY=your_key_here
```

### 3. Install the Claude Code skill

The setup script does this automatically. To do it manually:

```bash
# Global (available in all projects)
cp ~/gemini-image-gen/image-gen.md ~/.claude/commands/

# Or project-specific
cp ~/gemini-image-gen/image-gen.md .claude/commands/
```

### 4. Use it

In Claude Code, type `/image-gen` followed by what you want:

```
/image-gen a cozy coffee shop interior in watercolor style
```

Or just invoke `/image-gen` and describe what you need interactively.

> **Note:** The skill needs to be invoked with `/image-gen` at the start of each Claude Code session where you want to generate images. It does not persist across sessions — if you start a new session or clear the current one, type `/image-gen` again. This is by design: most sessions don't need image generation, and loading the skill only when needed saves tokens.

## Examples

**Simple generation:**
```
/image-gen a logo for a podcast about space exploration, minimal flat design
```

**With a reference style:**
```
/image-gen generate an image matching the style of reference.png but with a mountain landscape
```

**Carousel/series:**
```
/image-gen create a 5-slide carousel about healthy eating tips, consistent 3D illustration style, 4:5 portrait
```

**Style exploration:**
```
/image-gen show me available styles in the library
```

## Configuration

All configuration is via environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | (required) | Your Gemini API key |
| `IMAGE_GEN_MODEL` | (auto-detected) | Pin a specific model; leave empty for auto-detection |
| `IMAGE_GEN_ASPECT_RATIO` | `1:1` | Default aspect ratio |
| `IMAGE_GEN_OUTPUT_DIR` | `outputs` | Where generated images are saved |
| `STYLE_EXTRACT_MODEL` | `gemini-2.5-pro` | Model used for style analysis |

## Project Structure

```
gemini-image-gen/
├── image-gen.md          # Claude Code skill (copy to .claude/commands/)
├── image_gen.py          # Core generation + session management
├── style_extract.py      # Style extraction from reference images
├── get_style.py          # Style library helper
├── style-library.html    # 50+ searchable style prompts
├── docs/
│   ├── setup.md          # Python environment & dependency troubleshooting
│   ├── models.md         # Model auto-detection, selection & error handling
│   └── styles.md         # Style workflows, library usage & output organization
├── styles/               # Your extracted/saved styles
├── outputs/              # Generated images
├── setup.sh              # One-command setup
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template
```

## How It Works

1. You describe what you want in plain language
2. Claude Code enhances your prompt with specific details (lighting, composition, style, color palette)
3. The enhanced prompt is sent to Gemini's image generation API
4. Claude Code reviews the output and shows it to you
5. You can iterate ("make it warmer", "add more detail", "change the background") — Gemini remembers context within a session
6. When you're happy, the final image is in `outputs/`

## Requirements

- Python 3.9+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- A [Gemini API key](https://aistudio.google.com/apikey) (pay-per-use — see [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing))

## Acknowledgments

Inspired by Carl Vellotti's [Claude Code for Product Managers](https://ccforpms.com) course, with optimizations for session management, auto model detection, and style workflows.

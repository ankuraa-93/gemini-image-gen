# Style Workflows

## Using Reference Images
When the user provides a reference image for style:
1. First, extract the style: `extract_style(image_path)`
2. Read the extracted style description
3. Incorporate it into your generation prompt as a style prefix
4. Generate using `reference_images=[image_path]` for additional visual grounding

## Using the Style Library
When the user wants to browse styles:
1. List available styles: `list_styles()`
2. Show the user options by category
3. Once they pick one, get the full prompt: `get_style(style_id)`
4. Blend the library style prompt with the user's subject description

## Saving Custom Styles
When the user creates a look they like:
1. Extract the style from the generated image: `extract_and_save(output_path)`
2. This saves a reusable style guide to `styles/`
3. Reference it in future sessions

## Output Organization

- Generated images go to `outputs/` by default (configurable via `IMAGE_GEN_OUTPUT_DIR` env var)
- Each output is named `output_NNN_HHMMSS.png` (turn number + timestamp)
- Extracted styles go to `styles/`
- Session state is in `.image_session.json` (ephemeral, safe to delete)

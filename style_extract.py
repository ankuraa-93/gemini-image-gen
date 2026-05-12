"""
Style Extraction Module
Uses Gemini's vision capabilities to analyze and extract
detailed style information from images.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

_TOOLKIT_DIR = Path(__file__).parent
load_dotenv(_TOOLKIT_DIR / ".env")

from google import genai

VISION_MODEL = os.environ.get("STYLE_EXTRACT_MODEL", "gemini-2.5-pro")

STYLE_EXTRACTION_PROMPT = """Analyze this image and deconstruct its complete visual style. I want to be able to recreate this exact aesthetic for completely different subjects.

Describe in detail:

**Color Palette:** What are the dominant colors? Secondary colors? Describe the color temperature (warm, cool, neutral), saturation levels, and any notable color relationships or contrasts. Are there specific hex codes or color names that define this look?

**Lighting:** What type of lighting is used? Describe the direction, quality (soft, hard, diffused), color temperature of the light, shadows, highlights, and any atmospheric lighting effects like rim light, backlighting, or volumetric rays.

**Composition & Framing:** How is the image composed? Describe the perspective, camera angle, focal length feel (wide, telephoto, macro), depth of field, rule of thirds usage, leading lines, symmetry, or any other compositional techniques.

**Textures & Materials:** What surface qualities are present? Describe any grain, noise, smoothness, glossiness, or material properties that define the look.

**Mood & Atmosphere:** What emotional tone does this convey? Describe the overall vibe, energy level, and feeling the viewer gets.

**Artistic Style:** Is this photorealistic, illustrated, painterly, graphic, retro, futuristic, minimal, maximalist? What art movement or design era does it reference, if any?

**Typography & Graphics:** If text or graphic elements are present, describe the font style, weight, treatment, and how it integrates with the image.

**Special Effects:** Any glows, blurs, distortions, overlays, duotone treatments, or post-processing effects?

Write this as a cohesive style guide I can reference when generating new images. Be specific enough that someone could recreate this aesthetic without seeing the original."""


def _get_client():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Either:\n"
            "  1. Create a .env file in the toolkit directory with GEMINI_API_KEY=your_key\n"
            "  2. Export it: export GEMINI_API_KEY=your_key\n"
            "Get a key at: https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def extract_style(image_path: str, custom_prompt: str = None) -> str:
    """
    Extract detailed style information from an image.

    Args:
        image_path: Path to the image to analyze
        custom_prompt: Optional custom extraction prompt

    Returns:
        Detailed style description as text
    """
    client = _get_client()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = Image.open(image_path)
    prompt = custom_prompt or STYLE_EXTRACTION_PROMPT

    print(f"Analyzing style of: {image_path}")
    print("This may take a moment...")

    response = client.models.generate_content(
        model=VISION_MODEL,
        contents=[prompt, image]
    )

    style_description = response.text

    print("\n" + "=" * 60)
    print("STYLE EXTRACTION COMPLETE")
    print("=" * 60 + "\n")
    print(style_description)

    return style_description


def extract_and_save(image_path: str, output_path: str = None) -> str:
    """
    Extract style and save to a markdown file.

    Args:
        image_path: Path to the image to analyze
        output_path: Where to save (auto-generated if not provided)

    Returns:
        Path to the saved style guide
    """
    style_description = extract_style(image_path)

    if not output_path:
        image_name = Path(image_path).stem
        output_path = f"styles/{image_name}_style.md"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(f"# Style Guide: {Path(image_path).name}\n\n")
        f.write(f"*Extracted from: `{image_path}`*\n\n")
        f.write("---\n\n")
        f.write(style_description)

    print(f"\nStyle guide saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    print("Style Extraction Module")
    print("Use: extract_style(image_path), extract_and_save(image_path)")

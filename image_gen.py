"""
Gemini Image Generation Module
Handles session management, multi-turn conversations, and output saving.
Designed to be orchestrated by Claude Code via the image-gen skill.
"""
import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path

if sys.version_info < (3, 9):
    raise RuntimeError(
        f"image_gen.py requires Python 3.9+, but you're running {sys.version}. "
        f"Try: /usr/bin/python3 or install a newer Python."
    )

from dotenv import load_dotenv

# Load .env from the script's own directory (toolkit root)
_TOOLKIT_DIR = Path(__file__).parent
load_dotenv(_TOOLKIT_DIR / ".env")

from google import genai
from google.genai import types

# Configuration — override via environment variables or function args
SESSION_FILE = ".image_session.json"
OUTPUT_DIR = os.environ.get("IMAGE_GEN_OUTPUT_DIR", "outputs")
DEFAULT_MODEL = os.environ.get("IMAGE_GEN_MODEL", "")
DEFAULT_ASPECT_RATIO = os.environ.get("IMAGE_GEN_ASPECT_RATIO", "1:1")

# Cached model discovery result
_CACHED_IMAGE_MODEL = None


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


def list_models(image_only: bool = True) -> list:
    """
    List available Gemini models. If image_only=True, filters to models
    that support image generation (have 'generateContent' action and
    'image' in their name or output modalities).

    Returns:
        List of dicts with 'name', 'display_name', and 'description'.
    """
    client = _get_client()
    results = []
    for model in client.models.list():
        model_id = model.name if hasattr(model, 'name') else str(model)
        if image_only:
            model_str = str(model).lower()
            if 'image' not in model_str:
                continue
        results.append({
            "name": model_id,
            "display_name": getattr(model, 'display_name', model_id),
            "description": getattr(model, 'description', ''),
        })
    return results


def get_default_model() -> str:
    """
    Get the best available image generation model. Priority:
    1. IMAGE_GEN_MODEL env var (if set and non-empty)
    2. Auto-detect from API: prefer flash/lite image models for speed
    """
    global _CACHED_IMAGE_MODEL

    if DEFAULT_MODEL:
        return DEFAULT_MODEL

    if _CACHED_IMAGE_MODEL:
        return _CACHED_IMAGE_MODEL

    print("Auto-detecting best image generation model...")
    try:
        models = list_models(image_only=True)
        if not models:
            raise RuntimeError("No image generation models found via API.")

        names = [m["name"] for m in models]
        print(f"Available image models: {names}")

        # Prefer flash/lite models for speed, then pro
        for keyword in ["flash", "lite", "pro"]:
            for name in names:
                if keyword in name.lower():
                    _CACHED_IMAGE_MODEL = name
                    print(f"Selected: {name}")
                    return name

        # Fallback to first available
        _CACHED_IMAGE_MODEL = names[0]
        print(f"Selected (fallback): {names[0]}")
        return names[0]

    except Exception as e:
        raise RuntimeError(
            f"Could not auto-detect image model: {e}\n"
            "Set IMAGE_GEN_MODEL in your .env to specify one manually.\n"
            "Check available models at: https://ai.google.dev/gemini-api/docs/models"
        )


def _ensure_output_dir():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def _load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"history": [], "outputs": [], "turn": 0}
    return {"history": [], "outputs": [], "turn": 0}


def _reconstruct_history(raw_history):
    """Convert raw history dicts back to types.Content objects, preserving thought signatures for multi-turn."""
    reconstructed = []
    for item in raw_history:
        parts = []
        for part_data in item.get("parts", []):
            if "text" in part_data:
                part_kwargs = {"text": part_data["text"]}
                if "thought_signature" in part_data:
                    part_kwargs["thought_signature"] = base64.b64decode(part_data["thought_signature"])
                parts.append(types.Part(**part_kwargs))
            elif "inline_data" in part_data:
                blob = types.Blob(
                    mime_type=part_data["inline_data"]["mime_type"],
                    data=base64.b64decode(part_data["inline_data"]["data"])
                )
                part_kwargs = {"inline_data": blob}
                if "thought_signature" in part_data:
                    part_kwargs["thought_signature"] = base64.b64decode(part_data["thought_signature"])
                parts.append(types.Part(**part_kwargs))

        reconstructed.append(types.Content(
            role=item.get("role"),
            parts=parts
        ))
    return reconstructed


def _save_session(session):
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f)


def _get_next_output_path(session):
    _ensure_output_dir()
    turn = session.get("turn", 0) + 1
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{OUTPUT_DIR}/output_{turn:03d}_{timestamp}.png"


def new_session():
    """Clear the current session and start fresh."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    print("Session cleared. Ready for new image generation.")
    return {"history": [], "outputs": [], "turn": 0}


def session_info():
    """Display current session status."""
    session = _load_session()
    turn_count = session.get("turn", 0)
    outputs = session.get("outputs", [])

    if turn_count == 0:
        print("No active session. Start generating to create one.")
        return None

    print(f"Current session: {turn_count} turn(s)")
    print(f"Outputs generated:")
    for i, output in enumerate(outputs, 1):
        print(f"  {i}. {output}")

    return session


def revert(turns: int = 1):
    """Undo the last N turns from the current session."""
    session = _load_session()
    turn_count = session.get("turn", 0)

    if turn_count == 0:
        print("No active session to revert.")
        return None

    if turns > turn_count:
        print(f"Can only revert {turn_count} turn(s). Reverting all.")
        turns = turn_count

    items_to_remove = turns * 2
    session["history"] = session["history"][:-items_to_remove]
    session["outputs"] = session["outputs"][:-turns]
    session["turn"] = turn_count - turns

    _save_session(session)

    if session["turn"] == 0:
        print(f"Reverted {turns} turn(s). Session is now empty.")
    else:
        print(f"Reverted {turns} turn(s). Now at turn {session['turn']}.")
        print(f"Last output: {session['outputs'][-1] if session['outputs'] else 'None'}")

    return session


def generate(
    prompt: str,
    reference_images: list = None,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    model: str = None
) -> str:
    """
    Generate or refine an image. Automatically continues existing session.

    Args:
        prompt: Text description of what to generate/change
        reference_images: Optional list of image paths to use as references
        aspect_ratio: "1:1", "3:4", "4:5", "16:9", etc.
        model: Gemini model ID for image generation

    Returns:
        Path to the generated image
    """
    if model is None:
        model = get_default_model()

    client = _get_client()
    session = _load_session()

    content_parts = [prompt]

    if reference_images:
        from PIL import Image
        for img_path in reference_images:
            if os.path.exists(img_path):
                content_parts.append(Image.open(img_path))
            else:
                print(f"Warning: Reference image not found: {img_path}")

    config = types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspectRatio=aspect_ratio
        )
    )

    if session["history"]:
        print(f"Continuing session (turn {session['turn'] + 1})...")
        reconstructed_history = _reconstruct_history(session["history"])
        chat = client.chats.create(
            model=model,
            config=config,
            history=reconstructed_history
        )
        response = chat.send_message(content_parts)
        session["history"].append({"role": "user", "parts": [{"text": prompt}]})
    else:
        print("Starting new session...")
        chat = client.chats.create(
            model=model,
            config=config
        )
        response = chat.send_message(content_parts)
        session["history"].append({"role": "user", "parts": [{"text": prompt}]})

    output_path = None
    response_parts = []

    for part in response.parts:
        if part.text is not None:
            print(f"Model: {part.text}")
            part_data = {"text": part.text}
            if hasattr(part, 'thought_signature') and part.thought_signature:
                part_data["thought_signature"] = base64.b64encode(part.thought_signature).decode('utf-8')
            response_parts.append(part_data)
        elif part.inline_data is not None:
            output_path = _get_next_output_path(session)
            image = part.as_image()
            image.save(output_path)
            print(f"Saved: {output_path}")

            part_data = {
                "inline_data": {
                    "mime_type": part.inline_data.mime_type,
                    "data": base64.b64encode(part.inline_data.data).decode('utf-8')
                }
            }
            if hasattr(part, 'thought_signature') and part.thought_signature:
                part_data["thought_signature"] = base64.b64encode(part.thought_signature).decode('utf-8')
            response_parts.append(part_data)

    session["history"].append({"role": "model", "parts": response_parts})
    session["turn"] = session.get("turn", 0) + 1
    if output_path:
        session["outputs"].append(output_path)

    _save_session(session)

    return output_path


# Convenience alias
gen = generate


if __name__ == "__main__":
    print("Gemini Image Generation Module")
    print("Use: generate(prompt), new_session(), session_info(), revert()")

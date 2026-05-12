# Model Selection & Error Handling

## Auto-Detection

**Google frequently deprecates and renames Gemini models.** The toolkit auto-detects the best available image generation model at runtime so you never hit a "model not found" error.

### How it works
- `generate()` calls `get_default_model()` automatically if no model is passed
- `get_default_model()` queries the Gemini API via `list_models()` to find available image generation models
- It prefers flash/lite models (fast, good for iteration), then falls back to pro models
- The result is cached for the session so the API is only queried once

### Before first generation in a session
Run `list_models()` to see what's currently available. This helps you pick the right model and avoids surprises:
```python
from image_gen import list_models
models = list_models(image_only=True)
for m in models:
    print(f"  {m['name']}")
```

### Override behavior
- Pass `model="specific-model-id"` to `generate()` to use a specific model
- Set `IMAGE_GEN_MODEL` in `.env` to pin a default (bypasses auto-detection)
- If a model 404s despite being listed, it may have just been deprecated — re-run `list_models()` and pick another

### General guidance
- **Flash/lite models:** Fast, good for iteration and drafts. Use these during the creative loop.
- **Pro models:** Higher quality, slower. Use for final renders once you're happy with the composition.

## Error Handling

- **Model not found / deprecated:** Handled automatically by `get_default_model()`. If it still fails, run `list_models()` to see what's available and pass a valid model explicitly.
- **Rate limits:** Wait 30 seconds and retry. Gemini has per-minute quotas.
- **Safety filters:** If Gemini refuses a prompt, rephrase to be more neutral. Don't try to bypass safety — adjust the creative direction.
- **No image in response:** Sometimes Gemini returns only text. Check the response, adjust the prompt to be more visual/concrete, and retry.
- **Session corruption:** If multi-turn breaks, start a `new_session()` and regenerate.

# Setup & Environment

Python environment issues are the #1 cause of problems — multiple Python installs (Anaconda, Homebrew, system) can mean `pip install` puts packages somewhere different from where `python3` looks.

## Step 1: Find the right Python
```bash
which python3 && python3 --version
```
Must be 3.9+. If it's older (e.g., Anaconda's 3.8), the user needs to use a different Python or upgrade.

## Step 2: Verify pip matches python3
```bash
python3 -m pip --version
```
This ensures you're installing to the SAME Python that will run the scripts. Never use bare `pip install` — always use `python3 -m pip install` to guarantee the right target.

## Step 3: Install dependencies
```bash
python3 -m pip install google-genai Pillow python-dotenv
```

## Step 4: Verify imports work
```bash
python3 -c "from google import genai; from PIL import Image; from dotenv import load_dotenv; print('OK')"
```
If this fails with `ModuleNotFoundError` after installing, `pip` and `python3` are pointing to different installs. Debug with:
```bash
python3 -c "import sys; print(sys.executable)"
python3 -m pip show google-genai
```
Both should reference the same Python prefix.

## Step 5: Check API key
Verify `$TOOLKIT/.env` exists and contains `GEMINI_API_KEY`.

Get a key at: https://aistudio.google.com/apikey

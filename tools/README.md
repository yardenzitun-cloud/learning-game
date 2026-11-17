# Voice tooling (not used by the app at runtime)

New session setup: `mkdir -p /home/claude/tts && cp tools/*.py tools/*.json /home/claude/tts/`, put the Gemini key in /home/claude/tts/.key, then run `python3 tools/extract_audio.py` BEFORE build6.py (it restores the recorded mp3s from the bundles).

- `collect4.py` – opens index.html in headless Chrome, generates every spoken phrase per track and gender → texts4.json
- `batchall.py <list.json>` – records phrases with Gemini TTS batch API (env VOICE=Leda). Needs the Gemini API key in /home/claude/tts/.key (never commit it).
- `build6.py` – rebuilds voice_<track>_<n>.js bundles + CLIPS map in index.html from recorded mp3s, bumps cache versions.
- `rec_leda_all.json` – full list of recorded phrases.
Paths inside the scripts assume /home/claude/tts and /home/claude/kids-app/audio.

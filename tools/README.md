# Voice tooling (not used by the app at runtime)

- `collect4.py` – opens index.html in headless Chrome, generates every spoken phrase per track and gender → texts4.json
- `batchall.py <list.json>` – records phrases with Gemini TTS batch API (env VOICE=Leda). Needs the Gemini API key in /home/claude/tts/.key (never commit it).
- `build6.py` – rebuilds voice_<track>_<n>.js bundles + CLIPS map in index.html from recorded mp3s, bumps cache versions.
- `rec_leda_all.json` – full list of recorded phrases.
Paths inside the scripts assume /home/claude/tts and /home/claude/kids-app/audio.

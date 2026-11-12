---
name: face-reel
description: Make a finished 1080x1920 face reel (talking-head video) for one of our mortgage-broker clients from a raw clip. Use when the user gives a raw video and wants it edited into a reel, or asks to start/redo a reel for a client.
---

# face-reel

Follow `CLAUDE.md` (the five rules and the pipeline). In short:

1. **Which client?** Ask if not stated. Load that client's folder (client.json, brand.json, compliance.json, voice.md, people-rules.json, learnings.md). If compliance.json is unfilled, stop and use `/new-client` first.
2. **Create the reel folder** `clients/<slug>/reels/<YYYY-MM-DD>_<short-name>/{raw,build,broll,out}`; move the raw clip into `raw/`.
3. **Toolchain check** (`vendor/ghost-editor/scripts/doctor.sh`); report what is missing.
4. **Ingest, transcribe, face-track, choose takes**, then write a **beat sheet** using `references/element-families.md` (3+ families, none back-to-back). Show it to the user.
5. **Build** in the client's brand; B-roll per the no-paid-generation rule; soft sound design with the voice dominant.
6. **QA gate**: compliance_check, loudness, contact sheet, captions vs face, safe zones, end-card legibility. Fix and re-check; report real results.
7. **Preview first**, wait for the user's OK, then final render into `out/`, and copy to the location the user asks for.
8. **Close out**: update `learnings.md`, list open confirmations.

If something needed is missing (brand files, licence number, footage rights, API key), ask. If a step fails, say so with the evidence.

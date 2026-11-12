# Face Reels Playbook

Everything we learned, built and collected while setting up an AI-assisted workflow for **face reels** (vertical 1080x1920 talking-head videos) for **mortgage-broker clients**: the research, the resources (every GitHub link with what it helps with), our own tools, the learnings and mistakes, the design standard, the licence/compliance rules, and a client template.

> **Private by default.** The docs mention that the first client was an Ontario mortgage brokerage but contain no client licence numbers, contact details, brand files, raw footage or API keys. Client data lives in each client's own private folder (see `templates/client`). Before making this repo public, re-read it once for anything you would not publish.

## Start here
| You want to... | Read |
|---|---|
| Understand what we learned (and avoid our mistakes) | [docs/01-learnings.md](docs/01-learnings.md) |
| Make a reel, step by step, with commands | [docs/02-workflow.md](docs/02-workflow.md) |
| Make graphics that do not look AI-generated | [docs/03-design-quality.md](docs/03-design-quality.md) and [docs/04-element-families.md](docs/04-element-families.md) |
| Pick the right resource for an outcome (and decide whether you need it) | [docs/05-choose-your-tools.md](docs/05-choose-your-tools.md) |
| See every GitHub link, licence and what it helps with | [docs/resources/github-repos.md](docs/resources/github-repos.md) |
| Check licences and the compliance gate | [docs/06-licences-and-compliance.md](docs/06-licences-and-compliance.md) |
| Set up a Mac from scratch | [docs/07-setup-macos.md](docs/07-setup-macos.md) |
| Run many clients from one agent | [docs/08-multi-client-architecture.md](docs/08-multi-client-architecture.md) |

## What is in the repo
```
docs/                    the knowledge base (above)
  resources/             github-repos.md (all links), asset-sources.md, design-skills scan catalog,
                         reviewed-engines notes, the raw awesome-list slice (TSV)
tools/                   our own scripts (cut plan, base cut, face data, person cut-out, frame renderer,
                         composer, sound mixer, on-screen text extractor, compliance checker, client scaffolder,
                         download helpers, catalog/generator tools)
templates/client/        client template: client.json, brand.json, compliance.json, voice.md, people-rules.json, learnings.md
agent/                   the parent agent's rules (CLAUDE.md) and two project skills (face-reel, new-client)
examples/
  reel-paper-collage/    the graphics template, behind-the-speaker layer and sound cue list from the reel that worked
  anti-patterns/         the two earlier versions the client rejected, kept to show what NOT to do
```

## The short version of what we found
1. **The pipeline works end to end on a laptop**: whisper.cpp (aligned word times) -> energy-based cut plan -> MediaPipe face data -> ffmpeg base cut -> HTML/CSS graphics rendered by Chromium frame by frame -> real foley sound -> two-pass ffmpeg compose -> automated QA (visible-text compliance check, loudness, contact sheets). A reel went from raw clip to finished in about an hour of work once the tools existed.
2. **What made graphics look "AI-made" was flat vectors, UI-card mockups, label rows and one repeated layout.** What fixed it was a single physical paper-collage world: scanned paper textures, photographic die-cut stickers, torn edges with correct shadows, hand-drawn marker strokes, a serif/sans type pair, decelerating arrivals, and words placed behind the speaker with a person cut-out.
3. **Word timings from a plain transcription are unreliable near silence.** Use token-level DTW alignment plus the measured audio energy.
4. **ffmpeg 9.0.2 can deadlock** when B-roll overlays and a PNG-sequence overlay share one filter graph: render in two passes with a timeout on every call.
5. **Licences matter for an agency**: several popular repos are noncommercial (ideas only); stock photos with brands, flyers or people must be avoided; one popular repo changed its licence after we cloned it.
6. **Compliance is a gate, not a hope**: extract the visible text and check required licence numbers, the exact disclaimer and forbidden claims before any final render.
7. **Be honest about progress**: verify from evidence (frames, bytes, measured loudness), not from file existence.

## Status and open items
- Reel 1 (v1 and v3) were rejected for look; Reel 2 (paper-collage) is the working standard.
- Open: confirm one ambiguous word ("cost"/"costs"), a client's social handle and agent-level wording, the brokerage's compliance review path, and obtain original (uncompressed) footage.
- Not yet used from the research: HyperFrames as the renderer, ghost-editor's own styles (Face RESULT / Tactile paper), the ClearerVoice audio clean-up (not needed for clean audio).

## Licensing of this repo
Our own scripts and docs have no licence file yet; add one before sharing. Third-party material is linked, not copied; see [docs/06-licences-and-compliance.md](docs/06-licences-and-compliance.md). The `examples/anti-patterns` and `examples/reel-paper-collage` HTML files are our own work and contain no client contact data.

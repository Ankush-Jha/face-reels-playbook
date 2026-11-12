# Which resource gets you what you want

Use this page like a menu. Find the outcome you want, then the type of resource that delivers it, then the specific repos or sites. Every link is explained in [resources/github-repos.md](resources/github-repos.md) (with licence and status). **Status** says what we actually did: `USED` (in our proven pipeline), `LIBRARY` (assets we downloaded), `REFERENCE` (read and borrowed ideas), `IDEAS-ONLY` (noncommercial licence: do not copy code into client work), `NOT TRIED`.

## A. Do you actually need these resources? (by person)

| If you are... | You probably want | You can skip |
|---|---|---|
| **A new editor making a first face reel** | The [workflow](02-workflow.md), the [design standard](03-design-quality.md), whisper.cpp, ffmpeg, the asset library (textures/photos/foley), one finished example to copy (`examples/reel-paper-collage`) | Remotion/HyperFrames frameworks, avatar tools, music-video skills |
| **An agency owner running many clients** | The multi-client structure ([08](08-multi-client-architecture.md)), `compliance_check.py`, `onscreen_text.py`, client templates, the licence table ([06](06-licences-and-compliance.md)) | Heavy local ML (matte, audio QA) until a client needs a "words behind the speaker" look |
| **A developer extending the tools** | `tools/`, HyperFrames, Playwright, rough.js, GSAP skills, ghost-editor internals, BiRefNet | Style packs |
| **A client's compliance reviewer** | `templates/client/compliance.json`, the on-screen text extraction, the numbers/claims policy | Everything creative |
| **Someone who only wants captions/cuts fast** | ghost-editor, claude-video-effects, SeeCut-style editors (check licences) | Our custom collage renderer |

## B. What do you want, and what kind of resource gets it?

### 1. "A clean cut: best takes, no dead air, word-timed captions"
Resource type: **transcription + silence analysis + auto-editor skill**.
- whisper.cpp (USED) for word times; ggml `small.en` model is enough for clear speech.
- Our `tools/plan_cut.py` (USED): silence trimming + punch-ins from measured energy.
- ghost-editor (REFERENCE/LIBRARY): take selection across retakes, `transcribe.py`, QA that checks captions against the face. Apple-silicon, MIT.
- yt-dlp (USED for study): download a reference reel by link to study its structure (respect platform terms; study, never reuse their footage).

### 2. "Graphics that look hand-made, not AI"
Resource type: **real materials + design-taste skills**.
- Textures: ambientCG (CC0) paper/cardboard scans (LIBRARY). Photos: Pexels (LIBRARY, with the brand/people rules in [06](06-licences-and-compliance.md)). Cut-outs: BiRefNet via `tools/cutout_image.py` (USED).
- Hand-drawn strokes: rough.js and rough-notation, MIT (USED).
- Fonts: Playfair Display, Caveat, Inter, SIL OFL (USED).
- Design-taste skills to read and apply: **motionmaxxing**, **motion-video-kit**, **motion-kit**, **30x-video**, **MotionCraft**, anthropic **frontend-design**, **gsap-skills** (REFERENCE). Their "never ship" lists are the fastest way to find slop.
- Paper looks as ready-made systems: papercut-explainer (24 paper backdrops, camera moves, tape/page-turn/stamp transitions), paper-reel, gbro-collage-info/gbro-collage-broll/VOX-COLLAGE-BROLL (halftone paper collage) (REFERENCE), eian-riso-broll (risograph; personal non-commercial licence: IDEAS-ONLY), lemo-opuscar (66 style recipes; docs are CC BY-NC with permission to follow them for films: read its LICENSE) (REFERENCE).

### 3. "Words behind the speaker / graphics that go around the head"
Resource type: **face tracking + person matting**.
- MediaPipe Face Landmarker (USED) for the face box.
- BiRefNet (USED): best-quality person cut-out via ghost-editor's `matte.py`.
- claude-video-effects (REFERENCE): 51 face-aware effects (orbit, spotlight, backdrop-word, comment-box, phone-fan, LED sign).

### 4. "Charts, diagrams, data"
Resource type: **dataviz principles + hand-drawn or minimal charts**.
- rough.js (hand-drawn diagrams), HyperFrames catalog (data blocks), the `dataviz` guidance in design skills. Label anything without client data `ILLUSTRATION`.

### 5. "Sound that does not sound like cheap beeps"
Resource type: **real foley library + measured mixing**.
- Mixkit SFX/music (free, commercial use; not for Content ID registration) and CC0 clips via ghost-editor's library (LIBRARY).
- motion-graphics `sound-effects` skill (REFERENCE): cue lists, beat grid, measured loudness.
- Our `tools/mix_sound.py` (USED).

### 6. "A renderer I can drive from code"
Resource type: **HTML-to-video or React-to-video frameworks**.
- Our Chromium/Playwright frame renderer (USED, simplest, deterministic).
- HyperFrames (Apache-2.0, HTML + GSAP, 449-block catalog) (INSTALLED, pinned 0.8.159, not needed for our reel).
- Remotion skills (REFERENCE).

### 7. "Fast one-click reels from a talking head"
Resource type: **end-to-end editor skills**. ghost-editor (34 styles incl. Face RESULT / Tactile paper), SeeCut (IDEAS-ONLY), Agent Motion (IDEAS-ONLY), claude-youtube-editor, claude-shorts. Check the licence before using for clients.

### 8. "Make it continuous, every beat growing out of the last"
Resource type: **method**. onetake (IDEAS-ONLY, PolyForm Noncommercial): measured continuity, shot lengths varying 4x or more, motion blur via sub-frame averaging, stillness. Take the ideas, not the code.

### 9. "Keep a client's look consistent across reels"
Resource type: **style/brand kit pattern**. lemo-opuscar's "make a style your own" flow (REFERENCE; see its mixed licence); our `templates/client/brand/brand.json` and per-client `learnings.md`.

### 10. "Find more resources"
- The awesome list: zhuyansen/awesome-claude-video-skills (469 repos, 10 types, security-graded by an automated model; the grades are not a guarantee). Live page: agentskillshub.top/best/claude-video-skills.
- HyperFrames catalog: hyperframes.heygen.com/catalog.

## C. Quick decision tree
1. Need just cuts and captions? ghost-editor or our plan_cut + build_base.
2. Need a custom, brand-specific look? Our renderer + the library + the design standard.
3. Need depth effects (behind the head)? MediaPipe + BiRefNet matte.
4. Client work? Check the licence column first; noncommercial means ideas only.
5. Anything with a number, rate or promise on screen? Run the compliance gate, and get the client's compliance contact to confirm.

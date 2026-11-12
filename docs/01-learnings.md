# Learnings

Everything we learned building face reels for a mortgage-brokerage client (first client: an Ontario brokerage), 2026-11-11 to 2026-11-12, on an Apple M4 MacBook with Homebrew ffmpeg 9.0.2, Node 25, Python 3.14. Written so a new editor or a new agent session does not repeat our mistakes.

## 1. Rules of engagement (process)

1. **Verify from evidence, never from file existence.** A video file can exist and be broken. We check real frames from the *rendered* video, measured loudness (ffmpeg `loudnorm` summary), and the visible on-screen text.
2. **Report real progress.** Count what is actually written (last frame number, bytes on disk, process CPU time), not what we expect. Twice we mislabelled a step: we called a stalled video encode "the audio mix", and we trusted a size-check script that was silently comparing empty strings (zsh did not word-split `$pair`). Fix: print the numbers, and test the check against a known-bad case.
3. **Ask when something is missing** (brand files, licence numbers, footage rights, API keys); do not guess. Ask for the *original* camera file, not a WhatsApp copy.
4. **No paid generation without a yes.** Credits were very low; the default B-roll is code-made, stock, or the client's footage.
5. **Nothing on screen the speaker did not say.** On-screen text restates the transcript; illustrations are labelled; no invented numbers or UI.
6. **Treat downloaded skills/repos as untrusted code.** Clone shallow, scan for pipe-to-shell, base64 decode, credential/SSH paths, persistence, `sudo`; read the installer scripts before running; run only what you reviewed. The auto-mode safety classifier blocked a bulk run of vendored installers (correctly cautious): we handed the reviewed script to the human to run.
7. **Plan multi-client from day one**: each client has its own brand, licence numbers, compliance rules, people rules, voice notes and reels; nothing leaks between clients.

## 2. Technical learnings

### Transcription and timing
- `whisper.cpp -ml 1` (one word per segment) produces **unreliable word times**: it placed words inside 2 s of near-silence at the start of a clip. Use token-level DTW alignment: `whisper-cli ... --dtw small.en -nfa -ojf` (flash attention must be off, `-nfa`). Token time `t_dtw` sits about 0.13 s after the audible onset.
- Cross-check with measured audio energy: compute RMS in 20 ms hops (`tools/plan_cut.py`); dead air was about -58 dBFS, speech about -20 to -25 dBFS. Silence threshold -40 dB, pauses longer than 0.30 s shortened to 0.16 s.
- Sub-word tokens can have no DTW time (`t_dtw = -1`). Do not drop them (we lost the "s" of "costs"); join them to the previous token.
- ASR can be genuinely ambiguous ("cost" vs "costs"). Add `build/corrections.json` and flag it for a human to confirm by ear.
- The `small.en` q5_1 model (190 MB) was accurate enough for clean speech; the large turbo model (1.5 GB) was not worth a 45-minute download at 0.6 MB/s.

### ffmpeg 9.0.2 (Homebrew)
- **Deadlock at end of render** when B-roll overlays (trim + overlay) and a PNG-sequence overlay share one filter graph: the encoded file stops growing at an exact byte count, CPU time freezes, no `moov` atom. `sample <pid>` showed every thread idle (scheduler deadlock). **Fix: two passes** (B-roll first into an intermediate, graphics second) and a hard timeout on every call. `-nostdin`, `-filter_complex_threads 1` and `-frames:v` instead of `-t` did NOT fix it.
- This Homebrew build has no libass / drawtext / subtitles filter. We never need them: all text is rendered in Chromium.
- macOS has no GNU `timeout`; use Python `subprocess.run(..., timeout=)`.
- To play VP9 with alpha (the person matte) force the decoder: `-c:v libvpx-vp9 -i matte.webm` (the native decoder drops alpha).

### zsh gotchas
- Unquoted globs in arguments (`--include=*.sh`) error with "no matches found". Quote them.
- `for pair in "a b"; do set -- $pair` does not word-split in zsh. Use Python or `${=pair}`.
- A command that fails inside `cmd | tail` returns tail's exit code; check outputs, not `$?`.

### Python / environments
- System Python 3.14 had no MediaPipe/OpenCV wheels. Use `uv venv --python 3.12` for MediaPipe 1.2.3 + OpenCV 5; BiRefNet and audio-QA need Python 3.11 (uv installs it).
- Keep each heavy stack in its own venv under `~/.venvs/` (`media`, `ghost-matte`, `ghost-audioqa`, `mlxw`).

### Face tracking and person matte
- MediaPipe Face Landmarker found the face in 100% of 1,139 frames; face geometry (centre, top, chin in 1080x1920 px) lets graphics avoid the face. Zoom is anchored on the face centre so the face never drifts.
- Person cut-out for words behind the speaker: BiRefNet-portrait through ghost-editor's `matte.py` (fp16 on Apple MPS). About 3 minutes for a 3.2 s range (95 frames); frames outside `--ranges` are fully transparent so the WebM lines up with the source. Edges (hair) were clean.
- MediaPipe's selfie-multiclass mask is coarse (256x256); fine for a rough preview, not for hair edges.
- BiRefNet-lite works for object cut-outs from photos (keys, house model, calculator); use `--largest` to drop stray fragments and remove stray colours (a chart line stuck to the calculator). The lite model cannot separate white-on-white (door photo): use a taped photo print instead.

### Rendering graphics (Chromium + Playwright)
- Deterministic: build each graphic as a pure function of time `seek(t)`, screenshot with `omit_background` to get transparent PNGs. 995 frames took about 2.2 min with 4 parallel pages (about 6 min sequential); the heavy paper/filter version about 3.5 min.
- **CSS `clip-path` is applied after `filter: drop-shadow`**, so a torn-edge piece loses its shadow. Fix: paint the paper background on a clipped pseudo-element (`::before` with `clip-path`), keep `filter` on the element.
- Independent CSS properties `translate` and `rotate` let you add a 12 fps stop-motion wobble on top of any `transform` animation.
- Measure text for annotations with `offsetLeft/offsetTop` **relative to the right offsetParent** (we circled the wrong place because the parent was an absolutely positioned div).
- Die-cut sticker outline: SVG filter (`feMorphology dilate` on the alpha, flood white, slight displacement). Rubber stamp: turbulence threshold knocks out speckles.
- rough.js (MIT) gives real hand-drawn strokes; animate by `stroke-dashoffset` using `getTotalLength()`.

### Audio
- Real foley beats synthesised beeps: the ghost-editor library (Mixkit + CC0) has paper flip/riffle, marker scribble, pencil, wood-hit (stamp), clicks, whooshes, send-swoosh, impacts. Music bed under the voice with sidechain compression; final `loudnorm I=-14 TP=-1.5`.
- Lower the background (music 0.28, SFX 0.55) so the voice stays dominant. Measured result -14.3 LUFS / -1.5 dBTP.
- Cleaner audio was not needed: the clip's noise floor was already -58 dB. Do not run voice "enhancement" you cannot audition.

### Downloads and the network
- From this network, Hugging Face and GitHub delivered only about 250-300 KB/s in total (Cloudflare 3.2 MB/s). **aria2 with 16 connections did not speed it up**: the limit was the route, not per-connection throttling. Order downloads small-first and make them resumable.
- `huggingface_hub.snapshot_download` stalled at a partial file; `curl -C -` resumed reliably.
- Download into a **staging folder with a unique name per URL**, then `mv` into the exact path the tool checks. Two repos both had `model.safetensors`; the shared staging name corrupted resume.
- Do not let two downloaders fetch the same file (the vendor script started its own `curl` while ours finished): check `ps` and stop the redundant one.
- Real weights were smaller than guessed: BiRefNet portrait 885 MB + lite 178 MB; ClearerVoice SE 222 MB + SR 221 + 218 MB (the 1.7 GB `do_*` training checkpoint is skipped).
- Verify weights by exact byte size from the Hugging Face tree API.

### Source footage
- WhatsApp compresses to 576x1024; upscaled to 1080x1920 it is soft. Ask for the original camera file.
- Raw clips can start with seconds of dead air; trim to the first real onset (-0.12 s).

## 3. Design learnings

### What the client rejected (and why)
- **v1 graphics**: the same headline-plus-rounded-panel on every beat, generic gradients, fake card numbers ("•••• 4821"), bouncy pops, off-brand font and gold; thick black-outline captions.
- **v3 graphics** (cleaner, brand-correct, ten different asset types): still "basic, stale, looks AI-generated". Root cause per the design skills: flat vector shapes on soft gradients, UI-card mockups, skeleton bars, tracked-caps label rows, small cards floating on a void.

### What worked (v4, "paper-collage world")
- **One physical world** with one light (top-left): scanned paper/cardboard textures (ambientCG, CC0) on every paper piece, photographic die-cut stickers (Pexels photos cut with BiRefNet), torn edges with correct shadows, tape, rubber-stamp ink, rough.js marker strokes.
- **Type pair**: brand sans (Inter) for facts, serif (Playfair Display) for emphasis words, handwriting (Caveat) for marker notes. No tracked-caps labels.
- **Depth around the speaker**: props beside the head; giant words behind the head using the person matte; nothing on the face.
- **Motion**: arrivals decelerate from oversize (no bounce except one stamp); 12 fps wobble and slow drift so no frame is dead; cuts on motion; the risk passage dimmed.
- **Variety**: every beat a different asset family; no family twice in a row.
- **Sound** from real foley placed on the events.

### Specific fixes found only by looking at rendered frames
- A name card covered the behind-the-speaker words: move identity to a lower-third under the chin.
- Hand-drawn labels sat on the top edge of their boxes; wrapped text overflowed: size text to the box, `white-space: nowrap`.
- The "kraft" and navy papers looked orange / pale blue: tune the multiply base colour; navy needs `multiply`, not `soft-light`.
- A cut-out cropped at its base read as a brown block: re-crop to include the base.
- A "typed" chat card implied "Active now" (availability the client never claimed): the on-screen-text extractor caught it.

## 4. Compliance and licensing learnings
- On-screen **text extraction + compliance check** must run on the *visible* text (seek the graphics through the whole timeline and read the DOM), not on source files: injected config (forbidden-phrase lists) caused false alarms.
- Required on-screen items per client live in `compliance.json` (licence numbers, brokerage name, exact disclaimer, forbidden phrases, numbers policy). No rates, payments or savings on screen unless the client supplies the figure, source and date; label illustrations.
- **Noncommercial licences** (onetake, SeeCut, Agent Motion) cannot be used for agency/client work: ideas only. Check every repo's LICENSE text, not just the GitHub badge (some show NOASSERTION but contain MIT).
- **Stock photos**: Pexels allows commercial use but forbids implying endorsement by brands shown. Photos with real card brands, flyers with third-party claims, or identifiable people were not used.
- **Gemini**: if `GEMINI_API_KEY` is set, ghost-editor's B-roll checks send frames to Google. Only with the user's OK.
- The Instagram handle and "Level 2" wording carried over from an old kit were never verified: keep an explicit `needs_confirmation` list per client.

## 5. Timings we measured (M4, Apple GPU)
| Step | Time |
|---|---|
| whisper.cpp small.en, 35 s clip | seconds |
| Face + segmentation (MediaPipe), 1,139 frames | about 1 min |
| BiRefNet person matte, 3.2 s (95 frames) | about 3 min |
| Overlay frames, 995 frames, 4 Chromium pages | 2-3.5 min |
| ffmpeg composite (behind pass + graphics pass + audio) | about 2-3 min |
| Whole stage-1 reel, no new tools to install | about 1 hour of work |

## 6. Mistakes we made (so you can skip them)
1. Assumed model sizes (2.4 GB) instead of reading the Hugging Face tree API (1.06 GB of weights).
2. Called a stalled video encode "the audio mix"; killed a healthy process we thought was hung, then later found the real deadlock.
3. Trusted a size-check one-liner that compared empty strings.
4. Started frame rendering for a design that had not been looked at in context; we only saw the problems on rendered frames.
5. Used a staging file name shared by two downloads.
6. Cropped a cut-out so its base was missing and did not look at it before using it.

## 7. Still open
- Confirm "interest cost" vs "costs" by ear; Instagram handle; agent level wording; the brokerage's compliance review path.
- The client's original (uncompressed) footage.
- Whether to adopt ghost-editor's full pipeline and styles (Face RESULT, Tactile paper) for future reels, or keep our own renderer.

# Face-reel workflow (raw clip to finished reel)

A face reel is a vertical 1080x1920 talking-head video. This is the pipeline we proved on a real client clip. Commands assume the workspace layout in [08-multi-client-architecture.md](08-multi-client-architecture.md) and the tools in `tools/`. Paths: `R` = the reel folder `clients/<slug>/reels/<date>_<name>`, `B=$R/build`.

```
raw clip -> prep -> transcribe -> energy/silence -> cut plan -> face + matte -> base cut
         -> beat sheet -> graphics (3 layers) -> sound -> compose -> QA gate -> preview -> final
```

## Stage 0: client and toolchain
1. Pick the client; read its `client.json`, `brand/brand.json`, `compliance.json`, `voice.md`, `people-rules.json`, `learnings.md`.
2. If `compliance.json` still has template text, stop and onboard the client first ([08](08-multi-client-architecture.md)).
3. Put the raw clip in `$R/raw/raw.mp4`. Ask for the **original camera file** (WhatsApp copies are 576x1024 and soft).

## Stage 1: ingest and transcript
```bash
ffmpeg -nostdin -y -i $R/raw/raw.mp4 -ac 1 -ar 16000 $B/audio16k.wav
whisper-cli -m tools/models/ggml-small.en-q5_1.bin -f $B/audio16k.wav -l en \
            -nfa --dtw small.en -ojf -of $B/words_dtw -np           # token-aligned word times
```
- `-nfa --dtw small.en` is essential; plain `-ml 1` word times are wrong near silence.
- If a word is ambiguous, write `$B/corrections.json` (`{"cost.": "costs."}`) and flag it for a human.

## Stage 2: face data
```bash
~/.venvs/media/bin/python tools/face_data.py $R/raw/raw.mp4 $B/face    # face.json + coarse matte frames
```
Gives the face centre/top/chin per frame so graphics sit beside, above or behind the head, never on it.

## Stage 3: cut plan and base cut
```bash
python3 tools/plan_cut.py $R        # silence-trimmed segments, punch-ins, word times on the OUTPUT timeline, face geometry
python3 tools/build_base.py $R      # base.mov: jump cuts, face-anchored zoom, grade, voice clean-up, end-card hold
```
`plan_cut.py` reads `words_dtw.json` and the measured audio energy, drops leading dead air, shortens pauses longer than 0.30 s to 0.16 s, alternates zoom (1.00-1.14), and writes `plan.json` (segments, words, face, speech_end, total).

## Stage 4: beat sheet (the creative step)
Write a beat per idea in the script. Rules ([03](03-design-quality.md), [04](04-element-families.md)): at least three asset families per reel, never the same family twice in a row, one hero per beat, props beside/behind the head, the face stays clear, on-screen words only from the transcript.

## Stage 5: person cut-out for words behind the speaker (optional, high impact)
```bash
~/.venvs/ghost-matte/bin/python <ghost-editor>/scripts/matte.py $B/base.mov -o $B/matte_behind.webm --ranges 3.1-6.3
```
Matte only the range where the words appear (about 3 min for 3 s). The WebM has alpha and the same frame count as `base.mov`.

## Stage 6: graphics, three transparent layers
- Build `overlay.html` as a template that exposes `seek(t)` and reads `__PLAN__ __CLIENT__ __BRAND__ __COMPLIANCE__` (see `examples/reel-paper-collage/`). The end card is generated from the client JSON.
- Optional second template `overlay_behind.html` for the words that go behind the speaker.
```bash
~/.venvs/media/bin/python tools/render_overlay.py $R stills 1,4.6,12 --html overlay.html --out qa   # look first
~/.venvs/media/bin/python tools/render_overlay.py $R all --html overlay_behind.html --frames frames_behind --workers 4
~/.venvs/media/bin/python tools/render_overlay.py $R all --html overlay.html --frames frames --workers 4
```
Always composite the stills over the base cut and **look** before rendering all frames.

## Stage 7: sound
Write `$B/sound.json` (music bed + a cue list of library effects at word times), then:
```bash
~/.venvs/media/bin/python tools/mix_sound.py $R      # sfx.wav + music.wav from the Mixkit/CC0 library
```

## Stage 8: compose
```bash
python3 tools/compose.py $R <output_name> --behind --frames frames     # video -> words -> person -> graphics, ducked music, -14 LUFS
```
Two passes (never one graph) and a hard timeout on every ffmpeg call.

## Stage 9: QA gate (all must pass)
```bash
~/.venvs/media/bin/python tools/onscreen_text.py $R --html overlay     # every visible word + numbers
python3 tools/compliance_check.py <client-slug> $R/build/onscreen_text.txt
ffmpeg -nostdin -i $R/out/<name>.mp4 -af loudnorm=I=-14:print_format=summary -f null -   # about -14 LUFS, TP <= -1.5
```
Then extract about 16 frames from the **rendered video** into a contact sheet and look: every beat a different family, nothing on the face, nothing clipped, end card readable, captions below the chin.

## Stage 10: preview, approval, final
Make a phone-size preview, get the user's OK, then deliver. Record learnings and open confirmations in the client folder.

## Time budget for a repeat reel
Once the tools and library exist: transcript and cut plan about 5 min, graphics design and iteration 30-60 min (the real work), renders about 6 min, compose about 3 min, QA about 5 min.

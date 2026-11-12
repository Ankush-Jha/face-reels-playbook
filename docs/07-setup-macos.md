# Setup on macOS (Apple silicon)

Tested on a MacBook Pro M4, macOS, Homebrew, Node 25.5, ffmpeg 9.0.2, Python 3.14 (system). About 8 GB of downloads in total. On a slow route to Hugging Face/GitHub (we measured 250-300 KB/s) allow 1-2 hours; everything resumes.

## 1. Base tools (Homebrew)
```bash
brew install ffmpeg node uv whisper-cpp yt-dlp aria2
brew install --cask font-inter font-caveat
```
Playfair Display is loaded straight from the woff2 files bundled with ghost-editor (`@font-face`), so it needs no install.
- aria2 did not speed up Hugging Face/GitHub from our network; it is still handy for resuming big files.
- ffmpeg from Homebrew 9.0.2 lacks libass/drawtext: fine for this pipeline.

## 2. Python environments (never use system Python 3.14 for ML)
```bash
uv venv --python 3.12 ~/.venvs/media
uv pip install --python ~/.venvs/media/bin/python numpy opencv-python pillow scipy mediapipe playwright google-genai
~/.venvs/media/bin/python -m playwright install chromium
```
`~/.venvs/ghost-matte` (BiRefNet, Python 3.11) and `~/.venvs/ghost-audioqa` (ClearerVoice, Python 3.11) are created by ghost-editor's own setup scripts.

## 3. Models (put under `tools/models/`, not committed)
```bash
mkdir -p tools/models && cd tools/models
curl -L -C - -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en-q5_1.bin     # 190 MB speech model
curl -L -O https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
curl -L -O https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
```
Use `curl -C -` (resumable); `huggingface_hub.snapshot_download` stalled for us.

## 4. ghost-editor engine and its heavy extras (review first!)
```bash
git clone --depth 1 https://github.com/kurbaitaev/ghost-editor vendor/ghost-editor
# read scripts/setup_matte.sh, setup_audioqa.sh, library_restore.py before running them
bash tools/prefetch_weights.sh      # our aria2 pre-fetch of the 5 big weights into the exact cache folders (resumable)
bash tools/setup_all.sh             # Python 3.11, media library (Mixkit), BiRefNet venv, audio-QA venv, pinned HyperFrames, doctor.sh
```
Expected doctor result for us: 20 ok, 2 missing (libass, openai-whisper CLI), neither needed.

Weights verified by exact size: BiRefNet-portrait 884,878,856 B; BiRefNet_lite 177,634,392 B; MossFormer2_SE 221,552,019 B; MossFormer2_SR 220,712,702 B + 218,471,889 B. Prefetch order: small and useful first.

## 5. Asset library (not committed; fetch it)
See [resources/asset-sources.md](resources/asset-sources.md) for source URLs and licences:
- ambientCG: `https://ambientcg.com/get?file=Paper001_1K-JPG.zip` (also Paper003, Cardboard002).
- Pexels photo direct URLs: `https://images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?auto=compress&cs=tinysrgb&w=1800`.
- rough.js: `https://cdn.jsdelivr.net/npm/roughjs@4.6.6/bundled/rough.js`; rough-notation 0.5.1.
- Fonts: copy `playfair-display-*.woff2`, `caveat-latin.woff2`, `inter-latin.woff2` from ghost-editor's `templates/fonts`.

## 6. Cut-outs from photos
```bash
~/.venvs/ghost-matte/bin/python tools/cutout_image.py library/photos/<photo>.jpg library/cutouts/<name>.png \
        --crop x0,y0,x1,y1 --largest [--grow -2]
```
About 6-15 s per object on Apple MPS.

## 7. Skills for the agent
Project skills live in `.claude/skills/` (symlinks to the vendored repos plus our own `face-reel` and `new-client`). Do not link flagged or noncommercial repos. Too many linked skills bloats the model's skill list; keep a curated set and leave the rest in the catalog.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| ffmpeg output has no `moov` atom, file stops at same size | ffmpeg 9.0.2 filter-graph deadlock (B-roll + PNG sequence in one graph) | Two passes; hard timeout |
| Words appear before they are spoken | whisper.cpp plain word times | `--dtw small.en -nfa` + energy check |
| `no matches found: --include=*.sh` | zsh globbing | Quote the glob |
| Check script says OK for everything | zsh did not word-split | Use Python to compare |
| Downloaded model file is partial | stalled `snapshot_download` | `curl -C -` resume; verify byte size |
| Two downloaders write the same file | a vendor script started its own curl | Stop the redundant process |
| Torn paper has no shadow | `clip-path` after `drop-shadow` | Paint paper on a clipped `::before` |
| Person-matte WebM shows no alpha in ffmpeg | native VP9 decoder drops alpha | `-c:v libvpx-vp9 -i file.webm` |
| Auto-mode blocks running vendor installers | classifier caution on external code | Review the scripts, then run them yourself in Terminal |

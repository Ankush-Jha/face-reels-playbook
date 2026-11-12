# Vendored engines: pinned commits and review status

Cloned 2026-11-12 with `git clone --depth 1`. Code was scanned before use (pipe-to-shell, eval/exec, credential and SSH access, keychain, persistence, unexpected hosts). Findings: nothing malicious. Benign hits noted below. **Do not update (`git pull`) without re-reading the diff.**

| Repo | Commit | Licence | Notes from review |
|---|---|---|---|
| kurbaitaev/ghost-editor | ce17272 | MIT | `osascript` is used only for macOS OCR of local frames (`ocr_text.js`); PyTorch `.eval()`; contacts Mixkit (sounds), Hugging Face (model weights), jsDelivr (JS libs), GitHub (Fluent emoji, MIT), and Google Gemini only if a key is set (frames leave the machine). Demo clips in the repo are watch-only. |
| Vibha-Ramprakash/claude-video-effects | a6c05c5 | MIT | no flagged patterns, no external hosts. Free starter of a paid studio. |
| 0xS4N4TG/papercut-explainer | ff8223a | MIT | no flagged patterns. Remotion library; 79 synthesised SFX and 8 music beds, no licences to clear. |
| haiderfarooq3/paper-reel | 9c5bc57 | MIT | no flagged patterns; needs whisper.cpp + Kokoro for voice. |
| pyang5166/gbro-collage-info | 0b97a81 | MIT | no flagged patterns; HyperFrames-based halftone paper-collage skill. |
| Barty-Bart/motion-graphics | 3d83d98 | MIT | one `eval()` of ffprobe's frame-rate fraction in `sound_pass.py` (low risk). |
| lemomo-ai/lemo-opuscar | 9eb7739 | MIT **at that commit; upstream has since moved to a mixed licence (code MIT, docs CC BY-NC 4.0 + permission to follow for films): re-read before reuse** | reference only: style recipes (`styles/*/STYLE.md`); tuned for Opus 5.5. Not scanned as deeply (not linked as a skill). |

## Noncommercial: not vendored, ideas only
onetake (PolyForm Noncommercial), SeeCut (appears noncommercial), Agent Motion (noncommercial). Do not copy their code into client work.

## Installed outside this folder
HyperFrames (Apache-2.0) runs via `npx hyperframes@<pinned>` (version in `vendor/ghost-editor/scripts/HF_VERSION`). whisper.cpp and yt-dlp via Homebrew. Python envs in `~/.venvs/`.

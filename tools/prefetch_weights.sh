#!/usr/bin/env bash
# Pre-fetch the big model weights with aria2 into the exact folders the vendored setup scripts check, so their
# single-stream downloads are skipped. Smallest / most useful first. Downloads to a staging folder and moves each
# file into place only when complete, so a half-finished file is never mistaken for a finished one.
# Safe to re-run (resumes). Sources: huggingface.co only.
# NOTE (measured 2026-11-12): from this network Hugging Face delivers only ~250-300 KB/s in total however many
# connections are used, so aria2 does not speed it up; it still gives resume + the ordering below.
set -u
STAGE="$HOME/.cache/prefetch_stage"; mkdir -p "$STAGE"
A=(aria2c -x16 -s16 -k1M -c --file-allocation=none --max-tries=0 --retry-wait=3 --console-log-level=warn --summary-interval=30 --allow-overwrite=true)

get(){ # get <url> <final dir> <file name>
  local url="$1" dir="$2" name="$3"
  mkdir -p "$dir"
  if [ -s "$dir/$name" ]; then echo "have  $dir/$name"; return 0; fi
  local key="${url//[\/:?=&]/_}"   # unique staging name per URL (two repos both have model.safetensors)
  echo "fetch $name  ($(date +%T))"
  "${A[@]}" -d "$STAGE" -o "$key.part" "$url" && mv "$STAGE/$key.part" "$dir/$name" && echo "done  $dir/$name"
}
birefnet(){ for f in birefnet.py BiRefNet_config.py config.json model.safetensors; do
  get "https://huggingface.co/ZhengPeng7/$1/resolve/main/$f" "$HOME/.cache/ghost-matte/hf/$1" "$f"; done; }

Q="$HOME/.cache/ghost-audioqa/clearvoice/checkpoints"
hf(){ echo "https://huggingface.co/alibabasglab/$1/resolve/main/$2"; }

birefnet BiRefNet_lite                                                     # 178 MB: fast person cut-out
get "$(hf MossFormer2_SE_48K last_best_checkpoint.pt)" "$Q/MossFormer2_SE_48K" last_best_checkpoint.pt   # 221 MB: voice clean-up
birefnet BiRefNet-portrait                                                 # 885 MB: best-quality person cut-out
get "$(hf MossFormer2_SR_48K last_best_checkpoint_g.pt)" "$Q/MossFormer2_SR_48K" last_best_checkpoint_g.pt  # 221 MB
get "$(hf MossFormer2_SR_48K last_best_checkpoint_m.pt)" "$Q/MossFormer2_SR_48K" last_best_checkpoint_m.pt  # 218 MB
# marker files last: they tell voice_enhance.py a model is complete
get "$(hf MossFormer2_SE_48K last_best_checkpoint)" "$Q/MossFormer2_SE_48K" last_best_checkpoint
get "$(hf MossFormer2_SR_48K last_best_checkpoint)" "$Q/MossFormer2_SR_48K" last_best_checkpoint
echo "PREFETCH DONE $(date +%T)"

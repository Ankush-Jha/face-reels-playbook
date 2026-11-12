#!/usr/bin/env bash
# Clone every repo in vendor/design-skills/LIST.tsv into vendor/design-skills/<owner>__<repo>.
# Shallow + partial clone (skips blobs > 1 MB such as GIF/MP4 previews). 4 in parallel; stalled connections abort.
# Nothing is executed or linked as a skill here; scanning and enabling are separate, deliberate steps.
set -u
D="$HOME/Desktop/FACE_REELS_AGENT/vendor/design-skills"; cd "$D" || exit 1
fetch(){
  r="$1"; n="${r/\//__}"
  top="$HOME/Desktop/FACE_REELS_AGENT/vendor/${r#*/}"
  if [ -d "$n/.git" ] || [ -d "$top/.git" ]; then echo "have   $r"; return 0; fi
  for try in 1 2 3; do
    if git -c http.lowSpeedLimit=2000 -c http.lowSpeedTime=45 clone -q --depth 1 --filter=blob:limit=1m "https://github.com/$r.git" "$n" 2>/dev/null; then
      echo "ok     $r  $(git -C "$n" rev-parse --short HEAD)  $(du -sh "$n" | cut -f1)"; return 0
    fi
    rm -rf "$n"; sleep 3
  done
  echo "FAILED $r"
}
export -f fetch; export D
cut -f1 LIST.tsv | xargs -P4 -I{} bash -c 'fetch {}'
echo "FETCH DONE $(date +%T)"

#!/usr/bin/env python3
"""Generate docs/resources/github-repos.md from the awesome-list slice (LIST.tsv) and the scan catalog (CATALOG.md).

    python3 tools/gen_resources.py <path-to>/design-skills-list.tsv <path-to>/CATALOG.md > docs/resources/github-repos.md
"""
import re, sys

CORE = [
 # (name/repo, url, licence, status, helps with, who needs it)
 ("zhuyansen/awesome-claude-video-skills","https://github.com/zhuyansen/awesome-claude-video-skills","other/see repo","REFERENCE","Index of 469 repos that let coding agents make video, 10 types (frameworks, promo, explainers, editing, shorts, avatars, stories, motion graphics, scripts, music), each graded by an automated model. Live page: https://agentskillshub.top/best/claude-video-skills/","Anyone looking for more tools"),
 ("ffmpeg/ffmpeg","https://github.com/ffmpeg/ffmpeg","LGPL/GPL (build-dependent)","USED","Cuts, zooms, grade, audio chain, loudness, overlays, muxing. Watch for the 9.0.2 filter-graph deadlock (two passes + timeouts).","Everyone"),
 ("heygen-com/hyperframes","https://github.com/heygen-com/hyperframes","Apache-2.0","INSTALLED (pinned 0.8.159)","HTML + GSAP to deterministic MP4; docs https://hyperframes.heygen.com ; 449-block catalog (captions, shader transitions, 3D, data charts, halftone/paper surfaces). Studio app free.","Developers who want a framework; not needed for our own renderer"),
 ("google-ai-edge/mediapipe","https://github.com/google-ai-edge/mediapipe","Apache-2.0","USED","Face Landmarker (face box per frame) and selfie segmentation; keeps graphics off the face.","Anyone doing face-aware layout"),
 ("yt-dlp/yt-dlp","https://github.com/yt-dlp/yt-dlp","Unlicense","USED (for study)","Download a reference reel by link to study its structure and pacing. Study only; never reuse others' footage.","Editors studying references"),
 ("ggml-org/whisper.cpp","https://github.com/ggml-org/whisper.cpp","MIT","USED","Local transcription with word times; use `--dtw small.en -nfa` for accurate token alignment.","Everyone"),
 ("feitangyuan/onetake","https://github.com/feitangyuan/onetake","PolyForm Noncommercial","IDEAS-ONLY","Method for continuous, every-beat-grows-from-the-last films; measured continuity; shot lengths vary 4x+; real motion blur. Pro licence $79 for commercial.","Agencies: ideas only"),
 ("MegaTroll222/VOX-COLLAGE-BROLL","https://github.com/MegaTroll222/VOX-COLLAGE-BROLL","MIT","REFERENCE","One spoken line to a halftone paper-collage explainer; three-gate approval flow, locked visual language, self-QA. Needs MaxFusion MCP (paid, third-party) for generation.","Those wanting the collage look via generation"),
 ("lemomo-ai/lemo-opuscar","https://github.com/lemomo-ai/lemo-opuscar","MIXED: code MIT; docs/style recipes CC BY-NC 4.0 + permission to follow them to make films (commercial OK); embedding the docs in your own product needs a commercial licence. Upstream changed from plain MIT after we cloned: read its LICENSE","REFERENCE","66 film-style recipes (hand-drawn, print, paper, infographic, evidence films); 'make a style your own' flow; tuned for Opus 5.5; 30-60 min per film.","Art directors wanting style recipes"),
 ("kurbaitaev/ghost-editor","https://github.com/kurbaitaev/ghost-editor","MIT","USED (library, matte) / REFERENCE","Raw talking-head take in, reel out: take selection, face tracking, captions that avoid the face, 34 styles (Face RESULT, Tactile paper, Caption News...), SFX/music library, BiRefNet person matte, QA. Apple silicon.","Editors wanting an end-to-end pipeline"),
 ("Vibha-Ramprakash/claude-video-effects","https://github.com/Vibha-Ramprakash/claude-video-effects","MIT","REFERENCE","51 face-aware effects: orbit, spotlight, backdrop word, comment box, phone fan, LED sign, slow push.","Editors wanting quick effects"),
 ("0xS4N4TG/papercut-explainer","https://github.com/0xS4N4TG/papercut-explainer","MIT","REFERENCE","Cut-paper reels: 24 paper backdrops, 17 camera moves, 10 paper transitions (tape-pull, page-turn, tear-away, stamp), 79 synthesised SFX, 8 music beds.","Paper-look builders"),
 ("haiderfarooq3/paper-reel","https://github.com/haiderfarooq3/paper-reel","MIT","REFERENCE","Faceless cut-paper explainer reels; voice is the clock; whisper.cpp word timing; free, local.","Paper-look builders"),
 ("pyang5166/gbro-collage-info","https://github.com/pyang5166/gbro-collage-info","MIT","REFERENCE","Halftone paper-collage info animations from a script; hard rules (one idea per cut-out, one accent per frame, info in top two-thirds, never fake UI).","Info-graphic builders"),
 ("pyang5166/gbro-collage-broll","https://github.com/pyang5166/gbro-collage-broll","MIT","REFERENCE","Original (Chinese) of VOX-COLLAGE-BROLL; first/last-frame assembly animation.","Collage-look builders"),
 ("YIAN6557/eian-riso-broll","https://github.com/YIAN6557/eian-riso-broll","Eian Personal Non-Commercial License 1.0 (custom)","IDEAS-ONLY","Risograph two-colour info animations for talking-head videos (bundled GSAP keeps its own licence).","Agencies: ideas only"),
 ("Barty-Bart/motion-graphics","https://github.com/Barty-Bart/motion-graphics","MIT","REFERENCE","Skills: motion B-roll timed to words, object separation, explainers, and a measured sound-effects pass.","Motion editors"),
 ("Tejashmakwana/motionmaxxing","https://github.com/Tejashmakwana/motionmaxxing","Apache-2.0","REFERENCE (design standard)","'Never ship' list and craft laws that separate motion-designer work from AI slop; gates computed on the render.","Anyone judging quality"),
 ("echris6/motion-video-kit","https://github.com/echris6/motion-video-kit","MIT","REFERENCE","Independent critic loop, quality bar and motion principles from 28 launch films.","Anyone judging quality"),
 ("hughminhphan/motion-kit","https://github.com/hughminhphan/motion-kit","MIT","REFERENCE","Motion curves per move, timing from distance, reactions not staggers.","Motion editors"),
 ("iart-ai/kinetic-typography-skills","https://github.com/iart-ai/kinetic-typography-skills","MIT","REFERENCE","Kinetic typography skills: turn text into beat-synced animated type for social, titles and lyric videos.","Type-led motion"),
 ("norahe0304-art/30x-video","https://github.com/norahe0304-art/30x-video","MIT","REFERENCE (design standard)","A 16-law 'taste codex' for agency-grade launch videos (Remotion + React): one URL in, a film with its own design world out.","Anyone judging quality"),
 ("ahmdd4vd/MotionCraft","https://github.com/ahmdd4vd/MotionCraft","MIT","REFERENCE","Clean, high-taste motion-graphics videos made by an agent with Remotion; one-command install.","Remotion users"),
 ("greensock/gsap-skills","https://github.com/greensock/gsap-skills","MIT","REFERENCE","Official GSAP skills: correct timelines, plugins, performance (HyperFrames builds on GSAP).","Developers"),
 ("anthropics/skills","https://github.com/anthropics/skills","no repo-level licence on GitHub; check each skill folder","REFERENCE","Anthropic's official skills incl. frontend-design (design direction that avoids generic looks), canvas-design, brand-guidelines, theme-factory.","Anyone building visual output"),
 ("remotion-dev/skills","https://github.com/remotion-dev/skills","no repo-level licence on GitHub; Remotion itself has its own company licence (check before commercial use)","REFERENCE","Remotion's own skills for React-based video.","Developers using Remotion"),
 ("YeJe-cpu/SeeCut","https://github.com/YeJe-cpu/SeeCut","appears noncommercial","IDEAS-ONLY","Talking-head editor that watches its own cut; pairwise AI judging; real-evidence screenshots instead of fake UI.","Agencies: ideas only"),
 ("erduo1998-cell/erduo-broll-loop-engineering","https://github.com/erduo1998-cell/erduo-broll-loop-engineering","MIT (discontinued)","REFERENCE","SRT-driven B-roll with Director/Creator/Reviewer roles and 152 shot cards. Successor Agent Motion is noncommercial.","Reference"),
 ("ZhengPeng7/BiRefNet","https://github.com/ZhengPeng7/BiRefNet","MIT","USED (weights from Hugging Face)","Person and object cut-outs (portrait for people, lite for objects).","Anyone doing cut-outs"),
 ("rough-stuff/rough","https://github.com/rough-stuff/rough","MIT","USED","rough.js: real hand-drawn-looking SVG/canvas strokes (boxes, arrows, circles, fills).","Anyone making diagrams look hand-made"),
 ("pshihn/rough-notation","https://github.com/pshihn/rough-notation","MIT","LIBRARY","Animated hand-drawn annotations (underline, box, circle, highlight, strike).","Annotation effects"),
 ("microsoft/playwright","https://github.com/microsoft/playwright","Apache-2.0","USED","Headless Chromium for deterministic frame-by-frame rendering of HTML graphics.","Developers"),
 ("astral-sh/uv","https://github.com/astral-sh/uv","Apache-2.0 / MIT","USED","Fast Python installs and per-tool virtual environments (3.11, 3.12).","Developers"),
]

def main():
    lst, cat = sys.argv[1], sys.argv[2]
    stars = {}
    for ln in open(lst):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 2: stars[p[0]] = (p[1], p[2] if len(p) > 2 else "")
    rows = []
    for ln in open(cat):
        if ln.startswith("| ") and not ln.startswith("| Repo") and not ln.startswith("|---"):
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 7: rows.append(c)
    out = ["# GitHub resources: every link, what it helps with, whether you need it", "",
           "Generated 2026-11-12 from our research (user-supplied repos, the awesome-claude-video-skills list, and a bulk clone of its motion/design slice). Stars are as listed then. 'Status' says what we did with it; see [../05-choose-your-tools.md](../05-choose-your-tools.md) to pick by outcome.", "",
           "## A. Core stack and the repos you asked about", "",
           "| Repo | Licence | Status | What it helps with | Who needs it |", "|---|---|---|---|---|"]
    for n, u, lic, st, h, w in CORE:
        out.append(f"| [{n}]({u}) | {lic} | {st} | {h} | {w} |")
    out += ["", "## B. Other sites and libraries (not GitHub)", "",
            "| Site | What it gives | Licence |", "|---|---|---|",
            "| https://ambientcg.com | CC0 PBR textures (paper, cardboard); API docs https://docs.ambientcg.com | CC0 |",
            "| https://www.pexels.com | Free stock photos/videos; license https://www.pexels.com/license/ | Pexels licence |",
            "| https://mixkit.co | Free SFX and music | Mixkit licence |",
            "| https://roughjs.com | rough.js docs | MIT |",
            "| https://hyperframes.heygen.com | HyperFrames docs, catalog, lessons | Apache-2.0 |",
            "| https://agentskillshub.top/best/claude-video-skills/ | Live, filterable version of the awesome list | n/a |",
            "| https://fonts.google.com | Inter, Playfair Display, Caveat, Montserrat | SIL OFL |", "",
            f"## C. Design and motion skills we cloned and scanned ({len(rows)} repos)", "",
            "Verdicts: **ENABLE-OK** = permissive licence and no scan flags; **REVIEW** = a scan flag or no/unclear licence (read the flagged lines before enabling; many flags are test fixtures or install docs); **IDEAS-ONLY** = noncommercial; **REFERENCE** = no SKILL.md. Scan looked for pipe-to-shell, base64 decode, credential/SSH paths, persistence, sudo. Nothing was executed.", "",
            "| Repo | Stars | Licence | Skills | Verdict | Scan flags | What it says it does |", "|---|---:|---|---:|---|---|---|"]
    for name, lic, n, size, verdict, flags, desc in [(c[0], c[1], c[2], c[3], c[4], c[5], c[6]) for c in rows]:
        s = stars.get(name, ("", ""))[0]
        s = s if re.match(r"^[0-9.]+k?$", s) else ""
        out.append(f"| [{name}](https://github.com/{name}) | {s} | {lic} | {n} | {verdict} | {flags} | {desc} |")
    print("\n".join(out))

main()

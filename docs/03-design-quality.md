# Design quality standards for face reels

Distilled 2026-11-12 from the motion-design skills we fetched (motionmaxxing, motion-video-kit, motion-kit, gsap-skills, anthropic frontend-design, papercut-explainer, gbro-collage-info) and from the client's rejections of Reel 01 v1 and v3. Read before planning any beat.

## What reads as "AI slop" (never ship)
- Page chrome: tracked-caps label rows with hairlines, counters, scene labels, corner tags.
- Generic web-component UI: rounded cards with status dots, skeleton bars, notification banners, chat bubbles, toggles.
- Deck layouts: a left-aligned headline block with a kicker above it; small cards floating on an empty void.
- Flat vector shapes on soft gradients; the same panel look repeated beat after beat.
- Invented numbers, fake card numbers, fake UI, stat walls.
- Fades between beats; bounce on every entrance; everything the same size.

## What makes it feel made by a person
1. **One built world.** One light source (top-left), one material logic, one drawing logic. Here: a tactile paper-collage world.
2. **Real materials.** Scanned paper and cardboard (ambientCG CC0) on every paper piece; photographic die-cut stickers (Pexels photos cut with BiRefNet, white border from the object's own silhouette); torn edges whose shadow follows the tear; tape; rubber-stamp ink; rough.js hand-drawn strokes (marker boxes, arrows, circles) drawn on over time.
3. **Type pair with intent.** Brand sans (Inter) for facts, a serif (Playfair Display) for emphasis words, a handwriting face (Caveat) only for marker annotations. No tracked-caps labels.
4. **Depth around the speaker.** Props beside and behind the head; words behind the speaker use the person matte (BiRefNet). Never on the face.
5. **Arrivals decelerate from oversize**: most travel in the first frames, a long tail, no bounce; leaves ease out. About one visible overshoot per film (the stamp). Almost nothing fades; things arrive by moving, cutting, unmasking, wiping.
6. **No dead frame**: every held object keeps one living thing (12 fps stop-motion wobble, slow drift). Cuts happen on motion.
7. **Emphasis is spent, not spread**: one hero per beat, one accent colour, the loudest beat is the point of the script; the risk passage is deliberately quieter and darker (tone dim).
8. **Words move at speech rhythm**: graphics land on the spoken word (cue from word times), not before.
9. **Sound is physical**: real paper, marker, wood-thud, click, swoosh foley placed on the events; voice always dominant; music low.
10. **Honest content**: on-screen text restates the transcript only; illustrations are labelled; no brand logos or real card brands from stock photos.

## Checklist before showing the user
- Contact sheet of every beat from the RENDERED video (not stills): is each beat a different asset family? any HUD/label rows? any text clipped or touching the face?
- tools/onscreen_text.py + tools/compliance_check.py pass; numbers on screen are traceable.
- Loudness about -14 LUFS, true peak <= -1.5 dBTP.
- Asset provenance in library/SOURCES.md; no photo with identifiable people or third-party brand/text.

## Where the building blocks live
`library/` (textures, photos, cutouts, fonts, js), `tools/cutout_image.py`, `tools/render_overlay.py`, `tools/compose.py --behind`, `tools/mix_sound.py`, and the reference build `examples/reel-paper-collage/overlay.html`.

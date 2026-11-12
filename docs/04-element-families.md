# Element families and beat-sheet rules

A face reel is built from beats. Every beat uses an element from one family. The look comes from mixing families on purpose, in the client's brand.

## Beat-sheet rules
1. Use **at least three families** in one reel; never use the same family in two consecutive beats.
2. One idea per beat; one accent colour per frame; no more than two on-screen text blocks at once.
3. Vary shot length by 4x or more (some 0.8 s beats, some 3 s holds). Include stillness: rests make moves land.
4. The face is the product. Put props beside, behind or around the speaker, not over the face (use face.json). Words behind the head need the person matte.
5. Info stays in the top two-thirds (y <= 1280 at 1080x1920); the bottom ~640 px is caption and platform-UI safe area.
6. Every beat names what it carries over from the previous one when possible (a shape that becomes the next thing).
7. Real or abstract, never fake: no invented UI, numbers or logos. Use placeholders (grey bars) until a real asset exists; label illustrations.
8. Sound is part of the beat: soft whoosh on entry, tick on a UI action, chime on a "done" state, low sub-hit on the end card.

## Families (pick from these)
| Family | Elements |
|---|---|
| Paper and collage | cut-paper backdrops, torn caption scraps, tape, pins, stamps, polaroids, sticky notes, page folds and page-turn cuts, halftone cut-outs, 10 fps stop-motion jitter, paper grain |
| Print | risograph misregistration, newsprint headline strip, woodcut or engraving panels, silkscreen poster blocks, halftone dossier |
| Hand-drawn | marker circles, arrows and underlines, scribbles around the speaker, whiteboard or chalkboard split, handwriting write-on, freeze-frame with drawn arrow |
| Data and finance | story-first line/bar charts, ledger rows, rate dials and gauges, count-ups, timelines, tier lists, before/after sliders, statements and receipts, calendars |
| UI mock | notifications, DM composer typing, comment box, toggles, checklists, glass widgets, phone fan |
| Spatial and 3D | words behind the head, orbit around the head, spotlight, carousel, isometric house or city, exploded stack, flow ribbons that merge, decision forks |
| Camera and cuts | whip, zoom-through, match cut, rack focus, slow push, handheld drift, tape-pull, stamp cut, tear-away |
| Surfaces and look | film grain, halftone fields, paper board, ink bleed, gate weave, LED sign, vignette, colour grade |
| Identity | name badge with brand motif, lower third, logo ring watermark, end card |

## Mortgage-broker asset pack (build once per client, in their brand)
house key, house silhouette (paper-cut and line versions), calendar, calculator, contract and pen, stack of bills, rate dial, amortisation-style step chart (ILLUSTRATION), maple leaf or regional motif where the client uses it, handshake-free "keys handover" shot, sold-sign alternatives that are not misleading.

## Where to get ready-made versions
- ghost-editor styles: Face RESULT (paper props beside the speaker), Tactile paper, Caption News, Whiteboard, Step Deck, Halftone Dossier, Swiss Grid, Telestrator.
- claude-video-effects: 51 face-aware effects (orbit, spotlight, backdrop-word, comment-box, tier-list, phone-fan, led-sign, slow-push).
- papercut-explainer / paper-reel / gbro-collage-info: paper backdrops, camera moves, paper cuts, collage rules.
- HyperFrames catalog: captions (karaoke, highlight, parallax behind subject), shader transitions, halftone and paper surfaces, data charts, 3D.
- lemo-opuscar STYLE.md files: recipes for print, hand-drawn and infographic looks (reference only; tuned for Opus 5.5).

# Licences and compliance

Not legal advice. Verified by reading each repo's LICENSE text on 2026-11-12. Re-check before relying on it; licences change.

## 1. Tool and skill licences (what can be used for client/agency work)

| Resource | Licence | Client work? |
|---|---|---|
| HyperFrames (heygen-com/hyperframes) | Apache-2.0 | Yes |
| ghost-editor (kurbaitaev) | MIT (its demo clips: watch only; sound from Mixkit) | Yes (do not reuse its demo media) |
| claude-video-effects (Vibha-Ramprakash) | MIT (repo shows NOASSERTION on GitHub; the LICENSE file is MIT) | Yes |
| papercut-explainer, paper-reel, gbro-collage-info, gbro-collage-broll, VOX-COLLAGE-BROLL, motion-graphics (Barty-Bart), motionmaxxing (Apache-2.0), motion-video-kit, motion-kit, gsap-skills, kinetic-typography-skills | MIT / Apache-2.0 | Yes (keep notices) |
| **lemo-opuscar** (lemomo-ai) | **Mixed (changed after we cloned it)**: code MIT; Markdown docs and style recipes CC BY-NC 4.0 with an extra permission for you, your staff, contractors and the client to read, follow and copy them to make films; "films you make are yours, commercial films included"; Clawd/Anthropic marks excluded | Yes to follow its recipes for client films; **no** to embedding its docs in your own product/service. Read its LICENSE |
| whisper.cpp | MIT | Yes |
| MediaPipe | Apache-2.0 | Yes |
| yt-dlp | Unlicense | Tool is fine; what you download is governed by its owner and the platform |
| ffmpeg | LGPL/GPL (depends on build) | Using the output is fine |
| rough.js, rough-notation | MIT | Yes |
| BiRefNet weights (ZhengPeng7) | MIT | Yes. Note: rembg's default `bria-rmbg` needs a paid licence and is refused by ghost-editor |
| ClearerVoice weights (alibabasglab) | Apache-2.0 | Yes |
| **onetake** (feitangyuan) | **PolyForm Noncommercial 1.0.0** (Pro $79 adds commercial use) | **No: ideas only** |
| **SeeCut** (YeJe-cpu) | appears noncommercial (LICENSE text begins with a "Required Notice" form) | **No: ideas only** (verify) |
| **Agent Motion** (erduo1998-cell) | noncommercial; written permission needed | **No: ideas only** |
| **eian-riso-broll** (YIAN6557) | Eian Personal Non-Commercial License 1.0 (custom, not open source) | **No: ideas only** |
| erduo broll-loop-engineering | MIT but project discontinued | Yes, unmaintained |
| MaxFusion MCP (needed by VOX-COLLAGE-BROLL) | paid third-party service | Content goes to their service |

An agency is a business: "noncommercial" licences exclude it even if the individual editor says it is fine. Only the author can waive a licence.

## 2. Asset licences
| Asset | Licence | Rule |
|---|---|---|
| ambientCG textures | CC0 | Free, no attribution |
| Pexels photos | Pexels licence | Free commercial use; **do not imply endorsement by people or brands shown**; do not resell unaltered copies; you are responsible for model releases if identifiable people |
| Mixkit sound effects and music | Mixkit licence | Free commercial use; music not for Content ID registration, TV/radio/games |
| CC0 sound clips (ghost-editor library) | CC0 | Free |
| Playfair Display, Caveat, Inter, Montserrat | SIL OFL | Free to use and embed |

**Rules we adopted**
- No stock photo showing real bank/credit-card brands, third-party flyers or claims, or identifiable people. (We rejected a credit-card photo with a visible brand name, and a keys photo lying on a real mortgage flyer.)
- Keep `library/SOURCES.md` updated with every asset's source, ID and licence.

## 3. Compliance for mortgage-broker reels (starting defaults; the client decides)
Per client, `compliance.json` holds:
- `require_all_strings`: licence numbers and brokerage name that must appear.
- `require_disclaimer`: the exact end-card sentence.
- `forbid_patterns`: words never allowed ("guaranteed", "best rate", "lowest rate", "no credit check"...).
- `numbers_policy`: no rates, payments, savings or percentages unless the client supplies figure, source and date; mark charts without client data `ILLUSTRATION`.
- `claims_policy`: educational language only ("may", "depending on your situation", "subject to approval").
- `reviewer`: who at the client or brokerage reviews content and how fast.

**Gate before a final render**: `compliance.json` filled with real values; `tools/onscreen_text.py` + `tools/compliance_check.py` pass on the VISIBLE text; the end card is read in the real rendered frame (disclaimer at least 24 px at 1080 wide, end card shown at least 3 s); a human at the client confirms anything unusual. The tools check text, they do not replace a regulator-aware review.

**Things the gate caught or taught us**
- "Active now" in a chat mock-up implied availability the client never claimed: removed.
- On-screen numbers must be traceable (licence, phone, address, or the transcript).
- A risk passage in the script ("moving unsecured debt into debt secured against your home") must stay on screen and audible; we dimmed and slowed the visuals there on purpose.

## 4. Data and privacy
- Client footage, licence numbers, contact details and brand files live only in the client's private folder; this playbook repo contains templates only.
- ghost-editor can send sampled frames to Google Gemini if `GEMINI_API_KEY` is set. Ask first; client footage leaves the machine.
- Do not commit raw footage, API keys, `.env` files or licensed photos.

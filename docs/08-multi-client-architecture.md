# Multi-client architecture (one parent agent, many brokerage clients)

We are an agency that makes face reels for several mortgage-broker clients. One parent agent runs the shared pipeline; every client is a sealed folder. Nothing is shared between clients by accident.

```
workspace/
  CLAUDE.md                the parent agent's rules (see agent/CLAUDE.md)
  clients/
    _template/             copy of templates/client; seeds a new client
    <client-slug>/
      client.json          people, licences, company, contact, socials, languages, platforms, needs_confirmation
      brand/brand.json     colours, fonts, logo variants, motif, motion and sound feel
      brand/logo*.png      logos (light, dark, mark-only), brand/fonts/
      compliance.json      required strings, exact disclaimer, forbidden phrases, numbers/claims policy, reviewer
      voice.md             tone, words to use/avoid, script spine, topics never to cover
      people-rules.json    rules for who/what may appear in B-roll (only if the client asked)
      learnings.md         what the client approved/rejected, per reel
      assets/              client-supplied media (photos, B-roll, face reference)
      reels/<date>_<name>/ raw/  build/  broll/  out/
  vendor/                  third-party engines at pinned, reviewed commits
  library/                 shared textures, photos, cut-outs, fonts, js (licence-tracked)
  references/              design standard, element families, studied reels
  tools/                   our scripts
```

## Rules the parent agent follows
1. **Client first**: every job starts with "which client?". Load its folder before planning. Never use another client's logo, footage, script, colours or learnings.
2. **Compliance gate**: no final render until `compliance.json` is filled with real values and the visible-text check passes.
3. **Brand-driven rendering**: graphics templates read `client.json`, `brand.json` and `compliance.json` at render time, so the end card, name tag and colours come from the client folder, never from code.
4. **Per-client learnings** are appended after each reel and read before the next one.
5. **No paid generation** without approval; **no noncommercial code** in client work.

## Onboarding a new client
```bash
python3 tools/new_client.py <slug> "<Display Name>"      # copies the template, replaces placeholders
```
Then collect (never guess): people on camera (name, role, licence number, a clear face photo), company (legal name, brokerage licence, regulator, jurisdiction, address, website, phone, email, socials), brand (guide or logo files, colours, fonts; if only a website exists, read colours/fonts from it and say so in `source_of_truth`), compliance (required text, exact disclaimer, forbidden claims, reviewer), voice, CTA, languages, platforms. List anything unconfirmed in `needs_confirmation`. The agent must refuse to start a reel for a client whose `compliance.json` still has template text (`compliance_check.py` flags it).

## Adding a reel
Create `clients/<slug>/reels/<YYYY-MM-DD>_<short-name>/{raw,build,broll,out}`, move the raw clip into `raw/`, and follow [02-workflow.md](02-workflow.md).

## Why folders, not a database
Everything is plain JSON/Markdown: easy to review with the client, easy to diff, easy for a new editor to read, and the agent can load a client's whole context with a few file reads.

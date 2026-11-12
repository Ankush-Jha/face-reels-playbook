---
name: new-client
description: Onboard a new mortgage-broker client into the FACE REELS workspace: create their folder from the template and collect brand, licence, compliance and voice details. Use when the user mentions a new client, brand, broker or agent we have not made reels for yet.
---

# new-client

1. Ask the user for the client's display name; derive a slug (lowercase, hyphens).
2. Run `python3 tools/new_client.py <slug> "<Display Name>"` from the workspace root.
3. Collect, asking the user for anything missing (never guess licence numbers, handles or disclaimer wording):
   - People on camera: name, role, licence number, one clear face photo -> `assets/people/`.
   - Company: legal name, brokerage licence number, regulator and jurisdiction, address, website, phone, email, social handles.
   - Brand: official brand guide or logo files (light, dark, mark-only), colours, fonts. If only a website exists, read colours/fonts from it and mark `source_of_truth` accordingly.
   - Compliance: required on-screen text, exact disclaimer, forbidden claims, who reviews content and how fast.
   - Voice: tone, words to use/avoid, topics to avoid, CTA, languages, platforms.
   - B-roll people rules only if the client asked for any.
4. Fill `client.json`, `brand/brand.json`, `compliance.json`, `voice.md`; put logos in `brand/`, fonts in `brand/fonts/`.
5. List anything unconfirmed in `client.json -> needs_confirmation`.
6. Run `python3 tools/compliance_check.py <slug> clients/<slug>/brand`: it must no longer complain about template placeholders before any reel is made.
7. Tell the user what is still missing. Do not start a reel for a client whose compliance.json is unfilled.

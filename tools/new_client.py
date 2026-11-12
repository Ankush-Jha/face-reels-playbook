#!/usr/bin/env python3
"""Create a new client folder from clients/_template.

    python3 tools/new_client.py <slug> "<Display Name>"

Example:
    python3 tools/new_client.py maple-hill-mortgages "Maple Hill Mortgages"

Refuses to overwrite an existing client. Every client gets its own brand kit,
compliance rules, people rules, voice notes, assets and reels, so nothing is
shared between clients by accident.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "clients" / "_template"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    slug, name = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", slug):
        print("slug must be lowercase letters, digits and hyphens, e.g. maple-hill-mortgages")
        return 2
    dest = ROOT / "clients" / slug
    if dest.exists():
        print(f"clients/{slug} already exists; not touching it")
        return 1
    shutil.copytree(TEMPLATE, dest)
    for f in list(dest.rglob("*.json")) + list(dest.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        text = text.replace("CLIENT-SLUG", slug).replace("CLIENT DISPLAY NAME", name)
        f.write_text(text, encoding="utf-8")
    (dest / "assets" / "people").mkdir(parents=True, exist_ok=True)
    (dest / "brand" / "fonts").mkdir(parents=True, exist_ok=True)
    print(f"created clients/{slug}")
    print("next: fill client.json, brand/brand.json (+ logos, fonts), compliance.json, voice.md;")
    print("      the agent must not make a reel until compliance.json has real values.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

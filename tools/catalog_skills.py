#!/usr/bin/env python3
"""Catalog the cloned design/motion skill repos in vendor/design-skills (and the top-level vendor engines).

    python3 tools/catalog_skills.py            # writes vendor/design-skills/CATALOG.md and prints a summary

For each repo: licence (from the LICENSE file text), number of SKILL.md files, first skill description, size,
and security-scan flags (pipe-to-shell, base64 decode, credential/SSH paths, persistence, sudo). Nothing is executed.
A repo is marked ENABLE-OK only when its licence is permissive (MIT / Apache-2.0 / BSD / ISC / Unlicense / CC0) and
no scan flags were raised; noncommercial licences are marked IDEAS-ONLY; everything else needs a human look.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "vendor" / "design-skills"
PAT = re.compile(r"curl[^|\n]*\|\s*(ba)?sh|wget[^|\n]*\|\s*(ba)?sh|base64 (-d|--decode)|atob\(|os\.system|\.ssh/|id_rsa|find-generic-password|"
                 r"AWS_SECRET|\.aws/credentials|\.claude/(settings|\.credentials)|crontab|launchctl|sudo ")
CODE = {".sh", ".py", ".js", ".mjs", ".ts", ".tsx", ".json", ".md"}
SKIP = {"node_modules", ".git"}


def licence_of(repo: Path) -> str:
    for n in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING"):
        f = repo / n
        if f.exists():
            t = f.read_text(errors="ignore")[:1800].lower()
            if "polyform" in t or "noncommercial" in t or "non-commercial" in t:
                return "NONCOMMERCIAL"
            if "mit license" in t or "permission is hereby granted, free of charge" in t:
                return "MIT"
            if "apache license" in t:
                return "Apache-2.0"
            if "bsd" in t and "redistribution" in t:
                return "BSD"
            if "unlicense" in t or "public domain" in t:
                return "Unlicense"
            if "isc license" in t:
                return "ISC"
            if "gnu general public" in t:
                return "GPL"
            return "OTHER (read it)"
    return "NONE FOUND"


def description(repo: Path) -> tuple[int, str]:
    skills = [p for p in repo.rglob("SKILL.md") if not (set(p.parts) & SKIP)]
    desc = ""
    for p in sorted(skills, key=lambda p: len(p.parts))[:1]:
        m = re.search(r"^description:\s*(.+)$", p.read_text(errors="ignore")[:3000], re.M)
        if m:
            desc = m.group(1).strip().strip('"\'')[:150]
    return len(skills), desc


def flags(repo: Path) -> list[str]:
    out = set()
    for f in repo.rglob("*"):
        if f.is_file() and f.suffix in CODE and not (set(f.parts) & SKIP) and f.stat().st_size < 600_000:
            try:
                for m in PAT.finditer(f.read_text(errors="ignore")):
                    out.add(m.group(0).strip()[:30])
            except OSError:
                pass
    return sorted(out)


def main() -> int:
    rows = []
    repos = sorted(p for p in D.iterdir() if p.is_dir() and (p / ".git").exists())
    for r in repos:
        lic = licence_of(r)
        n, desc = description(r)
        fl = flags(r)
        size = subprocess.run(["du", "-sh", str(r)], capture_output=True, text=True).stdout.split()[0]
        if lic == "NONCOMMERCIAL":
            verdict = "IDEAS-ONLY"
        elif lic in ("MIT", "Apache-2.0", "BSD", "Unlicense", "ISC") and not fl:
            verdict = "ENABLE-OK" if n else "REFERENCE (no SKILL.md)"
        else:
            verdict = "REVIEW"
        rows.append((r.name.replace("__", "/", 1), lic, n, size, verdict, ", ".join(fl) or "-", desc))
    lines = ["# Design / motion skills catalog", "", f"{len(rows)} repos cloned (shallow, blobs > 1 MB skipped). Nothing here is enabled until linked into `.claude/skills/`.", "",
             "| Repo | Licence | Skills | Size | Verdict | Scan flags | What it says it does |", "|---|---|---:|---:|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
    (D / "CATALOG.md").write_text("\n".join(lines) + "\n")
    from collections import Counter
    print(Counter(r[4] for r in rows))
    for r in rows:
        if r[4] == "REVIEW":
            print("REVIEW:", r[0], "|", r[1], "|", r[5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path

from generator.paths import catalog_dir, challenges_dir
from generator.schema import load_challenge


def build_catalog() -> Path:
    """Write catalog/index.json from all challenges/*/challenge.yml (public fields only)."""
    items = []
    root = challenges_dir()
    if root.exists():
        for yml in sorted(root.glob("*/challenge.yml")):
            ch = load_challenge(yml)
            items.append(
                {
                    "id": ch.id,
                    "name": ch.name,
                    "type": ch.type,
                    "language": ch.language,
                    "os": ch.os,
                    "pe_format": ch.pe_format,
                    "bits": ch.bits,
                    "arch": ch.arch,
                    "difficulty": ch.difficulty,
                    "summary": ch.summary,
                    "tags": ch.tags,
                    "created": ch.created,
                    "download": ch.pack_name,
                }
            )

    out_dir = catalog_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "index.json"
    out.write_text(json.dumps({"challenges": items}, indent=2) + "\n", encoding="utf-8")

    # Mirror into site/ for GitHub Pages
    site_catalog = Path(__file__).resolve().parent.parent / "site" / "catalog.json"
    if site_catalog.parent.exists():
        site_catalog.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")

    return out

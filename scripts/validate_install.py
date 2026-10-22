#!/usr/bin/env python3
"""Non-mutating repository layout, data and syntax validation (offline)."""
import ast
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "launcher.py",
    "src/config.py",
    "src/core/engine.py",
    "src/server/app.py",
    "src/ai/connector.py",
    "src/ai/knowledge_base.py",
    "src/content/creation_data.py",
    "templates/index.html",
    "static/css/style.css",
    "static/js/app.js",
    "game_data/active",
    "docs/worldbuilding/WORLD_BIBLE.md",
)
OBSOLETE = ("game_engine.py", "config.py", "ai_connector.py", "RPG-main")


def validate():
    problems = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            problems.append(f"Missing required path: {rel}")
    for rel in OBSOLETE:
        if (ROOT / rel).exists():
            problems.append(f"Duplicate/accidental root file: {rel}")

    data_dir = ROOT / "game_data" / "active"
    content_files = sorted(data_dir.rglob("*.json")) if data_dir.is_dir() else []
    if not content_files:
        problems.append("Active JSON data was not found")
    names = Counter(p.name for p in content_files)
    for name, count in names.items():
        if count > 1:
            problems.append(f"Duplicate active JSON basename: {name} ({count})")
    for path in content_files:
        if path.parent == data_dir:
            problems.append(f"Uncategorized data file: {path.relative_to(ROOT)}")
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problems.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")

    for path in sorted((ROOT / "src").rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as exc:
            problems.append(f"Invalid Python {path.relative_to(ROOT)}: {exc}")

    print(f"Active JSON: {len(content_files)}; Python modules: {len(list((ROOT / 'src').rglob('*.py')))}")
    for problem in problems:
        print("FAIL:", problem)
    if not problems:
        print("Repository layout and offline validation: PASS")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(validate())

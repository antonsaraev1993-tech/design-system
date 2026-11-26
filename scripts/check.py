#!/usr/bin/env python3
"""Проверка связности знания: problems -> patterns -> components -> tokens, decisions."""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
errors, warnings = [], []

REQUIRED = ["id", "title", "status", "context", "audience", "job",
            "observation", "tags", "severity"]


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    return yaml.safe_load(text.split("---", 2)[1])


def flatten(d, prefix=""):
    out = set()
    for k, v in d.items():
        if k.startswith("$"):
            continue
        key = f"{prefix}{k}"
        if isinstance(v, dict) and "$value" in v:
            out.add(key)
        elif isinstance(v, dict):
            out |= flatten(v, key + ".")
    return out


tags = set(yaml.safe_load((ROOT / "schema/tags.yaml").read_text(encoding="utf-8")))
tokens = flatten(json.loads((ROOT / "tokens/tokens.json").read_text(encoding="utf-8")))
components = yaml.safe_load((ROOT / "components/index.yaml").read_text(encoding="utf-8"))
composition = {p.stem for p in (ROOT / "composition").glob("*.md")}

# components -> tokens
for name, c in components.items():
    for t in c.get("tokens", []):
        if t not in tokens:
            errors.append(f"component {name}: нет токена {t}")

# patterns
patterns = {}
for p in sorted((ROOT / "patterns").glob("*.md")):
    fm = frontmatter(p)
    if not fm:
        errors.append(f"{p.name}: нет YAML-шапки")
        continue
    patterns[fm["id"]] = fm
    for t in fm.get("solves", []):
        if t not in tags:
            errors.append(f"pattern {fm['id']}: тег {t} не в словаре")
    for c in fm.get("uses", []):
        if c not in components:
            errors.append(f"pattern {fm['id']}: нет компонента {c}")
    for c in fm.get("composition", []):
        if c not in composition:
            errors.append(f"pattern {fm['id']}: нет правила composition/{c}.md")

active = {k: v for k, v in patterns.items() if v.get("status") == "active"}

# problems
problems = {}
for p in sorted((ROOT / "problems").glob("*.yaml")):
    pr = yaml.safe_load(p.read_text(encoding="utf-8"))
    problems[pr.get("id")] = pr
    for f in REQUIRED:
        if f not in pr:
            errors.append(f"{p.name}: нет поля {f}")
    for t in pr.get("tags", []):
        if t not in tags:
            errors.append(f"{pr['id']}: тег {t} не в словаре")
    if pr.get("status") in ("open", "in-progress"):
        primary = pr.get("tags", [None])[0]
        match = [k for k, v in active.items() if primary in v.get("solves", [])]
        proposed = [k for k, v in patterns.items()
                    if v.get("status") == "proposed" and primary in v.get("solves", [])]
        if not match and proposed:
            warnings.append(f"{pr['id']}: только proposed паттерн ({', '.join(proposed)})")
        elif not match:
            errors.append(f"{pr['id']}: нет паттерна для основного тега {primary}")

# decisions
for d in sorted((ROOT / "decisions").glob("D-*.md")):
    fm = frontmatter(d) or {}
    for pid in fm.get("problems", []):
        if pid not in problems:
            errors.append(f"{fm.get('id')}: нет проблемы {pid}")
    for pat in fm.get("patterns", []):
        if pat not in patterns:
            errors.append(f"{fm.get('id')}: нет паттерна {pat}")
        elif patterns[pat].get("status") != "active" and fm.get("status") == "accepted":
            errors.append(f"{fm.get('id')}: принято на неактивном паттерне {pat}")

# open questions
todo = sum(f.read_text(encoding="utf-8").count("[уточнить")
           for f in ROOT.rglob("*") if f.is_file() and f.suffix in {".md", ".yaml", ".json"})

print(f"problems {len(problems)} · patterns {len(patterns)} ({len(active)} active) · "
      f"components {len(components)} · tokens {len(tokens)}")
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print(f"открытых вопросов [уточнить]: {todo}")
sys.exit(1 if errors else 0)

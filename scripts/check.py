#!/usr/bin/env python3
"""Проверка связности знания одного проекта.

problems -> patterns -> components -> tokens, patterns <-> patterns, decisions.

    python3 scripts/check.py examples/glavpodryad
    python3 scripts/check.py .            # если проект лежит в корне

Код выхода 1, если есть ошибки. Предупреждения не роняют проверку.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors, warnings = [], []

REQUIRED = ["id", "title", "status", "context", "audience", "job",
            "observation", "tags", "severity"]
RELATIONS = ("part_of", "contains", "see_also")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    return yaml.safe_load(text.split("---", 2)[1]) or {}


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


def load_yaml(rel, default):
    p = ROOT / rel
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or default) if p.exists() else default


if not (ROOT / "tags.yaml").exists():
    sys.exit(f"{ROOT}: нет tags.yaml, это не папка проекта")

tags = set(load_yaml("tags.yaml", {}))
tokens_path = ROOT / "tokens/tokens.json"
tokens = flatten(json.loads(tokens_path.read_text(encoding="utf-8"))) if tokens_path.exists() else set()
components = load_yaml("components/index.yaml", {})
composition = {p.stem for p in (ROOT / "composition").glob("*.md")}

# components -> tokens
for name, c in components.items():
    for t in (c or {}).get("tokens", []):
        if t not in tokens:
            errors.append(f"component {name}: нет токена {t}")

# patterns
patterns = {}
for p in sorted((ROOT / "patterns").glob("*.md")):
    fm = frontmatter(p)
    if fm is None:
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

# patterns <-> patterns, forces
for pid, fm in patterns.items():
    rel = fm.get("related") or {}
    for kind in RELATIONS:
        for other in rel.get(kind) or []:
            if other not in patterns:
                errors.append(f"pattern {pid}: related.{kind} ссылается на несуществующий {other}")
    for other in rel.get("contains") or []:
        back = (patterns.get(other, {}).get("related") or {}).get("part_of") or []
        if other in patterns and pid not in back:
            warnings.append(f"pattern {pid} contains {other}, но у {other} нет part_of: [{pid}]")
    for i, f in enumerate(fm.get("forces") or []):
        for key in ("pull", "against", "resolved_by"):
            if not f.get(key):
                errors.append(f"pattern {pid}: forces[{i}] без поля {key}")
    if fm.get("status") == "active":
        if not fm.get("forces"):
            warnings.append(f"pattern {pid}: active, но нет forces")
        if "related" not in fm:
            warnings.append(f"pattern {pid}: active, но нет related")

# problems
problems = {}
for p in sorted((ROOT / "problems").glob("*.yaml")):
    pr = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    problems[pr.get("id")] = pr
    for f in REQUIRED:
        if f not in pr:
            errors.append(f"{p.name}: нет поля {f}")
    for t in pr.get("tags", []):
        if t not in tags:
            errors.append(f"{pr.get('id')}: тег {t} не в словаре")
    if pr.get("status") in ("open", "in-progress"):
        primary = (pr.get("tags") or [None])[0]
        match = [k for k, v in active.items() if primary in v.get("solves", [])]
        proposed = [k for k, v in patterns.items()
                    if v.get("status") == "proposed" and primary in v.get("solves", [])]
        if not match and proposed:
            warnings.append(f"{pr['id']}: только proposed паттерн ({', '.join(proposed)})")
        elif not match:
            errors.append(f"{pr['id']}: нет паттерна для основного тега {primary}")

# decisions
covered = {}  # problem id -> теги, закрытые паттернами всех решений по ней
for d in sorted((ROOT / "decisions").glob("D-*.md")):
    fm = frontmatter(d) or {}
    did = fm.get("id", d.stem)
    solved = set()
    for pat in fm.get("patterns", []):
        if pat not in patterns:
            errors.append(f"{did}: нет паттерна {pat}")
            continue
        solved |= set(patterns[pat].get("solves", []))
        if patterns[pat].get("status") != "active" and fm.get("status") == "accepted":
            errors.append(f"{did}: принято на неактивном паттерне {pat}")
    for pid in fm.get("problems", []):
        if pid not in problems:
            errors.append(f"{did}: нет проблемы {pid}")
        covered.setdefault(pid, set()).update(solved)
    assumptions = fm.get("assumptions") or []
    for i, a in enumerate(assumptions):
        if not isinstance(a, dict) or not a.get("claim") or not a.get("if_false"):
            errors.append(f"{did}: assumptions[{i}] нужны поля claim и if_false")
    if assumptions and fm.get("status") == "accepted":
        errors.append(f"{did}: принято, но остались непроверенные assumptions")

for pid, solved in covered.items():
    missing = [t for t in problems.get(pid, {}).get("tags", []) if t not in solved]
    if missing:
        warnings.append(f"{pid}: теги {', '.join(missing)} не закрыты ни одним решением")

# open questions
todo = sum(f.read_text(encoding="utf-8").count("[уточнить")
           for f in ROOT.rglob("*") if f.is_file() and f.suffix in {".md", ".yaml", ".json"})

print(f"{ROOT.name}: problems {len(problems)} · patterns {len(patterns)} ({len(active)} active) · "
      f"components {len(components)} · tokens {len(tokens)}")
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print(f"открытых вопросов [уточнить]: {todo}")
sys.exit(1 if errors else 0)

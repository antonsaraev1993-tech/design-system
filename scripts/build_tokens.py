#!/usr/bin/env python3
"""Собирает tokens/tokens.json (DTCG) из дизайн-системы.

Источник: design/glavpodryad-redesign/design-system/tokens.json. Руками tokens/tokens.json не правят:
меняют дизайн-систему и запускают этот скрипт. scripts/check.py падает, если файл устарел.

Запуск: python3 scripts/build_tokens.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "design/glavpodryad-redesign/design-system/tokens.json"
TARGET = ROOT / "tokens/tokens.json"
EXT = "pro.glavpodryad"

# Имена, на которые уже ссылаются components/, composition/ и decisions/.
# Это ссылки на токены дизайн-системы, своих значений у них нет.
ALIASES = {
    "color.text": "color.text-primary",
    "color.surface": "color.bg-page",
    "color.surface-alt": "color.bg-surface",
    "space.stack.lg": "space.block",          # «между блоками внутри секции»
    "space.page.x": "space.page-gutter",
    "radius.card": "radius.none",             # «всё: кнопки, карточки, поля»
}

# Имена из components/, которым в дизайн-системе нет пары. Значение взято с сайта
# (site/css/tokens-ext.css, часть 2: предложения в ДС), а не из дизайн-системы.
PROPOSED = {
    "space.stack.sm": ("dimension", "18px", "--gp-space-md",
                       "Между элементами карточки. В дизайн-системе токена нет, "
                       "значение с сайта (--gp-space-md, предложение в ДС)."),
}


def token(type_, value, description=None, css=None):
    t = {"$type": type_, "$value": value}
    if description:
        t["$description"] = description
    if css:
        t["$extensions"] = {EXT: {"css": css}}
    return t


def put(tree, path, value):
    *groups, leaf = path.split(".")
    for g in groups:
        tree = tree.setdefault(g, {})
        if "$value" in tree:
            raise SystemExit(f"{path}: {g} уже токен, а не группа")
    if leaf in tree:
        raise SystemExit(f"{path}: имя занято")
    tree[leaf] = value


def strip(name, prefix):
    assert name.startswith(prefix), name
    return name[len(prefix):]


def build():
    ds = json.loads(SOURCE.read_text(encoding="utf-8"))
    out = {
        "$description": f"Сгенерировано scripts/build_tokens.py из {SOURCE.relative_to(ROOT)} "
                        f"({ds['name']}, v{ds['version']}). Руками не править.",
    }

    for t in ds["color"]["tokens"]:
        put(out, "color." + strip(t["name"], "color-"),
            token("color", t["value"], t.get("usage"), "--" + t["name"]))

    for fam, value in ds["type"]["families"].items():
        put(out, f"font.family.{fam}", token("fontFamily", value, css=f"--font-{fam}"))
    weights = {"regular": 400, "medium": 500, "semibold": 600, "bold": 700}
    for name, w in weights.items():
        put(out, f"font.weight.{name}", token("fontWeight", w, css=f"--font-weight-{name}"))
    for group in ds["type"]["groups"]:
        for s in group["styles"]:
            n = s["name"]
            put(out, f"font.size.{n}", token("dimension", s["fontSize"], s.get("usage"), f"--type-{n}-size"))
            put(out, f"font.line-height.{n}", token("number", s["lineHeight"]))
            put(out, f"font.weight-of.{n}", token("fontWeight", s["fontWeight"]))
            if "letterSpacing" in s:
                put(out, f"font.tracking.{n}", token("dimension", s["letterSpacing"], css=f"--type-{n}-tracking"))

    for t in ds["spacing"]["tokens"]:
        put(out, "space." + strip(t["name"], "space-"), token("dimension", t["value"], t.get("usage"), "--" + t["name"]))
    for t in ds["radius"]["tokens"]:
        put(out, "radius." + strip(t["name"], "radius-"), token("dimension", t["value"], t.get("usage"), "--" + t["name"]))
    for t in ds["borderWidth"]["tokens"]:
        put(out, "border.width." + strip(t["name"], "border-"), token("dimension", t["value"], t.get("usage"), "--" + t["name"]))
    for t in ds["size"]["tokens"]:
        key = strip(t["name"], "size-")
        if key == "container":
            key = "container.max"  # имя из composition/grid.md
        put(out, "size." + key, token("dimension", t["value"], t.get("usage"), "--" + t["name"]))

    for alias, target in ALIASES.items():
        ref = out
        for part in target.split("."):
            ref = ref[part]
        put(out, alias, {"$type": ref["$type"], "$value": "{" + target + "}",
                         "$description": f"Старое имя, ссылка на {target}."})
    for path, (type_, value, css, desc) in PROPOSED.items():
        t = token(type_, value, desc, css)
        t["$extensions"][EXT]["status"] = "proposed"
        put(out, path, t)
    return out


def render():
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    TARGET.write_text(render(), encoding="utf-8")
    print(f"записано {TARGET.relative_to(ROOT)}")

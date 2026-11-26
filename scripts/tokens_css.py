#!/usr/bin/env python3
"""tokens/tokens.json (DTCG) -> prototype/tokens.css: каждый токен становится CSS-переменной.

color.text-muted -> --color-text-muted, space.page.x -> --space-page-x.
Прототип не задаёт значений сам, только ссылается на эти переменные.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def walk(node, path):
    for key, value in node.items():
        if key.startswith("$"):
            continue
        if isinstance(value, dict) and "$value" in value:
            yield "-".join(path + [key]), value["$value"]
        elif isinstance(value, dict):
            yield from walk(value, path + [key])


tokens = json.loads((ROOT / "tokens/tokens.json").read_text(encoding="utf-8"))
lines = ["/* Сгенерировано scripts/tokens_css.py из tokens/tokens.json. Не править вручную. */", ":root {"]
lines += [f"  --{name}: {value};" for name, value in walk(tokens, [])]
lines.append("}")

out = ROOT / "prototype/tokens.css"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"{out.relative_to(ROOT)}: {len(lines) - 3} токенов")

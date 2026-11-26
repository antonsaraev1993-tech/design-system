#!/usr/bin/env python3
"""Проверка site/: токены, захардкоженные значения, доступность, состав главной по HANDOFF.md.

Запуск: python3 scripts/check_site.py   (код выхода 1, если есть ошибки)
"""
import filecmp
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REF = ROOT / "design/glavpodryad-redesign/design-system/tokens.css"
TOKEN_FILES = {SITE / "css/tokens.css", SITE / "css/tokens-ext.css"}
errors, warnings = [], []

# ---------- 1. tokens.css совпадает с эталоном ----------
if not filecmp.cmp(SITE / "css/tokens.css", REF, shallow=False):
    errors.append("site/css/tokens.css отличается от design-system/tokens.css эталона")

# ---------- 2. нет захардкоженных цветов и размеров вне файлов токенов ----------
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla)\(")
LENGTH = re.compile(r"(?<![\w-])\d*\.?\d+(?:px|rem|em|vw|vh|pt)\b")
defined = set()
for f in TOKEN_FILES:
    defined |= set(re.findall(r"(--[\w-]+)\s*:", f.read_text(encoding="utf-8")))

used = set()
for css in sorted((SITE / "css").rglob("*.css")):
    text = re.sub(r"/\*.*?\*/", "", css.read_text(encoding="utf-8"), flags=re.S)
    used |= set(re.findall(r"var\((--[\w-]+)", text))
    if css in TOKEN_FILES:
        continue
    rel = css.relative_to(ROOT)
    for n, line in enumerate(text.splitlines(), 1):
        for m in COLOR.findall(line):
            errors.append(f"{rel}:{n}: цвет без токена «{m}»")
        for m in LENGTH.findall(line):
            if float(re.match(r"\d*\.?\d+", m).group()) == 0:
                continue  # 0px (например, запасное значение env()) не размер
            errors.append(f"{rel}:{n}: размер без токена «{m}»")

html = (SITE / "index.html").read_text(encoding="utf-8")
used |= set(re.findall(r"var\((--[\w-]+)", html))
for v in sorted(used - defined):
    errors.append(f"var({v}) не определён ни в tokens.css, ни в tokens-ext.css")
if re.search(r"\sstyle=", html):
    errors.append("index.html: inline style=, стили должны быть в CSS")


# ---------- 3. разбор страницы ----------
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.elements, self.texts = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        el = {"tag": tag, "attrs": a, "classes": set((a.get("class") or "").split()),
              "ancestors": [p["classes"] for p in self.stack], "anc_tags": [p["tag"] for p in self.stack], "text": ""}
        self.elements.append(el)
        if tag not in VOID:
            self.stack.append(el)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1]["tag"] in ("script", "style"):
            return
        for el in self.stack:
            el["text"] += data
        if data.strip():
            self.texts.append(data.strip())


page = Page()
page.feed(html)
els = page.elements


def has(el, cls):
    return cls in el["classes"]


def inside(el, cls):
    return any(cls in c for c in el["ancestors"])


def count(cls, within=None):
    return sum(1 for e in els if has(e, cls) and (within is None or inside(e, within)))


def text(el):
    return re.sub(r"\s+", " ", el["text"]).strip()


# плейсхолдеры в квадратных скобках не должны попасть на страницу
for t in page.texts:
    if re.search(r"\[[^\]]+\]", t):
        errors.append(f"index.html: плейсхолдер в скобках на странице: «{t[:60]}»")

# доступность
ids = {e["attrs"].get("id") for e in els}
labelled = {e["attrs"].get("for") for e in els if e["tag"] == "label"}
for e in els:
    a = e["attrs"]
    if e["tag"] in ("input", "select", "textarea") and a.get("type") != "hidden":
        if a.get("id") not in labelled and "label" not in e["anc_tags"] and not a.get("aria-label"):
            errors.append(f"поле без подписи: {e['tag']}#{a.get('id')}")
    if e["tag"] == "button" and not text(e) and not a.get("aria-label"):
        errors.append("кнопка без текста и без aria-label")
    if e["tag"] == "img" and "alt" not in a:
        errors.append(f"img без alt: {a.get('src')}")
    if e["tag"] == "a" and not a.get("href"):
        errors.append(f"ссылка без href: «{text(e)}»")
    if e["tag"] == "a" and a.get("href", "").startswith("#") and len(a["href"]) > 1 and a["href"][1:] not in ids:
        errors.append(f"якорь ведёт в никуда: {a['href']}")
    for ref in ("aria-controls", "aria-describedby", "aria-labelledby"):
        if a.get(ref) and a[ref] not in ids:
            errors.append(f"{ref}=\"{a[ref]}\" ссылается на несуществующий id")

# ---------- 4. состав главной: таблица «Состав главной» из HANDOFF.md ----------
submenu = [text(e) for e in els if has(e, "gp-submenu__link")]
chips = [text(e) for e in els if has(e, "gp-service-chip")]
cta = sum(1 for e in els if e["tag"] in ("a", "button") and text(e) == "Оставить заявку")
submit = sum(1 for e in els if e["tag"] == "button" and e["attrs"].get("type") == "submit" and text(e) == "Отправить")
stats_labels = [f"{a} {b}" for a, b in zip([text(e) for e in els if has(e, "gp-stat__value") and inside(e, "gp-about")],
                                            [text(e) for e in els if has(e, "gp-stat__label") and inside(e, "gp-about")])]

rows = [
    ("Меню шапки", "6", count("gp-header__link")),
    ("Подменю «Услуги»", "13", len(submenu)),
    ("Цифры в hero", "0", count("gp-stat", within="gp-hero")),
    ("Объекты", "6", count("gp-project")),
    ("Цифры «О компании»", "4", count("gp-stat", within="gp-about")),
    ("Преимущества", "7", count("gp-advantage")),
    ("Карточки услуг", "3", count("gp-service")),
    ("Чипы услуг", "11", len(chips)),
    ("Возможности кабинета", "5", count("gp-check")),
    ("Партнёры", "5", count("gp-partner")),
    ("Способы связи", "4", count("gp-contact-chip")),
    ("Статьи блога на главной", "0", count("gp-blog-card")),
    ("Меню подвала", "5", count("gp-footer__link")),
    ("Соцсети в подвале", "2", count("gp-footer__social-link")),
    ("Юр. ссылки в подвале", "5", count("gp-footer__legal-link")),
    ("Кнопки «Оставить заявку»", "3", cta),
    ("Кнопка «Отправить» в форме", "1", submit),
]

expected_stats = ["100+ построенных домов", "6+ лет опыта", "6+ постоянных бригад", "90+ счастливых клиентов"]
if stats_labels != expected_stats:
    errors.append(f"цифры «О компании» не совпадают с HANDOFF: {stats_labels}")
if chips != submenu[2:]:
    errors.append("чипы услуг не совпадают с подменю (пункты 3–13) по составу или порядку")

print(f"{'Блок':32} {'HANDOFF':>8} {'на странице':>12}")
for name, exp, got in rows:
    ok = str(got) == exp
    if not ok:
        errors.append(f"{name}: ожидается {exp}, на странице {got}")
    print(f"{name:32} {exp:>8} {got:>12}  {'ok' if ok else 'ОШИБКА'}")

print()
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print("ошибок:", len(errors))
sys.exit(1 if errors else 0)

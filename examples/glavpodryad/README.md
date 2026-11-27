# Пример: Главподряд

Концепт редизайна главной glavpodryad.pro. Принцип проекта: редизайн без изменения сущности. Показывается с согласия компании.

| Что | Где |
|---|---|
| Знание о редизайне | `invariants/`, `problems/`, `patterns/`, `composition/`, `components/`, `tokens/`, `tags.yaml` |
| Решения | `decisions/D-001` (пример формата, человек), `decisions/D-004` (холодный запуск агента, см. `docs/cold-run-01.md` в корне), `decisions/D-005` (ориентир цены, по нему сделаны цены в `site/`) |
| Макеты компонентов и брендбук | `design/glavpodryad-redesign/` (начать с `HANDOFF.md`) |
| Статическая главная по эталону | `site/index.html`, что заменить до запуска: `site/TODO.md` |

Проблемы P-001…P-005 выписаны по живому сайту в ноябре 2026, без аналитики: поле `evidence` экспертное, метрики [уточнить у клиента].

`tokens/tokens.json` собирается из `design/glavpodryad-redesign/design-system/tokens.json` скриптом `build_tokens.py`. Руками его не правят. `scripts/check.py` вызывает этот скрипт сам и падает, если файл отстал от дизайн-системы, а расхождения со стилями сайта (`site/css/`) выводит предупреждениями.

```
python3 examples/glavpodryad/build_tokens.py       # после правки дизайн-системы
python3 scripts/check.py examples/glavpodryad      # из корня репозитория
python3 examples/glavpodryad/check_site.py
```

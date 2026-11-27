# Пример: Главподряд

Концепт редизайна главной glavpodryad.pro. Принцип проекта: редизайн без изменения сущности. Показывается с согласия компании.

| Что | Где |
|---|---|
| Знание о редизайне | `invariants/`, `problems/`, `patterns/`, `composition/`, `components/`, `tokens/`, `tags.yaml` |
| Решения | `decisions/D-001` (пример формата, человек), `decisions/D-002` (холодный запуск агента, см. `docs/cold-run-01.md` в корне) |
| Макеты компонентов и брендбук | `design/glavpodryad-redesign/` (начать с `HANDOFF.md`) |
| Статическая главная по эталону | `site/index.html`, что заменить до запуска: `site/TODO.md` |

Проблемы P-001…P-005 выписаны по живому сайту в ноябре 2026, без аналитики: поле `evidence` экспертное, метрики [уточнить у клиента]. Значения токенов в `tokens/` пока заглушки, эталон стилей лежит в `design/`.

```
python3 scripts/check.py examples/glavpodryad      # из корня репозитория
python3 examples/glavpodryad/check_site.py
```

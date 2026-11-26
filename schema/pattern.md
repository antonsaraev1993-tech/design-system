# Формат паттерна

Файл `patterns/<id>.md`. В начале YAML-шапка, ниже свободный текст для людей.

```yaml
---
id: kebab-case-id
status: active | proposed | deprecated
solves: [теги из schema/tags.yaml]
when:        # условия, при которых паттерн подходит
  - ...
avoid_when:  # когда не применять, даже если теги совпали
  - ...
uses: [компоненты из components/index.yaml]
composition: [файлы из composition/]
---
```

Тело: суть паттерна, структура блока, правила контента, анти-паттерны, пример.

# Button

Кнопка и ссылка-действие: один главный призыв «Оставить заявку» и вторичные действия.

**Варианты (`variant`):**
- `primary` — `color-accent`, текст `color-accent-on`, hover `color-accent-hover`. Одна на экран.
- `outline` — рамка `color-border-strong` (на тёмном `color-border-inverse`), для второго действия рядом с primary.
- `link` — текст + стрелка, для «Все объекты →», «Подробнее →».

**Размеры (`size`):** `md` = `size-control-md` (52), `sm` = `size-control-sm` (44, в шапке), отправка формы `size-control-lg` (56) на всю ширину.

**Свойства:** `label`, `href`, `inverse` (на тёмном фоне), `arrow`, `block`, `submit`.

**Play** — отдельный круглый вариант (`radius-full`, `size-play`) только для видео, с `aria-label`.

Нельзя: белый текст на оранжевом, две primary рядом, скругления.

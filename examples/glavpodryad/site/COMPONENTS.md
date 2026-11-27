# Компоненты: из `.dc.html` в статику

Источник: `design/glavpodryad-redesign/components/`. Каждый компонент — один CSS-файл в `css/components/` и шаблон разметки ниже. Свойства-переключатели стали классами-модификаторами, текстовые свойства стали текстом в разметке. Повторы (`sc-for`) расписаны в `index.html` вручную, их количество проверяет `scripts/check_site.py`.

Подключение: `tokens.css` → `tokens-ext.css` → `base.css` → `components/*.css` → `page.css`.

| Компонент | Файл | Свойства из `.md` | Как задаются |
|---|---|---|---|
| Logo | `logo.css` | `inverse`, `href` | `gp-logo` + `gp-logo--inverse`, `href` у `<a>` |
| Button | `button.css` | `variant`, `size`, `inverse`, `arrow`, `block`, `submit`, `label`, `href` | `gp-btn--primary / --outline / --link`, `--sm`, `--inverse`, `--block`; `arrow` = `<svg class="gp-btn__icon">` внутри; `submit` = `<button type="submit" class="gp-btn … gp-btn--lg">` |
| Play | `page.css` (`.gp-play`) | круглый вариант кнопки, только для видео | `<button class="gp-play" aria-label="…">` |
| Badge | `badge.css` | `label` | `<span class="gp-badge">` |
| Chip | `chip.css` | `label`, `href` | `<a class="gp-chip">` в `<ul class="gp-chips">` |
| CheckItem | `check-item.css` | `label` | `<li class="gp-check">` в `<ul class="gp-checklist">` |
| Stat | `stat.css` | `value`, `label`, `tone` | `gp-stat` (+ `gp-stat--dark`), `__value`, `__label`; ряд `<ul class="gp-stats">` |
| Field | `field.css` | `label`, `placeholder`, `type`, `kind`, `options` | `<label class="gp-field">` + `<input>` или `<select>` с классом `gp-field__control`; ошибка `gp-field__error` |
| Placeholder | `placeholder.css` | `label`, `height`, `tone` | `gp-placeholder` + `--photo / --cover / --thumb / --logo` (высота) и `--dark / --outline` (тон); `data-todo` = номер в TODO.md |
| SectionHeader | `section-header.css` | `overline`, `heading`, `linkLabel` + `linkHref`, `inverse` | `gp-section-header` (+ `--inverse`, `--spaced`), ссылка — `gp-btn--link` |
| ProjectCard | `project-card.css` | `heading`, `status`, `area`, `floors`, `floorsLabel`, `href` | `<a class="gp-project">`: Placeholder + Badge, `__title`, `__meta`; сетка `gp-projects` |
| ServiceCard | `service-card.css` | `n`, `heading`, `text`, `cta`, `href`, `inverse` | `<a class="gp-service">` (+ `--inverse`), сетка `gp-services` |
| AdvantageCell | `advantage-cell.css` | `n`, `heading`, `text` | `<li class="gp-advantage">` в `<ul class="gp-advantages">` |
| BlogCard | `blog-card.css` | `heading`, `date`, `href` | `<a class="gp-blog-card">`; на главной не используется, как в эталоне |
| Header | `header.css` | меню 6, подменю «Услуги» 13, телефон, Button sm | `gp-header`; подменю `#submenu-services`, кнопка `gp-header__toggle` (`js/menu.js`) |
| Footer | `footer.css` | меню 5, соцсети 2, юр. ссылки 5 | `gp-footer` |

## Шаблоны

```html
<!-- Button: primary, outline + inverse + arrow, link, submit -->
<a class="gp-btn gp-btn--primary" href="#form">Оставить заявку</a>
<a class="gp-btn gp-btn--outline gp-btn--inverse" href="#projects">Смотреть объекты
  <svg class="gp-btn__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
<a class="gp-btn gp-btn--link" href="…">Все объекты <svg class="gp-btn__icon" …/></a>
<button class="gp-btn gp-btn--primary gp-btn--lg gp-btn--block" type="submit">Отправить</button>

<!-- SectionHeader со ссылкой -->
<div class="gp-section-header gp-section-header--spaced">
  <div class="gp-section-header__text">
    <p class="gp-overline">Наши объекты</p>
    <h2 class="gp-section-header__title">Спроектируем и построим дом вашей мечты</h2>
  </div>
  <a class="gp-btn gp-btn--link" href="…">Все объекты <svg class="gp-btn__icon" …/></a>
</div>

<!-- ProjectCard -->
<a class="gp-project" href="…">
  <div class="gp-project__media">
    <div class="gp-placeholder gp-placeholder--photo" data-todo="TODO-03" aria-hidden="true"></div>
    <span class="gp-badge gp-project__badge">Построен в 2022</span>
  </div>
  <div class="gp-project__body">
    <h3 class="gp-project__title">Дом на склоне</h3>
    <div class="gp-project__meta"><span><b>220</b> м²</span><span><b>3</b> этажа</span><span class="gp-project__more">Подробнее →</span></div>
  </div>
</a>

<!-- Field: input и select -->
<label class="gp-field" for="f-name">Имя
  <input class="gp-field__control" id="f-name" name="Name" type="text" placeholder="Как к вам обращаться" required>
</label>
<label class="gp-field" for="f-plan">Что планируете
  <select class="gp-field__control" id="f-plan" name="formservices[]"><option>Строительство дома</option></select>
</label>
```

## Где отступили от эталона

- **Тексты-плейсхолдеры** `[в скобках]` заменены нейтральными заглушками (TODO.md, шаг 4 задания).
- **Подменю «Услуги».** В `Header.dc.html` его нет, хотя HANDOFF требует 13 пунктов. Сделано панелью под шапкой: так она не выходит за край экрана на 390 px.
- **Адаптив трёх значений.** Высота видео и поля панели контактов и формы на узких экранах меньше, на 1440 px совпадают с эталоном. В эталоне на 390 px слово «строительство» выходит за панель.
- **Перенос по слогам** у заголовка первого экрана и заголовков карточек услуг. В эталоне длинные слова («Индивидуальное», «комфортной») на узких колонках выходят за край.
- **Линия над цифрами** 1 px, как в `Main.dc.html`. В `Stat.md` написано `border-focus` (2 px).
- **Ссылки** ведут на настоящие страницы glavpodryad.pro, там где в эталоне стоят якоря-заглушки (`#docs`, `#services` у чипов).
- **Состояния.** Добавлены hover и видимый фокус по README («фокус `border-focus`»); в шаблонах их нет.

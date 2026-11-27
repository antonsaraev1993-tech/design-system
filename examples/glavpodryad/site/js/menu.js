/* Подменю «Услуги». Без JS кнопка скрыта, «Услуги» ведёт к секции услуг на странице.
   С JS ссылка скрыта, вместо неё кнопка «Услуги ⌄» целиком. */
(function () {
  var toggle = document.querySelector(".gp-header__toggle");
  if (!toggle) return;
  var menu = document.getElementById(toggle.getAttribute("aria-controls"));
  if (!menu) return;
  toggle.hidden = false;
  // С JS «Услуги» и стрелка одна кнопка, ссылка-запасной вариант не нужна
  var link = document.querySelector(".gp-header__link--services");
  if (link) link.hidden = true;

  function setOpen(open) {
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    menu.hidden = !open;
  }
  // Превью услуги справа в подменю (видно только на десктопе, см. header.css)
  var art = menu.querySelector(".gp-submenu__art");
  var caption = menu.querySelector(".gp-submenu__caption");
  var links = menu.querySelectorAll("[data-preview]");
  function preview(link) {
    if (!art || !caption) return;
    art.setAttribute("data-art", link.getAttribute("data-preview"));
    caption.textContent = link.textContent;
    links.forEach(function (l) { l.removeAttribute("data-active"); });
    link.setAttribute("data-active", "");
  }
  links.forEach(function (link) {
    link.addEventListener("mouseenter", function () { preview(link); });
    link.addEventListener("focus", function () { preview(link); });
  });
  if (links.length) preview(links[0]);

  toggle.addEventListener("click", function () {
    setOpen(toggle.getAttribute("aria-expanded") !== "true");
  });
  document.addEventListener("keydown", function (e) {
    // stopImmediatePropagation: этот Escape закрывает только подменю, панель «Меню» остаётся открытой
    if (e.key === "Escape" && !menu.hidden) { setOpen(false); toggle.focus(); e.stopImmediatePropagation(); }
  });
  document.addEventListener("click", function (e) {
    if (!menu.hidden && !menu.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
  });
})();

/* Кнопка «Меню» на узких экранах (≤ 1023 px, --gp-bp-nav в tokens-ext.css).
   Без JS кнопки нет, шапка остаётся развёрнутой. */
(function () {
  var header = document.querySelector(".gp-header");
  var burger = document.querySelector(".gp-header__burger");
  var panel = burger && document.getElementById(burger.getAttribute("aria-controls"));
  if (!header || !panel) return;
  // Тот же брейкпоинт, что в @media header.css: берём из токена, запасное значение на случай старого CSS
  var bp = getComputedStyle(document.documentElement).getPropertyValue("--gp-bp-nav").trim() || "1023px";
  var narrow = window.matchMedia("(max-width: " + bp + ")");
  header.classList.add("gp-header--collapsible");
  burger.hidden = false;

  function setOpen(open) {
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    burger.setAttribute("aria-label", open ? "Закрыть меню" : "Меню");
    header.classList.toggle("gp-header--open", open);
  }
  function isOpen() { return burger.getAttribute("aria-expanded") === "true"; }

  burger.addEventListener("click", function () { setOpen(!isOpen()); });
  // Переход по пункту меню (якорь на этой странице) закрывает панель
  panel.addEventListener("click", function (e) {
    if (narrow.matches && e.target.closest("a")) setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    // Открытое подменю «Услуги» перехватывает Escape раньше (см. выше), сюда доходит второй Escape
    if (e.key === "Escape" && isOpen()) { setOpen(false); burger.focus(); }
  });
  // Экран стал широким (поворот планшета): панель не нужна
  narrow.addEventListener("change", function () { if (!narrow.matches) setOpen(false); });
})();

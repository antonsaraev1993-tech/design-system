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
    if (e.key === "Escape" && !menu.hidden) { setOpen(false); toggle.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (!menu.hidden && !menu.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
  });
})();

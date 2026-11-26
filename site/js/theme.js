/* Переключатель светлой и тёмной темы (точка в шапке). Выбор запоминается в localStorage.
   Цвета тёмной темы: tokens-ext.css, :root[data-theme="dark"]. */
(function () {
  var btn = document.querySelector(".gp-theme");
  if (!btn) return;
  var root = document.documentElement;

  function apply(dark) {
    if (dark) root.setAttribute("data-theme", "dark"); else root.removeAttribute("data-theme");
    btn.setAttribute("aria-pressed", dark ? "true" : "false");
  }
  apply(root.getAttribute("data-theme") === "dark");
  btn.hidden = false;

  btn.addEventListener("click", function () {
    var dark = root.getAttribute("data-theme") !== "dark";
    apply(dark);
    try { localStorage.setItem("gp-theme", dark ? "dark" : "light"); } catch (e) {}
  });
})();

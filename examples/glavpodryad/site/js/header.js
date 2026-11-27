/* Шапка: прячется при прокрутке вниз, появляется при прокрутке вверх.
   Не прячется, пока открыто подменю, фокус с клавиатуры внутри шапки или страница у самого верха. */
(function () {
  var header = document.querySelector(".gp-header");
  if (!header) return;
  var HIDDEN = "gp-header--hidden";
  var THRESHOLD = 6; // пикселей прокрутки, чтобы не дёргалась от мелких движений
  var last = window.scrollY;

  function update() {
    var y = window.scrollY;
    var menuOpen = header.querySelector('[aria-expanded="true"]');
    var focused = header.querySelector(":focus-visible"); // фокус с клавиатуры, не от клика мышью
    if (y <= header.offsetHeight || menuOpen || focused) {
      header.classList.remove(HIDDEN);
    } else if (y > last + THRESHOLD) {
      header.classList.add(HIDDEN);
    } else if (y < last - THRESHOLD) {
      header.classList.remove(HIDDEN);
    } else {
      return; // мелкое движение: last не трогаем, копим сдвиг
    }
    last = y;
  }

  // scroll и так приходит не чаще раза за кадр, работа в update дешёвая
  window.addEventListener("scroll", update, { passive: true });
  // Tab в шапку с клавиатуры: показать её
  header.addEventListener("focusin", function (e) {
    if (e.target.matches(":focus-visible")) header.classList.remove(HIDDEN);
  });
})();

/*
  Форма заявки, демо-режим (TODO-12 в TODO.md).
  Данные никуда не отправляются: на живом сайте форма работает через сервис форм Tilda
  (блок T702, поля Name, Phone, formservices[], после отправки переход на /spasibo),
  а доступа к проекту Tilda нет. Чтобы подключить настоящую отправку, замените функцию send().
*/
(function () {
  var form = document.getElementById("lead-form");
  if (!form) return;
  var status = document.getElementById("form-status");

  function digits(v) { return (v || "").replace(/\D/g, ""); }

  function check(input, ok) {
    var err = document.getElementById(input.id + "-err");
    input.setAttribute("aria-invalid", ok ? "false" : "true");
    if (err) err.hidden = ok;
    return ok;
  }

  function send(data) {
    // Демо: ничего не отправляем. Здесь будет fetch() на обработчик заявок.
    return Promise.resolve({ demo: true, data: data });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = form.elements.Name;
    var phone = form.elements.Phone;
    var d = digits(phone.value);
    var okName = check(name, name.value.trim().length > 0);
    var okPhone = check(phone, d.length === 11 || d.length === 10);
    if (!okName) { name.focus(); return; }
    if (!okPhone) { phone.focus(); return; }

    send(new FormData(form)).then(function () {
      status.textContent = "Это концепт сайта, заявка не отправлена. Чтобы связаться с компанией, позвоните: +7 (863) 209-84-64.";
      status.hidden = false;
    });
  });
})();

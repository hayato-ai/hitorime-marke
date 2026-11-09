/* 自前のフォーム：必須項目をその場で検証し、Google Apps Script（gas/Code.gs）に送る。
   受け取った側で、スプレッドシートへの記録・運営者への通知・送った人への自動返信を行う。
   ★ 設定（手順は docs/google-setup.md）。FORM_ENDPOINT が空のあいだは送信せず、フォームの下に「（設定前のため送信されません）」と出す。
   - FORM_ENDPOINT: Apps Script をウェブアプリとして公開したURL（https://script.google.com/macros/s/…/exec）
   - BOOKING_URL  : Google カレンダーの予約ページのURL。入れると、無料相談の送信後にカレンダーを表示する
   送る項目名：company ／ firstname（お名前）／ email ／ phone ／ consult_type ／ message。website はロボット対策の見えない欄 */
var FORM_ENDPOINT = "https://script.google.com/macros/s/AKfycbwKfyZAlqzSPJmKAyAsOKn1D-O1t6Bo4EKeTlo1o-Cm35THFQFgKnID31I_rgHh70uw/exec";
var BOOKING_URL = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ3fTX0eyWLPKCyGExebtZHKF4ATJo4ZCMW0hpOQuylXs_0TsDl6oxTcfatKuLPgUZ8sSLLceRU1?gv=true";

(function () {
  "use strict";

  var MSG_REQUIRED = "入力してください";
  var MSG_EMAIL = "メールアドレスの形式で入力してください";
  var MSG_CHECK = "同意にチェックを入れてください";
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function control(field) {
    return field.querySelector("input, select, textarea");
  }

  function setError(field, message) {
    var c = control(field);
    var err = field.querySelector(".field__err");
    if (!c || !err) return;
    if (message) {
      err.textContent = message;
      err.hidden = false;
      field.classList.add("is-invalid");
      c.setAttribute("aria-invalid", "true");
    } else {
      err.hidden = true;
      field.classList.remove("is-invalid");
      c.removeAttribute("aria-invalid");
    }
  }

  // 検証：必須の未入力、メールの形式、同意のチェック。エラー文を返す（問題なければ空文字）
  function check(field) {
    var c = control(field);
    if (!c) return "";
    var required = c.required;
    if (c.type === "checkbox") return required && !c.checked ? MSG_CHECK : "";
    var v = (c.value || "").trim();
    if (required && !v) return MSG_REQUIRED;
    if (c.type === "email" && v && !EMAIL_RE.test(v)) return MSG_EMAIL;
    return "";
  }

  function validate(form) {
    var first = null;
    var fields = form.querySelectorAll(".field");
    for (var i = 0; i < fields.length; i++) {
      var msg = check(fields[i]);
      setError(fields[i], msg);
      if (msg && !first) first = control(fields[i]);
    }
    return first;
  }

  function buildPayload(form, kind) {
    var data = { form: kind, page: location.href.split("#")[0] };
    var inputs = form.querySelectorAll("input, select, textarea");
    for (var i = 0; i < inputs.length; i++) {
      var c = inputs[i];
      if (c.type === "checkbox" || !c.name) continue;
      data[c.name] = (c.value || "").trim();
    }
    return data;
  }

  function show(el, on) {
    if (el) el.hidden = !on;
  }

  function init(form) {
    var kind = form.getAttribute("data-form");
    var note = form.querySelector(".lead-form__note");
    var fail = form.querySelector(".lead-form__fail");
    var done = form.parentNode.querySelector(".lead-form__done");
    var btn = form.querySelector('button[type="submit"]');
    var label = btn ? btn.querySelector("span") : null;
    var busy = false;

    // 入力しなおした項目は、その場でエラーを消す／出しなおす
    form.addEventListener("input", function (e) {
      var f = e.target.closest && e.target.closest(".field");
      if (f && f.classList.contains("is-invalid")) setError(f, check(f));
    });
    form.addEventListener("change", function (e) {
      var f = e.target.closest && e.target.closest(".field");
      if (f && f.classList.contains("is-invalid")) setError(f, check(f));
    });
    // 入力のあとで項目を離れたとき：メールの形式だけ確かめる（空の必須項目は、送信ボタンを押す前に出すとボタンが動いてクリックを外すので、送信時に出す）
    form.addEventListener("focusout", function (e) {
      var f = e.target.closest && e.target.closest(".field");
      var c = f && control(f);
      if (c && c.type === "email" && (c.value || "").trim()) setError(f, check(f));
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (busy) return;
      show(note, false);
      show(fail, false);
      var first = validate(form);
      if (first) {
        first.focus();
        return;
      }
      var endpoint = (window.FORM_ENDPOINT || "").trim();
      if (!endpoint) {
        // 設定前：送信しない
        show(note, true);
        return;
      }
      busy = true;
      if (btn) btn.disabled = true;
      var original = label ? label.textContent : "";
      if (label) label.textContent = "送信しています…";
      // Content-Type を付けない（text/plain の単純なリクエストにして、Apps Script で事前確認の通信が要らないようにする）
      fetch(endpoint, {
        method: "POST",
        body: JSON.stringify(buildPayload(form, kind))
      }).then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      }).then(function (r) {
        if (!r || !r.ok) throw new Error("NG");
        form.hidden = true;
        if (done) {
          var meetUrl = (window.BOOKING_URL || "").trim();
          var meet = done.querySelector(".lead-form__meet");
          if (meet && meetUrl) {
            var ifr = document.createElement("iframe");
            ifr.src = meetUrl + (/[?&]gv=true/.test(meetUrl) ? "" : (meetUrl.indexOf("?") < 0 ? "?" : "&") + "gv=true");
            ifr.title = "日程調整のカレンダー";
            ifr.className = "lead-form__meet-frame";
            ifr.loading = "lazy";
            meet.appendChild(ifr);
            meet.hidden = false;
            var ml = done.querySelector(".lead-form__meet-lead"); if (ml) ml.hidden = false;
            var fb = done.querySelector(".lead-form__meet-fallback"); if (fb) fb.hidden = true;
          }
          done.hidden = false;
          done.focus();
        }
      }).catch(function () {
        show(fail, true);
        busy = false;
        if (btn) btn.disabled = false;
        if (label) label.textContent = original;
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var forms = document.querySelectorAll("form.lead-form");
    for (var i = 0; i < forms.length; i++) init(forms[i]);
  });
})();

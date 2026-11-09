/* 自前のフォーム（v14）：必須項目をその場で検証し、HubSpot Forms API に JSON で POST する。
   ★ HubSpot の設定（公開前に本人が入れる）。下の3つが空のあいだは送信せず、フォームの下に「（設定前のため送信されません）」と出す。
   - HUBSPOT_PORTAL_ID    : HubSpot のポータルID（アカウントID）
   - HUBSPOT_FORM_DOWNLOAD: 資料請求フォームの GUID
   - HUBSPOT_FORM_CONSULT : 無料相談フォームの GUID
   HubSpot 側のフィールド名：company ／ firstname（お名前をそのまま入れる）／ email ／ phone ／ message ／ consult_type */
var HUBSPOT_PORTAL_ID = "";
var HUBSPOT_FORM_DOWNLOAD = "";
var HUBSPOT_FORM_CONSULT = "";

(function () {
  "use strict";

  var MSG_REQUIRED = "入力してください";
  var MSG_EMAIL = "メールアドレスの形式で入力してください";
  var MSG_CHECK = "同意にチェックを入れてください";
  var CONSENT_TEXT = "プライバシーポリシーに同意する";
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function formGuid(kind) {
    return kind === "consult" ? HUBSPOT_FORM_CONSULT : HUBSPOT_FORM_DOWNLOAD;
  }

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

  function buildPayload(form) {
    var data = {};
    var inputs = form.querySelectorAll("input, select, textarea");
    for (var i = 0; i < inputs.length; i++) {
      var c = inputs[i];
      if (c.type === "checkbox") continue;
      data[c.name] = (c.value || "").trim();
    }
    var fields = [];
    ["company", "firstname", "email", "phone", "consult_type", "message"].forEach(function (n) {
      if (data[n]) fields.push({ name: n, value: data[n] });
    });
    return {
      fields: fields,
      context: { pageUri: location.href.split("#")[0], pageName: document.title },
      legalConsentOptions: { consent: { consentToProcess: true, text: CONSENT_TEXT } }
    };
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
      var portal = (window.HUBSPOT_PORTAL_ID || "").trim();
      var guid = ((kind === "consult" ? window.HUBSPOT_FORM_CONSULT : window.HUBSPOT_FORM_DOWNLOAD) || "").trim();
      if (!portal || !guid) {
        // 設定前：送信しない
        show(note, true);
        return;
      }
      busy = true;
      if (btn) btn.disabled = true;
      var original = label ? label.textContent : "";
      if (label) label.textContent = "送信しています…";
      var url = "https://api.hsforms.com/submissions/v3/integration/submit/" + encodeURIComponent(portal) + "/" + encodeURIComponent(guid);
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload(form))
      }).then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res;
      }).then(function () {
        form.hidden = true;
        if (done) {
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

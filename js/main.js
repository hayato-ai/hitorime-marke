/* スクロール時のふわっとした表示、スマホ下部バーの出し入れ
   （v13：開閉するメニュー（トグル）は廃止。ナビは CSS だけで出し分ける。FAQ の開閉は <details> のネイティブ動作なので JS は不要。ヘッダーの固定と、バーの表示そのものは CSS だけで動く。JS が失敗しても <head> の保険タイマーで全部表示される） */
(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canObserve = "IntersectionObserver" in window;

  // html.js クラスは <head> のインラインで付けている（初期状態を透明にするのは動きを使える環境だけ）

  function initReveal() {
    var targets = document.querySelectorAll(".reveal");
    if (!targets.length) return;
    if (reduce || !canObserve) {
      for (var i = 0; i < targets.length; i++) targets[i].classList.add("is-visible");
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: "0px 0px -6% 0px" });
    for (var j = 0; j < targets.length; j++) io.observe(targets[j]);

    // 保険：何らかの理由で検知されなかった要素も、一定時間後に表示する
    window.setTimeout(function () {
      for (var k = 0; k < targets.length; k++) targets[k].classList.add("is-visible");
    }, 4000);
  }

  // スマホ：ページ内の CTA のボタン行（FV と FV のフォームのカード、プランの後の .plans-cta、担当者の後の白の行 .cta-row、最後の紺の帯 .cta-band）が画面に見えている間は、
  // 下部の追従バーを隠す（重複を避ける）。JS が無い時は常に表示。ボタン行そのものを観察するので、バーが隠れている間は必ず別のボタンが見えている
  function initBar() {
    var bar = document.querySelector(".cta-bar");
    var rows = document.querySelectorAll(".hero .btn-row, .hero-form, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row");
    if (!bar || !rows.length || !canObserve) return;
    var seen = [];
    var bio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var i = Array.prototype.indexOf.call(rows, e.target);
        // ボタン行は半分以上、背の高い FV のフォームのカードは4分の1以上見えていれば「見えている」とする
        seen[i] = e.isIntersecting && e.intersectionRatio >= (e.target.classList.contains("hero-form") ? 0.25 : 0.5);
      });
      var hide = seen.some(Boolean);
      bar.classList.toggle("is-hidden", hide);
    }, { threshold: [0, 0.25, 0.5, 0.75, 1], rootMargin: "-70px 0px 0px 0px" }); // 上は固定ヘッダー（スマホ69px）の下から数える
    for (var k = 0; k < rows.length; k++) bio.observe(rows[k]);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initReveal();
    initBar();
    // ここまで正常に動いた：<head> の保険タイマー（4秒後に js クラスを外して全部表示する）を解除する
    if (window.__revealTimer) window.clearTimeout(window.__revealTimer);
  });
})();

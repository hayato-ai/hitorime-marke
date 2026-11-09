// v14：FV（要点カード3つ＋資料請求フォームのカード）の収まり。320〜1440px：横スクロールなし、要点カードの文字が欠けない・値が折れない、
// カードが同じ高さ、ボタンが欠けない、フォームのカードがコンテナの中（PC は右、スマホは下）、H1 の第1文節が1行
import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9362);
let bad = 0;
const WS = [[320, 568, true], [360, 740, true], [375, 812, true], [414, 896, true], [479, 800, true], [480, 800, true], [600, 900, true], [767, 1024, false], [768, 1024, false], [959, 800, false], [960, 800, false], [1024, 800, false], [1100, 800, false], [1139, 800, false], [1140, 800, false], [1200, 800, false], [1280, 800, false], [1440, 900, false]];
try {
  for (const [w, h, m] of WS) {
    await cdp.viewport(w, h, m, 1);
    await cdp.goto(SITE + 'index.html', 700);
    const r = await cdp.ev(`(() => {
      const R = (e) => e.getBoundingClientRect();
      const de = document.documentElement;
      const kf = [...document.querySelectorAll('.key-facts li')].map((li) => { const k = li.querySelector('.key-facts__k'), v = li.querySelector('.key-facts__v'); const lh = (e) => parseFloat(getComputedStyle(e).lineHeight); return { w: Math.round(R(li).width), h: Math.round(R(li).height), vLines: Math.round(R(v).height / lh(v)), kLines: Math.round(R(k).height / lh(k)), vClip: v.scrollWidth > v.clientWidth + 1, vOver: R(v).right > R(li).right - 6, kOver: R(k).right > R(li).right - 6 }; });
      const g = document.querySelector('.hero__grid'); const t = document.querySelector('.hero__text'), f = document.querySelector('#hero-form');
      const gr = R(g), tr = R(t), fr = R(f);
      const btns = [...document.querySelectorAll('.hero .btn-row .btn')].map((b) => { const r = R(b); const sp = b.firstElementChild; return { w: Math.round(r.width), h: Math.round(r.height), top: Math.round(r.top), right: Math.round(r.right), clip: R(sp).right > r.right - 40 || b.scrollWidth > b.clientWidth + 1 }; });
      const bub = R(document.querySelector('.hero .bubble'));
      const h1 = document.querySelector('.hero h1'); const ph = h1.querySelector('.phrase'); const lh1 = parseFloat(getComputedStyle(h1).lineHeight);
      return { sw: de.scrollWidth, cw: de.clientWidth, kf, side: fr.left > tr.right - 1, below: fr.top >= tr.bottom - 1, fIn: fr.left >= gr.left - 0.5 && fr.right <= gr.right + 0.5, fw: Math.round(fr.width), fh: Math.round(fr.height), tw: Math.round(tr.width), tr: Math.round(tr.right), btns, bubR: Math.round(bub.right), vw: innerWidth, p1Lines: Math.round(R(ph).height / lh1), h1fs: getComputedStyle(h1).fontSize, imgs: document.querySelectorAll('.hero img').length };
    })()`);
    const iss = [];
    if (r.sw > r.cw) iss.push(`横スクロール ${r.sw}/${r.cw}`);
    if (r.imgs) iss.push('FV に画像が残っている');
    const hs = new Set(r.kf.map((x) => x.h));
    if (r.kf.length !== 3) iss.push('要点カードが3つでない');
    for (const k of r.kf) { if (k.vClip || k.vOver || k.kOver) iss.push('要点カードの文字が枠からはみ出す ' + JSON.stringify(k)); if (k.vLines !== 1) iss.push('要点カードの値が折り返す ' + k.vLines); }
    if (w >= 480 && hs.size > 1) iss.push('要点カードの高さがそろわない ' + [...hs]);
    if (w >= 480 && r.kf.some((k) => k.kLines > 2)) iss.push('要点カードのラベルが3行以上');
    if (!r.fIn) iss.push('フォームのカードがコンテナからはみ出す');
    if (w >= 960 && !r.side) iss.push('PC でフォームのカードが右にない');
    if (w < 960 && !r.below) iss.push('スマホ／タブレットでフォームのカードが下にない');
    if (r.btns.some((b) => b.clip)) iss.push('ボタンの文字が欠ける ' + JSON.stringify(r.btns));
    if (r.btns.some((b) => b.h < 60)) iss.push('ボタンの高さが60px未満');
    if (r.bubR > r.vw - 8) iss.push('吹き出しが画面端に寄りすぎ');
    if (r.p1Lines !== 1) iss.push('H1 の第1文節が1行でない ' + r.p1Lines);
    if (w >= 960 && r.fw < 380) iss.push('フォームのカードが狭い ' + r.fw);
    bad += iss.length ? 1 : 0;
    console.log(`${String(w).padStart(4)} ${iss.length ? 'NG' : 'ok'} kf=${r.kf.map((k) => k.w + 'x' + k.h).join(',')} form=${r.fw}x${r.fh} text=${r.tw} btns=${r.btns.map((b) => b.w + '@' + b.top).join(',')} h1=${r.h1fs}` + (iss.length ? '\n      - ' + iss.join('\n      - ') : ''));
  }
} finally { await cdp.close(); }
console.log(bad ? `NG ${bad}` : 'FV：全て通過');

// 使い方: node qa/clip.mjs <page> <w> <h> <mobile 0|1> <selector> <out> [pad] … セレクタの要素（周囲 pad px）を全体撮影（captureBeyondViewport）
import { launch, SITE, SP, sleep } from './cdp.mjs';
const [page, w, h, mobile, sel, out, pad] = process.argv.slice(2);
const cdp = await launch(9354);
try {
  await cdp.viewport(+w, +h, mobile === '1', 1);
  await cdp.goto(SITE + page + '.html', 1500);
  await cdp.ev(`document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-visible')); true`);
  await sleep(900);
  const r = await cdp.ev(`(() => { const el = document.querySelector(${JSON.stringify(sel)}); const b = el.getBoundingClientRect(); return { x: 0, y: b.top + scrollY, w: innerWidth, h: b.height }; })()`);
  const P = +(pad || 0);
  await cdp.shot(`${SP}/qa_shots/t13/${out}.png`, { x: 0, y: Math.max(0, r.y - P), width: r.w, height: r.h + 2 * P }, true);
  console.log(out, Math.round(r.h));
} finally { await cdp.close(); }

// 使い方: node qa/vp.mjs <page> <w> <h> <mobile 0|1> <selector> <outfile> [offsetY]  … セレクタの要素が画面の上から offset の位置に来るようにして撮る
import { launch, SITE, SP, sleep } from './cdp.mjs';
const [page, w, h, mobile, sel, out, off] = process.argv.slice(2);
const cdp = await launch(9353);
try {
  await cdp.viewport(+w, +h, mobile === '1', 1);
  await cdp.goto(SITE + page + '.html', 1200);
  await cdp.ev(`document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-visible')); true`);
  await sleep(700);
  await cdp.ev(`(() => { const el = document.querySelector(${JSON.stringify(sel)}); const r = el.getBoundingClientRect(); scrollTo({ top: scrollY + r.top - ${+(off || 90)}, behavior: 'instant' }); })(); true`);
  await sleep(900);
  await cdp.shot(`${SP}/qa_shots/t14/${out}.png`);
} finally { await cdp.close(); }

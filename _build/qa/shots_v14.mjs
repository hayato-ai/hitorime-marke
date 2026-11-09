// 全ページを375／1024／1440pxで、ビューポート単位（固定要素が実際の位置に写る）で撮る
// 使い方: node qa/shots_v14.mjs [page ...]   出力: ref_shots/v14_<page>_<m|d>_NN.png
import { launch, SITE, SP, sleep } from './cdp.mjs';
const pages = process.argv.slice(2).length ? process.argv.slice(2) : ['index', 'profile', 'contact', 'download', 'privacy'];
const cdp = await launch(9341);
try {
  for (const [tag, w, h, mobile] of [['m', 375, 812, true], ['t', 1024, 768, false], ['d', 1440, 900, false]]) {
    await cdp.viewport(w, h, mobile, 1);
    for (const p of pages) {
      await cdp.goto(SITE + p + '.html', 1800);
      const total = await cdp.ev('document.documentElement.scrollHeight');
      const step = h - 120;
      let n = 0;
      for (let y = 0; ; y += step) {
        const yy = Math.min(y, total - h);
        await cdp.ev(`scrollTo({top:${yy},behavior:'instant'}); true`);
        await sleep(900);
        // v10：画面内の写真が読み込まれ終わるまで待つ（最大6秒）。読み込めていない写真があれば報告
        const pend = await cdp.ev(`(async () => { const t0 = Date.now(); const vis = () => [...document.querySelectorAll('img')].filter((im) => { const r = im.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; }); while (Date.now() - t0 < 6000 && vis().some((im) => !(im.complete && im.naturalWidth > 0))) await new Promise((r) => setTimeout(r, 150)); return vis().filter((im) => !(im.complete && im.naturalWidth > 0)).length; })()`);
        if (pend) console.log('  [NG] 読み込めていない写真', p, tag, yy, pend);
        await cdp.shot(`${SP}/ref_shots/v14_${p}_${tag}_${String(n++).padStart(2, '0')}.png`);
        if (yy >= total - h) break;
      }
      console.log(p, tag, 'total', total, 'shots', n);
    }
  }
} finally { await cdp.close(); }

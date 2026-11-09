// H1 の折り返し（各行の文字）を、幅ごとに測る
import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9360);
try {
  for (const [w, h, m] of [[320,568,true],[360,740,true],[375,812,true],[414,896,true],[480,800,true],[520,800,true],[540,800,true],[600,900,true],[767,1024,false],[768,1024,false],[959,800,false],[960,800,false],[1024,800,false],[1100,800,false],[1200,800,false],[1280,800,false],[1440,900,false]]) {
    await cdp.viewport(w, h, m);
    await cdp.goto(SITE + 'index.html', 500);
    const r = await cdp.ev(`(() => {
      const h1 = document.querySelector('.hero h1'); const rng = document.createRange(); const lines = []; let cur = null;
      const walker = document.createTreeWalker(h1, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) { const n = walker.currentNode; for (let i = 0; i < n.length; i++) { rng.setStart(n, i); rng.setEnd(n, i + 1); const rc = rng.getClientRects()[0]; if (!rc) continue; const y = Math.round(rc.top); if (!cur || Math.abs(cur.y - y) > 6) { cur = { y, t: '', r: 0 }; lines.push(cur); } cur.t += n.data[i]; cur.r = Math.max(cur.r, rc.right); } }
      const cs = getComputedStyle(h1); const hr = h1.getBoundingClientRect();
      return { fs: cs.fontSize, boxR: Math.round(hr.right), lines: lines.map(l => l.t + ' (' + Math.round(l.r) + ')') };
    })()`);
    console.log(String(w).padStart(4), r.fs, 'boxR=' + r.boxR, JSON.stringify(r.lines));
  }
} finally { await cdp.close(); }

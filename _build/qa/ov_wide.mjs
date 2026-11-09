import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9345);
try {
  for (const w of [960, 1024, 1100, 1199, 1200]) {
    await cdp.viewport(w, 800, false, 1);
    await cdp.goto(SITE + 'index.html', 500);
    const r = await cdp.ev(`(() => { const de=document.documentElement; const b=[...document.querySelectorAll('.hero .btn')].map(a=>{const r=a.getBoundingClientRect(); const t=document.querySelector('.hero__text').getBoundingClientRect(); return Math.round(r.right - t.right)}); return {sw:de.scrollWidth, cw:de.clientWidth, btnOverText:b}; })()`);
    console.log(w, JSON.stringify(r));
  }
} finally { await cdp.close(); }

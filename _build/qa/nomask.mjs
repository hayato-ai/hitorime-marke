import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9340);
let bad = 0;
try {
  for (const w of [320, 360, 375, 414, 600, 767]) {
    await cdp.viewport(w, 800, w < 768);
    for (const p of ['index', 'profile', 'profile', 'contact', 'download', 'privacy']) {
      await cdp.goto(SITE + p + '.html', 400);
      await cdp.ev(`(() => { const s = document.createElement('style'); s.textContent = 'html,body{overflow-x:visible !important}'; document.head.appendChild(s); return true; })()`);
      await sleep(100);
      const r = await cdp.ev(`({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, bsw: document.body.scrollWidth })`);
      const ok = r.sw <= r.cw;
      if (!ok) bad++;
      if (!ok || w === 375) console.log(`${w} ${p.padEnd(9)} scrollW=${r.sw} clientW=${r.cw} ${ok ? 'ok' : 'OVERFLOW'}`);
    }
  }
} finally { await cdp.close(); }
console.log(bad ? 'NG ' + bad : 'no overflow even without overflow-x:hidden (320-767px, all pages)');

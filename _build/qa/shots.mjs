// 使い方:
//   node shots.mjs <page> <w> <h> <mobile 0|1> <dpr> slices <sliceH> <prefix>
//   node shots.mjs <page> <w> <h> <mobile 0|1> <dpr> at <y1,y2,...|bottom|top> <prefix> [open-menu]
import { launch, SITE, SP, sleep } from './cdp.mjs';
const [page, w, h, mobile, dpr, mode, arg, prefix, extra] = process.argv.slice(2);
const W = +w, H = +h;
const cdp = await launch(9335);
try {
  await cdp.viewport(W, H, mobile === '1', +dpr);
  await cdp.goto(SITE + page + ".html", 2500);
  const out = (n) => `${SP}/${prefix}_${String(n).padStart(2, '0')}.png`;
  if (mode === 'slices') {
    await cdp.ev(`document.querySelectorAll('.reveal,.reveal-group').forEach(e => e.classList.add('is-visible')); true`);
    await sleep(1200);
    const total = await cdp.ev(`document.documentElement.scrollHeight`);
    const S = +arg;
    let n = 0;
    for (let y = 0; y < total; y += S) {
      await cdp.shot(out(n++), { x: 0, y, width: W, height: Math.min(S, total - y) }, true);
    }
    console.log(`${page} ${W}x${H} total=${total} → ${n} slices`);
  } else if (mode === 'at') {
    const max = await cdp.ev(`document.documentElement.scrollHeight - innerHeight`);
    const ys = arg.split(',').map((s) => (s === 'bottom' ? max : s === 'top' ? 0 : +s));
    let n = 0;
    for (const y of ys) {
      if (extra === 'open-menu') {
        await cdp.ev(`document.getElementById('nav-toggle').click(); true`);
      }
      await cdp.ev(`scrollTo({top:${y},behavior:'instant'}); true`);
      await sleep(1100);
      await cdp.shot(out(n++));
    }
    console.log(`${page} ${W}x${H} viewport shots at ${ys.join(',')} (max=${max})`);
  }
} finally { await cdp.close(); }

import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9339);
const probe = `(() => {
  const bar = document.querySelector('.cta-bar'), footer = document.querySelector('.site-footer'), hdr = document.querySelector('.site-header');
  const br = bar.getBoundingClientRect(); const de = document.documentElement;
  const btn = bar.querySelector('.btn').getBoundingClientRect();
  return { vw: innerWidth, vh: innerHeight, hdrPos: getComputedStyle(hdr).position, barH: Math.round(br.height), barBottom: Math.round(br.bottom), btnBottom: Math.round(btn.bottom), bodyPB: getComputedStyle(document.body).paddingBottom,
    scrollW: de.scrollWidth, atBottomFooterBottom: null };
})()`;
try {
  // 横向きスマホ
  for (const [w, h] of [[667, 375], [736, 414], [568, 320]]) {
    await cdp.viewport(w, h, true);
    for (const page of ['index', 'contact']) {
      await cdp.goto(SITE + page + '.html', 500);
      await cdp.ev(`scrollTo({top: document.documentElement.scrollHeight, behavior:'instant'}); true`);
      await sleep(600);
      const p = await cdp.ev(probe);
      const fb = await cdp.ev(`Math.round(document.querySelector('.site-footer').getBoundingClientRect().bottom)`);
      const barTop = await cdp.ev(`Math.round(document.querySelector('.cta-bar').getBoundingClientRect().top)`);
      console.log(`landscape ${w}x${h} ${page.padEnd(8)} header=${p.hdrPos} barH=${p.barH} scrollW=${p.scrollW}/${p.vw} footerBottom=${fb} barTop=${barTop} ${fb <= barTop + 1 && p.scrollW <= p.vw ? 'ok' : 'NG'}`);
    }
  }
  // 安全領域（iPhone のホームバー）
  await cdp.viewport(375, 812, true);
  let supported = true;
  try { await cdp.send('Emulation.setSafeAreaInsetsOverride', { insets: { top: 0, left: 0, bottom: 34, right: 0 } }); } catch (e) { supported = false; console.log('safe-area override unsupported:', e.message); }
  if (supported) {
    await cdp.goto(SITE + 'index.html', 600);
    await cdp.ev(`scrollTo({top: document.documentElement.scrollHeight, behavior:'instant'}); true`);
    await sleep(600);
    const p = await cdp.ev(probe);
    const fb = await cdp.ev(`Math.round(document.querySelector('.site-footer').getBoundingClientRect().bottom)`);
    const barTop = await cdp.ev(`Math.round(document.querySelector('.cta-bar').getBoundingClientRect().top)`);
    const inset = await cdp.ev(`(() => { const d = document.createElement('div'); d.style.cssText = 'position:fixed;bottom:0;height:env(safe-area-inset-bottom,0px)'; document.body.appendChild(d); const h = d.getBoundingClientRect().height; d.remove(); return h; })()`);
    console.log(`safe-area inset(bottom)=${inset}px → barH=${p.barH} (expect 68+34=102) bodyPB=${p.bodyPB} footerBottom=${fb} barTop=${barTop} btnBottom=${p.btnBottom} vh=${p.vh} ${p.barH === 102 && fb <= barTop + 1 && p.btnBottom <= p.vh - 34 ? 'ok' : 'CHECK'}`);
    await cdp.shot(`${SP}/m375_safearea.png`);
  }
} finally { await cdp.close(); }

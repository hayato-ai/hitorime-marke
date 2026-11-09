import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9338);
const state = `(() => {
  const all = [...document.querySelectorAll('.reveal, .reveal-group .part')];
  const hidden = all.filter(e => parseFloat(getComputedStyle(e).opacity) < 0.99);
  return { total: all.length, notVisibleClass: document.querySelectorAll('.reveal:not(.is-visible), .reveal-group:not(.is-visible)').length, opacityHidden: hidden.length, jsClass: document.documentElement.classList.contains('js') };
})()`;
try {
  await cdp.viewport(375, 812, true);
  // 1) 通常（JSあり）：スクロールで順に表示される
  await cdp.goto(SITE + 'index.html', 600);
  let st = await cdp.ev(state);
  console.log('normal  @load   ', JSON.stringify(st));
  const max = await cdp.ev('document.documentElement.scrollHeight - innerHeight');
  for (let y = 0; y <= max + 400; y += 400) { await cdp.ev(`scrollTo({top:${y},behavior:'instant'}); true`); await sleep(120); }
  await sleep(1500);
  st = await cdp.ev(state);
  console.log('normal  @scrolled', JSON.stringify(st), st.opacityHidden === 0 && st.notVisibleClass === 0 ? 'ok' : 'NG');

  // 2) 視差・動きを減らす設定：最初から全部表示
  await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  await cdp.goto(SITE + 'index.html', 600);
  st = await cdp.ev(state);
  console.log('reduce  @load   ', JSON.stringify(st), st.opacityHidden === 0 ? 'ok' : 'NG');
  await cdp.send('Emulation.setEmulatedMedia', { features: [] });

  // 3) JS無効：最初から全部表示、CTAは CSS だけで動く
  await cdp.send('Emulation.setScriptExecutionDisabled', { value: true });
  for (const [w, h, m] of [[375, 812, true], [1280, 800, false]]) {
    await cdp.viewport(w, h, m);
    await cdp.goto(SITE + 'index.html', 600);
    st = await cdp.ev(state);
    const cta = await cdp.ev(`(() => { const hc = document.querySelector('.header-cta'), bar = document.querySelector('.cta-bar'); const el = innerWidth >= 768 ? hc : bar; const r = el.getBoundingClientRect(); return { which: innerWidth >= 768 ? 'header' : 'bar', shown: r.width > 0, bottom: Math.round(r.bottom), vh: innerHeight, hdrPos: getComputedStyle(document.querySelector('.site-header')).position }; })()`);
    console.log(`nojs ${w}  @load   `, JSON.stringify(st), JSON.stringify(cta), st.opacityHidden === 0 && cta.shown ? 'ok' : 'NG');
  }
} finally { await cdp.close(); }

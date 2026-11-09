// JS失敗時の保険と、スマホ下部バーの出し入れを確かめる
import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9343);
const st = `(() => { const all=[...document.querySelectorAll('.reveal')]; const bar=document.querySelector('.cta-bar'); const cs=getComputedStyle(bar); const r=bar.getBoundingClientRect();
  return { js: document.documentElement.classList.contains('js'), timer: typeof window.__revealTimer, reveals: all.length, hiddenReveals: all.filter(e=>parseFloat(getComputedStyle(e).opacity)<0.99).length, barHiddenClass: bar.classList.contains('is-hidden'), barVis: cs.visibility, barTop: Math.round(r.top), vh: innerHeight }; })()`;
let bad = 0;
try {
  await cdp.viewport(375, 812, true);
  // 1) main.js が読み込めない場合：4秒後に js クラスが外れて全て表示、バーは常に表示
  await cdp.send('Network.enable');
  await cdp.send('Network.setBlockedURLs', { urls: ['*main.js*'] });
  await cdp.goto(SITE + 'index.html', 300);
  let s = await cdp.ev(st);
  console.log('main.js blocked @0.3s', JSON.stringify(s));
  await sleep(4300);
  s = await cdp.ev(st);
  const ok1 = !s.js && s.hiddenReveals === 0 && !s.barHiddenClass && s.barVis === 'visible' && s.barTop < s.vh;
  console.log('main.js blocked @4.6s', JSON.stringify(s), ok1 ? 'ok' : 'NG'); if (!ok1) bad++;
  await cdp.send('Network.setBlockedURLs', { urls: [] });

  // 2) main.js が正常：保険タイマーは解除され、js クラスが残る
  await cdp.goto(SITE + 'index.html', 4800);
  s = await cdp.ev(st);
  const ok2 = s.js; console.log('normal @4.8s (timer cleared → js stays)', JSON.stringify(s), ok2 ? 'ok' : 'NG'); if (!ok2) bad++;

  // 3) スマホ下部バーの出し入れ（index）
  await cdp.goto(SITE + 'index.html', 900);
  s = await cdp.ev(st);
  let ok3 = s.barHiddenClass && s.barVis === 'hidden'; console.log('bar @top (FV buttons visible)', s.barHiddenClass, s.barVis, ok3 ? 'ok' : 'NG'); if (!ok3) bad++;
  const rowsVis = `(() => { const rows=[...document.querySelectorAll('.hero .btn-row, .hero-form, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row')]; return rows.map((r)=>{ const b=r.getBoundingClientRect(); return Math.round(Math.max(0, Math.min(b.bottom, innerHeight) - Math.max(b.top, 70)) / b.height * 100); }); })()`;
  const total = await cdp.ev('document.documentElement.scrollHeight');
  let ngBar = 0, nHidden = 0, nShown = 0, nBand = 0;
  for (let y = 0; y <= total - 812; y += 150) {
    await cdp.ev(`scrollTo({top:${y},behavior:'instant'}); true`); await sleep(450);
    s = await cdp.ev(st);
    const v = await cdp.ev(rowsVis);
    const want = v.some((p, i) => p >= (i === 1 ? 25 : 55)), mustShow = v.every((p, i) => p < (i === 1 ? 20 : 45));   // v14：index 1 は FV のフォームのカード（4分の1以上見えていれば隠れる）
    const hidden = s.barHiddenClass && s.barVis === 'hidden', shown = !s.barHiddenClass && s.barVis === 'visible';
    if (hidden) nHidden++; if (shown) nShown++;
    if (v.slice(2).some((p) => p >= 55)) nBand++;
    const bad = (want && !hidden) || (mustShow && !shown);
    if (bad) { ngBar++; console.log(`  NG scrollY=${y} rows=${v} hidden=${hidden} shown=${shown}`); }
  }
  console.log(`bar sweep: hidden ${nHidden} / shown ${nShown} positions (うち FV 以外の途中の白の行で隠れた位置 ${nBand}) ${ngBar ? 'NG ' + ngBar : 'ok'}`); if (ngBar || !nHidden || !nShown || !nBand) bad++;
  // 紺の各面のボタン行を個別に画面中央へ：隠れること
  const nrows = await cdp.ev(`document.querySelectorAll('.hero .btn-row, .hero-form, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row').length`);
  for (let i = 0; i < nrows; i++) {
    await cdp.ev(`(() => { const r=document.querySelectorAll('.hero .btn-row, .hero-form, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row')[${i}]; const b=r.getBoundingClientRect(); scrollTo({top: scrollY + b.top - innerHeight/2 + b.height/2, behavior:'instant'}); })(); true`); await sleep(600);
    s = await cdp.ev(st);
    const cls = await cdp.ev(`document.querySelectorAll('.hero .btn-row, .hero-form, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row')[${i}].closest('section').className`);
    const ok = s.barHiddenClass && s.barVis === 'hidden'; console.log(`  row ${i} (${cls}) centered → bar hidden=${s.barHiddenClass}`, ok ? 'ok' : 'NG'); if (!ok) bad++;
  }
  // 途中（サービス内容の中ほど）では表示
  await cdp.ev(`document.getElementById('flow').scrollIntoView({block:'center', behavior:'instant'}); true`); await sleep(700);
  s = await cdp.ev(st); const ok4 = !s.barHiddenClass && s.barVis === 'visible'; console.log('bar @flow', ok4 ? 'ok (shown)' : 'NG'); if (!ok4) bad++;
  await cdp.ev(`scrollTo({top:0,behavior:'instant'}); true`); await sleep(600);
  s = await cdp.ev(st); const ok5 = s.barHiddenClass && s.barVis === 'hidden'; console.log('bar back @top', ok5 ? 'ok (hidden)' : 'NG'); if (!ok5) bad++;
  // 4) 他ページ：profile は最後の途中の白の行が見えている間だけ隠れる。contact / download / privacy は常に表示（contact は自ページのボタンだけ隠れる）
  for (const p of ['contact', 'download', 'privacy']) {
    await cdp.goto(SITE + p + '.html', 700);
    s = await cdp.ev(st);
    const vis = await cdp.ev(`[...document.querySelectorAll('.cta-bar a')].map(a=>a.getBoundingClientRect().width>0)`);
    const ok = !s.barHiddenClass && s.barVis === 'visible' && s.barTop < s.vh; console.log(p, 'bar', JSON.stringify(vis), ok ? 'ok' : 'NG'); if (!ok) bad++;
  }
  // 5) スクリプト無効
  await cdp.send('Emulation.setScriptExecutionDisabled', { value: true });
  await cdp.goto(SITE + 'index.html', 600);
  s = await cdp.ev(st);
  const ok6 = !s.js && s.hiddenReveals === 0 && s.barVis === 'visible'; console.log('JS disabled', JSON.stringify(s), ok6 ? 'ok' : 'NG'); if (!ok6) bad++;
} finally { await cdp.close(); }
console.log(bad ? 'NG ' + bad : 'jsfail/bar all ok');

// v14：FAQ のアコーディオン（details/summary）。最初は全部閉じている／クリック・Enter・Space で開閉／開いた状態で横はみ出しなし（320〜1440px）／JS 無効でも開閉できる
import { launch, SITE, SP, sleep } from './cdp.mjs';
const cdp = await launch(9348);
let bad = 0;
const fail = (m) => { bad++; console.log('   NG', m); };
const STATE = `(() => [...document.querySelectorAll('#faq details.qa')].map((d) => {
  const s = d.querySelector('summary'), a = d.querySelector('.qa__a'), ic = d.querySelector('.qa__icon');
  const sr = s.getBoundingClientRect(), ar = a.getBoundingClientRect();
  const q = d.querySelector('.qa__badge').getBoundingClientRect(), ab = d.querySelector('.qa__badge--a').getBoundingClientRect();
  const h3 = d.querySelector('h3').getBoundingClientRect(), icr = ic.getBoundingClientRect();
  const afterOp = parseFloat(getComputedStyle(ic, '::after').opacity);
  return { open: d.open, sH: Math.round(sr.height), aShown: a.checkVisibility() && ar.width > 0 && ar.height > 0, aH: Math.round(ar.height), aRight: Math.round(ar.right), qLeft: Math.round(q.left), aLeft: Math.round(ab.left),
    h3Right: Math.round(h3.right), icLeft: Math.round(icr.left), icRight: Math.round(icr.right), dRight: Math.round(d.getBoundingClientRect().right), afterOp, pRight: Math.round(d.querySelector('.qa__a p').getBoundingClientRect().right), vw: innerWidth, sw: document.documentElement.scrollWidth };
}))()`;
async function click(i) {
  const r = await cdp.ev(`(() => { const s = document.querySelectorAll('#faq details.qa summary')[${i}]; s.scrollIntoView({ block: 'center', behavior: 'instant' }); const b = s.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2 }; })()`);
  await sleep(120);
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: r.x, y: r.y });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: r.x, y: r.y, button: 'left', clickCount: 1 });
  await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r.x, y: r.y, button: 'left', clickCount: 1 });
  await sleep(380);
}
async function key(i, k) {
  await cdp.ev(`document.querySelectorAll('#faq details.qa summary')[${i}].focus(); true`);
  const code = k === 'Enter' ? { key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, text: '\r' } : { key: ' ', code: 'Space', windowsVirtualKeyCode: 32, text: ' ' };
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', ...code });
  await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', ...code });
  await sleep(380);
}
try {
  for (const [w, h, m] of [[320, 568, true], [360, 740, true], [375, 812, true], [414, 896, true], [600, 900, true], [768, 1024, false], [960, 800, false], [1024, 800, false], [1280, 800, false], [1440, 900, false]]) {
    await cdp.viewport(w, h, m);
    await cdp.goto(SITE + 'index.html', 700);
    const n0 = await cdp.ev(`document.querySelectorAll('#faq details.qa').length`);
    let st = await cdp.ev(STATE);
    console.log(`${w}: details=${n0}`);
    if (n0 !== 4) fail('details が4つでない');
    if (st.some((x) => x.open || x.aShown)) fail('最初から開いている／答えが見えている');
    if (st.some((x) => x.sH < 44)) fail('summary の高さが44px未満 ' + st.map((x) => x.sH));
    if (st.some((x) => x.icRight > x.dRight || x.h3Right > x.icLeft + 0.5)) fail('見出しとアイコンが重なる／はみ出す ' + JSON.stringify(st.map((x) => [x.h3Right, x.icLeft, x.icRight, x.dRight])));
    // クリックで開閉（1問ずつ）
    for (let i = 0; i < 4; i++) {
      await click(i);
      st = await cdp.ev(STATE);
      const x = st[i];
      if (!x.open || !x.aShown || x.aH < 20) fail(`Q${i + 1}: クリックで開かない ${JSON.stringify(x)}`);
      if (x.aRight > x.vw + 0.5 || x.pRight > x.dRight + 0.5 || x.sw > x.vw) fail(`Q${i + 1}: 開いた状態で横はみ出し ${JSON.stringify(x)}`);
      if (Math.abs(x.qLeft - x.aLeft) > 1) fail(`Q${i + 1}: Q と A のバッジの左がそろっていない ${x.qLeft}/${x.aLeft}`);
      if (!(x.afterOp < 0.1)) fail(`Q${i + 1}: 開いたとき＋が−になっていない（縦線の opacity=${x.afterOp}）`);
      await click(i);
      st = await cdp.ev(STATE);
      if (st[i].open || st[i].aShown) fail(`Q${i + 1}: もう一度クリックで閉じない`);
      if (!(st[i].afterOp > 0.9)) fail(`Q${i + 1}: 閉じたとき−が＋に戻っていない（opacity=${st[i].afterOp}）`);
    }
    // キーボード：Enter／Space で開閉
    for (const k of ['Enter', 'Space']) {
      await key(0, k);
      st = await cdp.ev(STATE);
      if (!st[0].open) fail(`${k} で開かない`);
      await key(0, k);
      st = await cdp.ev(STATE);
      if (st[0].open) fail(`${k} で閉じない`);
    }
    // 4つ同時に開く（個別に開閉できる＝他を閉じない）。最も長い答え（Q1）を含めて横はみ出しがないこと
    for (let i = 0; i < 4; i++) await click(i);
    st = await cdp.ev(STATE);
    if (!st.every((x) => x.open && x.aShown)) fail('4つ同時に開けない');
    if (st.some((x) => x.sw > x.vw || x.aRight > x.vw || x.pRight > x.dRight + 0.5)) fail('4つ開いたとき横はみ出し');
    const ov = await cdp.ev(`(() => { const vw = innerWidth; return [...document.querySelectorAll('#faq *')].filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.right > vw + 0.5 || r.left < -0.5); }).length; })()`);
    if (ov) fail('FAQ 内に画面外の要素 ' + ov);
    if (w === 375 || w === 1440) { await cdp.ev(`document.getElementById('faq').scrollIntoView({block:'start', behavior:'instant'}); true`); await sleep(500); await cdp.shot(`${SP}/qa_shots/t13/faq_open_${w}.png`); }
    // #faq のアンカー
    await cdp.goto(SITE + 'index.html#faq', 2200);
    const tp = await cdp.ev(`Math.round(document.getElementById('faq').getBoundingClientRect().top)`);
    if (tp < 0 || tp > h) fail('#faq に着地しない top=' + tp);
  }
  // JS 無効でも開閉できる（ネイティブ）
  await cdp.send('Emulation.setScriptExecutionDisabled', { value: true });
  await cdp.viewport(375, 812, true);
  await cdp.goto(SITE + 'index.html', 600);
  await click(1);
  let st = await cdp.ev(STATE);
  console.log('JS 無効: Q2 をクリック → open=', st[1].open, st[1].aShown);
  if (!st[1].open || !st[1].aShown) fail('JS 無効で開かない');
  await click(1);
  st = await cdp.ev(STATE);
  if (st[1].open) fail('JS 無効で閉じない');
} finally { await cdp.close(); }
console.log(bad ? 'NG ' + bad : 'faq accordion all ok');

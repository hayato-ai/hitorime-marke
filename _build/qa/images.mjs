// v10：Unsplash の写真が、ネットワーク経由で実際に読み込まれ、表示されることを確かめる（375／1440。毎回まっさらなプロファイルなのでキャッシュは効かない）
//   確かめること：images.unsplash.com へのリクエストが 200（image/*）で完了、<img> が complete・naturalWidth>0、枠の中に収まって表示（object-fit:cover）、
//   srcset で選ばれた幅が枠の実寸×DPR に足りること、読み込み失敗・コンソールエラーがないこと、LCP が FV の写真であること
import { launch, SITE, SP, sleep } from './cdp.mjs';
const cdp = await launch(9362);
let bad = 0;
try {
  await cdp.send('Network.enable');
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  const reqs = new Map();
  const errs = [];
  cdp.on((m) => {
    if (m.method === 'Network.requestWillBeSent') { const u = m.params.request.url; if (u.includes('images.unsplash.com')) reqs.set(m.params.requestId, { url: u, status: null, mime: null, bytes: null, failed: null, priority: m.params.request.initialPriority }); }
    else if (m.method === 'Network.responseReceived') { const r = reqs.get(m.params.requestId); if (r) { r.status = m.params.response.status; r.mime = m.params.response.mimeType; r.fromCache = m.params.response.fromDiskCache || m.params.response.fromServiceWorker; } }
    else if (m.method === 'Network.loadingFinished') { const r = reqs.get(m.params.requestId); if (r) r.bytes = m.params.encodedDataLength; }
    else if (m.method === 'Network.loadingFailed') { const r = reqs.get(m.params.requestId); if (r) r.failed = m.params.errorText; }
    else if (m.method === 'Runtime.exceptionThrown') errs.push(m.params.exceptionDetails.text);
    else if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errs.push(m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await cdp.send('Log.enable');
  for (const [tag, w, h, mobile, dpr] of [['375 (dpr2)', 375, 812, true, 2], ['375 (dpr1)', 375, 812, true, 1], ['1440', 1440, 900, false, 1]]) {
    await cdp.send('Page.navigate', { url: 'about:blank' }); await sleep(400);   // 前の幅のページが開いたままだと、幅を変えた時点で srcset の再選択の要求が出てしまう
    reqs.clear(); errs.length = 0;
    await cdp.viewport(w, h, mobile, dpr);
    await cdp.goto(SITE + 'index.html', 1500);
    const total = await cdp.ev('document.documentElement.scrollHeight');
    for (let y = 0; y <= total; y += Math.round(h * 0.6)) { await cdp.ev(`scrollTo({top:${y},behavior:'instant'}); true`); await sleep(350); }
    await sleep(2500);
    const imgs = await cdp.ev(`[...document.querySelectorAll('img')].map((im) => { const r = im.getBoundingClientRect(); const fr = im.parentElement.getBoundingClientRect(); const cs = getComputedStyle(im); return { alt: im.alt, cur: im.currentSrc.replace(/\\?.*w=(\\d+).*/, ' w=$1'), cw: +(/[?&]w=(\\d+)/.exec(im.currentSrc) || [0, 0])[1], complete: im.complete, nw: im.naturalWidth, nh: im.naturalHeight, w: Math.round(r.width), h: Math.round(r.height), frame: Math.round(fr.width) + 'x' + Math.round(fr.height), fit: cs.objectFit, op: getComputedStyle(im.closest('.reveal') || im).opacity, loading: im.loading, fp: im.getAttribute('fetchpriority') }; })`);
    console.log('==== ' + tag);
    for (const [id, r] of reqs) console.log('  net', r.status, r.mime, (r.bytes ?? '?') + 'B', r.failed ? 'FAILED ' + r.failed : '', r.url.replace('https://images.unsplash.com/', '').replace(/\?auto.*w=(\d+).*/, ' w=$1'));
    for (const i of imgs) {
      const need = i.w * dpr;   // 選ばれた候補の幅（w=600／1200）が、枠の実寸×DPR を満たすこと。naturalWidth は sizes で換算された値なので使わない
      const ok = i.complete && i.nw > 0 && i.fit === 'cover' && i.w > 0 && i.h > 0 && i.cw >= need * 0.95 && parseFloat(i.op) > 0.99;
      if (!ok) bad++;
      console.log(`  img ${ok ? 'ok' : 'NG'} alt="${i.alt}" ${i.cur} cand=${i.cw}w natural(sizes換算)=${i.nw}x${i.nh} need≈${Math.round(i.w * dpr)}px shown=${i.w}x${i.h} frame=${i.frame} fit=${i.fit} loading=${i.loading} fetchpriority=${i.fp} opacity=${i.op}`);
    }
    const okNet = [...reqs.values()].length >= 2 && [...reqs.values()].every((r) => r.status === 200 && /^image\//.test(r.mime) && !r.failed && r.bytes > 5000);
    if (!okNet) bad++;
    console.log('  network', okNet ? 'ok' : 'NG', `(${[...reqs.values()].length} requests)`, errs.length ? 'errors: ' + JSON.stringify(errs) : 'no console errors');
    if (errs.length) bad++;
    // FV の写真が最初に（eager で）読み込まれること：ページ読み込み直後の時点で要求済みか
    // 撮影（確認用）：写真の枠が見える位置で
    const names = tag.startsWith('1440') ? 'd' : (tag.includes('dpr2') ? 'm' : null);
    if (names) {
      for (const [sel, nm] of [['#service .ph', 'svc'], ['.cta-band .ph', 'cta']]) {
        await cdp.ev(`(() => { const el = document.querySelector(${JSON.stringify(sel)}); const r = el.getBoundingClientRect(); scrollTo({ top: scrollY + r.top - ${h > 800 ? 160 : 100}, behavior: 'instant' }); })(); true`);
        await sleep(700);
        await cdp.shot(`${SP}/ref_shots/v14_img_${nm}_${names}.png`);
      }
    }
  }
  // LCP（1440）
  await cdp.viewport(1440, 900, false, 1);
  await cdp.goto(SITE + 'index.html', 200);
  await cdp.ev(`window.__lcp = null; new PerformanceObserver((l) => { const e = l.getEntries().pop(); window.__lcp = { url: e.url, el: e.element && e.element.tagName, t: Math.round(e.startTime) }; }).observe({ type: 'largest-contentful-paint', buffered: true }); true`);
  await sleep(3500);
  const lcp = await cdp.ev('window.__lcp');
  console.log('LCP @1440:', JSON.stringify(lcp));
} finally { await cdp.close(); }
console.log(bad ? 'NG ' + bad : 'images: all loaded over the network and shown');

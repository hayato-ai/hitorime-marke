import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9334);
try {
  await cdp.viewport(1280, 800, false);
  await cdp.goto(SITE + 'index.html', 2500);
  const r = await cdp.ev(`(async () => {
    await document.fonts.ready;
    const faces = [...document.fonts];
    const by = {};
    for (const f of faces) by[f.status] = (by[f.status] || 0) + 1;
    const loaded = faces.filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight);
    const h1 = getComputedStyle(document.querySelector('h1')).fontFamily;
    return { total: faces.length, by, loadedSample: loaded.slice(0, 5), h1 };
  })()`);
  console.log(JSON.stringify(r, null, 1));
} finally { await cdp.close(); }

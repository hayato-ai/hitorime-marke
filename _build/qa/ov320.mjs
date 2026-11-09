import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9342);
try {
  await cdp.viewport(320, 700, true);
  await cdp.goto(SITE + 'index.html', 600);
  const r = await cdp.ev(`(() => { const out=[]; for (const el of document.body.querySelectorAll('*')) { const r = el.getBoundingClientRect(); if (r.right > 321 && r.width>0) out.push(el.tagName+'.'+el.className+' w'+Math.round(r.width)+' '+Math.round(r.left)+'-'+Math.round(r.right)); } return {vw: innerWidth, sw: document.documentElement.scrollWidth, out: out.slice(0,40)}; })()`);
  console.log(JSON.stringify(r,null,1));
} finally { await cdp.close(); }

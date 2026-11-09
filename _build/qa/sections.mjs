import { launch, SITE } from './cdp.mjs';
const [page, w, h, mobile] = process.argv.slice(2);
const cdp = await launch(9336);
try {
  await cdp.viewport(+w, +h, mobile === '1');
  await cdp.goto(SITE + page + '.html', 500);
  const r = await cdp.ev(`[...document.querySelectorAll('main > section, main > div')].map(s => {
    const bg = getComputedStyle(s).backgroundColor;
    const h = s.querySelector('h1,h2');
    return Math.round(s.getBoundingClientRect().top + scrollY) + '  ' + Math.round(s.getBoundingClientRect().height) + '  ' + bg + '  ' + (s.id ? '#' + s.id : '') + '  ' + (h ? h.textContent.trim().slice(0, 30) : s.className);
  })`);
  console.log(r.join('\n'));
} finally { await cdp.close(); }

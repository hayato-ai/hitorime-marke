import { launch, SITE } from './cdp.mjs';
const cdp = await launch(9352);
try {
  for (const w of [1200, 1280, 1366, 1440]) {
    await cdp.viewport(w, 800, false, 1);
    await cdp.goto(SITE + 'index.html', 600);
    const r = await cdp.ev(`(() => {
      const inner = document.querySelector('.site-header__inner');
      const cs = getComputedStyle(inner);
      const logo = document.querySelector('.logo'); const nav = document.querySelector('.site-nav ul'); const cta = document.querySelector('.header-cta'); const right = document.querySelector('.site-header__right');
      const links = [...document.querySelectorAll('.site-nav li:not(.nav-top) a')].map(a => Math.round(a.getBoundingClientRect().width));
      const names = [...document.querySelectorAll('.logo__name, .logo__sub')].map(e => ({ t: e.textContent.trim().slice(0, 6), w: Math.round(e.getBoundingClientRect().width), h: Math.round(e.getBoundingClientRect().height), sw: e.scrollWidth }));
      return { inner: Math.round(inner.getBoundingClientRect().width), innerPad: cs.paddingLeft, logo: Math.round(logo.getBoundingClientRect().width), logoH: Math.round(logo.getBoundingClientRect().height), nav: Math.round(nav.getBoundingClientRect().width), cta: Math.round(cta.getBoundingClientRect().width), right: Math.round(right.getBoundingClientRect().width), links, names, hdrH: Math.round(document.querySelector('.site-header').getBoundingClientRect().height) };
    })()`);
    console.log(w, JSON.stringify(r));
  }
} finally { await cdp.close(); }

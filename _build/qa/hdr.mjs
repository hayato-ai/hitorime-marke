// v14：ヘッダーの収まり（ナビを出す幅の実測）。ロゴ・ナビ・CTAが1行に収まり、各要素の間に余裕があるか
import { launch, SITE } from './cdp.mjs';
const cdp = await launch(9352);
try {
  for (const w of process.argv.slice(2).map(Number)) {
    await cdp.viewport(w, 800, false, 1);
    await cdp.goto(SITE + 'index.html', 500);
    const r = await cdp.ev(`(() => {
      const R = (e) => e.getBoundingClientRect();
      const inner = document.querySelector('.site-header__inner'); const cs = getComputedStyle(inner);
      const logo = R(document.querySelector('.logo')); const nav = document.querySelector('.site-nav'); const navShown = getComputedStyle(nav).display !== 'none';
      const ul = nav.querySelector('ul'); const cta = R(document.querySelector('.header-cta'));
      const ctaBtns = [...document.querySelectorAll('.header-cta .btn')].map((b) => { const r = R(b); return [Math.round(r.left), Math.round(r.right), Math.round(r.height)]; });
      const links = [...nav.querySelectorAll('a')].map((a) => { const r = R(a); return [Math.round(r.left), Math.round(r.right), Math.round(r.height)]; });
      const hdr = R(document.querySelector('.site-header'));
      const innerR = R(inner); const padR = parseFloat(cs.paddingRight);
      const navR = navShown ? R(ul) : null;
      return { vw: innerWidth, sw: document.documentElement.scrollWidth, hdrH: Math.round(hdr.height), logo: [Math.round(logo.left), Math.round(logo.right), Math.round(logo.height)], navShown, nav: navR && [Math.round(navR.left), Math.round(navR.right)], gapLogoNav: navR ? Math.round(navR.left - logo.right) : null, gapNavCta: navR ? Math.round(cta.left - navR.right) : null, cta: [Math.round(cta.left), Math.round(cta.right)], ctaBtns, links, innerRight: Math.round(innerR.right - padR), ctaRightSlack: Math.round(innerR.right - padR - cta.right), toggle: !!document.getElementById('nav-toggle'), wrapTops: new Set([...document.querySelectorAll('.logo, .site-nav a, .header-cta .btn')].filter((e) => R(e).width > 0).map((e) => Math.round(R(e).top + R(e).height / 2))).size };
    })()`);
    console.log(w, JSON.stringify(r));
  }
} finally { await cdp.close(); }

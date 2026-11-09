import { launch, SITE, sleep } from './cdp.mjs';

const pages = ['index', 'contact', 'download', 'privacy'];
const viewports = [
  [320, 568, true], [360, 740, true], [375, 812, true], [414, 896, true], [600, 900, true], [719, 900, true], [720, 900, true],
  [767, 1024, false], [768, 1024, false], [900, 800, false], [1024, 768, false],
  [959, 800, false], [960, 800, false], [1023, 800, false], [1024, 800, false], [1025, 800, false], [1100, 800, false], [1199, 800, false], [1200, 800, false], [1279, 800, false], [1280, 800, false], [1366, 800, false], [1440, 900, false],
];

const FNS = `
window.__q = {
  overflow() {
    const vw = innerWidth, bad = [];
    for (const el of document.body.querySelectorAll('*')) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      if (r.right > vw + 0.5 || r.left < -0.5) {
        const cls = (typeof el.className === 'string' && el.className) ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
        bad.push(el.tagName.toLowerCase() + cls + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + ']');
      }
    }
    const de = document.documentElement;
    return { vw, scrollW: de.scrollWidth, clientW: de.clientWidth, bodyScrollW: document.body.scrollWidth, count: bad.length, els: bad.slice(0, 8) };
  },
  cta() {
    const hdr = document.querySelector('.site-header');
    const hc = document.querySelector('.header-cta');
    const bar = document.querySelector('.cta-bar');
    const probe = (root) => [...root.querySelectorAll('a.btn')].map((a) => {
      const r = a.getBoundingClientRect(), cs = getComputedStyle(a);
      const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return {
        t: a.textContent.trim(), href: a.getAttribute('href'),
        shown: r.width > 0 && r.height > 0 && cs.visibility !== 'hidden',
        inVp: r.top >= -0.5 && r.bottom <= innerHeight + 0.5 && r.left >= -0.5 && r.right <= innerWidth + 0.5,
        hit: !!hit && (a === hit || a.contains(hit)),
        h: Math.round(r.height),
      };
    });
    return {
      hdrPos: getComputedStyle(hdr).position, hdrTop: Math.round(hdr.getBoundingClientRect().top * 10) / 10,
      hdrH: Math.round(hdr.getBoundingClientRect().height),
      hcDisp: getComputedStyle(hc).display, barDisp: getComputedStyle(bar).display,
      hc: probe(hc), bar: probe(bar),
      barBottom: Math.round(bar.getBoundingClientRect().bottom), vh: innerHeight,
    };
  },
  bottom() {
    const bar = document.querySelector('.cta-bar'), footer = document.querySelector('.site-footer'), c = document.querySelector('.copyright');
    const fr = footer.getBoundingClientRect(), cr = c.getBoundingClientRect(), br = bar.getBoundingClientRect();
    const barShown = getComputedStyle(bar).display !== 'none';
    const de = document.documentElement;
    return { atBottom: Math.abs(scrollY + innerHeight - de.scrollHeight) < 2, footerBottom: Math.round(fr.bottom), copyBottom: Math.round(cr.bottom), barTop: barShown ? Math.round(br.top) : null, vh: innerHeight, bodyPB: getComputedStyle(document.body).paddingBottom };
  },
  nav() {
    const n = document.querySelector('.site-nav');
    return { toggle: !!document.getElementById('nav-toggle') || !!document.querySelector('.nav-toggle, header button'), nav: getComputedStyle(n).display };
  },
  // ヘッダー：ロゴ・ナビ・CTA が1行（縦の中心がそろう）、文字が折り返さない、右端・左端からはみ出さない、要素どうしが重ならない
  header() {
    const R = (e) => e.getBoundingClientRect();
    const hdr = document.querySelector('.site-header'), inner = document.querySelector('.site-header__inner');
    const hr = R(hdr), ir = R(inner), cs = getComputedStyle(inner);
    const items = [];
    const push = (kind, e) => { const r = R(e); if (r.width > 0 && r.height > 0) items.push({ kind, l: r.left, r: r.right, t: r.top, b: r.bottom, cy: (r.top + r.bottom) / 2, h: r.height, el: e }); };
    push('logo', document.querySelector('.logo'));
    document.querySelectorAll('.site-nav li a').forEach((a) => push('nav', a));
    document.querySelectorAll('.header-cta a.btn').forEach((a) => push('cta', a));
    const mid = (hr.top + hr.bottom) / 2 - 0.5;   // 罫線 1px を除いた中心
    const offs = items.map((i) => Math.abs(i.cy - ((hr.top + hr.bottom - 1) / 2)));
    // 折り返し：ロゴの文字・ボタンの文字・ナビの文字が1行（文字の範囲の高さが font-size×2.2 未満）
    const wrap = [];
    items.forEach((i) => { const sp = i.el.querySelector('span:not(.btn__arrow):not(.logo__mark)'); const t = sp || i.el; const rg = document.createRange(); rg.selectNodeContents(t); const rh = rg.getBoundingClientRect().height; const fs = parseFloat(getComputedStyle(t).fontSize); if (rh > fs * 2.2) wrap.push(i.kind + ':' + Math.round(rh)); });
    // 重なり・間隔：グループの境目（ロゴ→ナビ、ナビ→CTA、CTA どうし）の隙間。ナビの項目どうしは、ボタンの形の枠（余白つき）なので除く
    const sorted = items.slice().sort((a, b) => a.l - b.l);
    let minGap = 1e9, overlap = false;
    for (let k = 1; k < sorted.length; k++) { const g = sorted[k].l - sorted[k - 1].r; if (g < -0.5) overlap = true; if (!(sorted[k].kind === 'nav' && sorted[k - 1].kind === 'nav')) minGap = Math.min(minGap, g); }
    const innerR = ir.right - parseFloat(cs.paddingRight), innerL = ir.left + parseFloat(cs.paddingLeft);
    const rightMost = Math.max(...items.map((i) => i.r)), leftMost = Math.min(...items.map((i) => i.l));
    const logo = items.find((i) => i.kind === 'logo'); const navs = items.filter((i) => i.kind === 'nav'); const ctas = items.filter((i) => i.kind === 'cta');
    return { hdrH: Math.round(hr.height), hdrPos: getComputedStyle(hdr).position, n: { logo: !!logo, nav: navs.length, cta: ctas.length }, maxOff: Math.round(Math.max(...offs) * 10) / 10, wrap, minGap: Math.round(minGap), overlap, outR: Math.round((rightMost - innerR) * 10) / 10, outL: Math.round((innerL - leftMost) * 10) / 10, navGapLogo: navs.length ? Math.round(navs[0].l - logo.r) : null, ctaVisible: ctas.map((c) => c.el.getAttribute('href')), scrollW: document.documentElement.scrollWidth, vw: innerWidth, navH: navs.length ? Math.max(...navs.map((n) => Math.round(n.h))) : null };
  },
  scrollTo(y) { scrollTo({ top: y, behavior: 'instant' }); return scrollY; },
  maxScroll() { return document.documentElement.scrollHeight - innerHeight; },
  revealLeft() { return document.querySelectorAll('.reveal:not(.is-visible), .reveal-group:not(.is-visible)').length; },
};
true;
`;

const results = [];
const headerRows = [];
const cdp = await launch(9333);
try {
  // フォントの読み込み状況（参考）
  await cdp.viewport(1280, 800, false);
  await cdp.goto(SITE + 'index.html');
  const fonts = await cdp.ev(`[...document.fonts].map(f => f.family + ' ' + f.weight + ':' + f.status).slice(0,8)`);
  console.log('fonts:', JSON.stringify(fonts));
  console.log('Noto Sans JP usable:', await cdp.ev(`document.fonts.check('16px "Noto Sans JP"')`));

  for (const [w, h, mobile] of viewports) {
    await cdp.viewport(w, h, mobile);
    for (const p of pages) {
      await cdp.goto(SITE + p + '.html', 500);
      await cdp.ev(FNS);
      const o = await cdp.ev(`__q.overflow()`);
      const max = await cdp.ev(`__q.maxScroll()`);
      const wantHeader = w >= 768;
      const issues = [];
      // スクロール位置ごとの CTA
      for (const f of [0, 0.2, 0.4, 0.6, 0.8, 1]) {
        await cdp.ev(`__q.scrollTo(${Math.round(max * f)})`);
        await sleep(wantHeader ? 60 : 380);
        const c = await cdp.ev(`__q.cta()`);
        const all = wantHeader ? c.hc : c.bar;
        // 反対側：≥768 では下部バーが出ていないこと。<768 ではヘッダーの小さな主ボタン（無料相談）だけが出てよい（資料請求は出ない）
        const other = wantHeader ? c.bar : c.hc.filter((b) => b.href !== 'contact.html');
        // そのページ自身へのボタン（contact / download）は隠れていてよい
        const self = p === 'contact' ? 'contact.html' : p === 'download' ? 'download.html' : null;
        const set = all.filter((b) => b.href !== self);
        const exp = ['contact.html', 'download.html'].filter((h) => h !== self);
        if (all.length !== 2) issues.push(`f=${f}: CTA数=${all.length}`);
        if (!wantHeader) { const hp = c.hc.find((b) => b.href === 'contact.html'); const hg = c.hc.find((b) => b.href === 'download.html'); if (p !== 'contact' && !(hp && hp.shown && hp.inVp && hp.hit)) issues.push(`f=${f}: <768 のヘッダーに小さな主ボタン（無料相談）が出ていない ${JSON.stringify(hp)}`); if (hg && hg.shown) issues.push(`f=${f}: <768 のヘッダーに資料請求が出ている`); }
        if (self && all.find((b) => b.href === self)?.shown) issues.push(`f=${f}: 自ページへのボタンが表示されている`);
        // index のスマホ：FV のボタンが見えている間は下部バーが隠れてよい（その代わり FV のボタンが画面内にある）
        // スマホ：CTA のボタン行（FV・途中の白の行）が画面に見えている間は下部バーが隠れてよい（その代わりそのボタンが画面内で押せる）
        const ROWS = `[...document.querySelectorAll('.hero .btn-row, .plans-cta .btn-row, .cta-row .btn-row, .cta-band .btn-row')]`;
        const fv = !wantHeader && p !== 'privacy' ? await cdp.ev(`(() => !!document.querySelector('.cta-bar.is-hidden'))()`) : false;
        if (!fv) {
          for (const b of set) {
            if (!b.shown || !b.inVp || !b.hit) issues.push(`f=${f}: ${b.t} shown=${b.shown} inVp=${b.inVp} hit=${b.hit}`);
          }
          // バーが出ているのに、ボタン行が半分以上見えている（＝本来は隠れるはず）状態でないこと
          if (!wantHeader) {
            const should = await cdp.ev(`${ROWS}.some((r) => { const b = r.getBoundingClientRect(); const v = Math.max(0, Math.min(b.bottom, innerHeight) - Math.max(b.top, 70)) / b.height; return v >= 0.55; })`);
            if (should) issues.push(`f=${f}: ボタン行が見えているのにバーが隠れていない`);
          }
        } else {
          // 隠れているときは、見えているボタン行の中に、全体が画面内で押せるボタンが1つ以上あること
          const vis = await cdp.ev(`${ROWS}.flatMap((r) => [...r.querySelectorAll('.btn')]).filter((a) => { const r = a.getBoundingClientRect(); if (r.bottom <= 70 || r.top >= innerHeight) return false; const hit = document.elementFromPoint(r.left + r.width / 2, Math.min(Math.max(r.top + r.height / 2, 1), innerHeight - 1)); return r.top >= 69 && r.bottom <= innerHeight && !!hit && (hit === a || a.contains(hit)); }).length`);
          if (vis < 1) issues.push(`f=${f}: バー非表示中なのに押せるCTAのボタンが画面内にない`);
        }
        if (other.some((b) => b.shown)) issues.push(`f=${f}: 反対側のCTAも表示されている`);
        if (wantHeader && (c.hdrPos !== 'sticky' || Math.abs(c.hdrTop) > 0.6)) issues.push(`f=${f}: ヘッダー pos=${c.hdrPos} top=${c.hdrTop}`);
        if (!wantHeader && !fv && (c.barBottom !== c.vh)) issues.push(`f=${f}: バー下端=${c.barBottom} vh=${c.vh}`);
        if (set.length && JSON.stringify(set.map((s) => s.href)) !== JSON.stringify(exp)) issues.push(`href違い ${set.map(s=>s.href)}`);
        if (!wantHeader && f === 0 && c.hdrPos === 'static') issues.push('(info) 低い横向きでヘッダー非固定');
      }
      // 最下部：フッターがバーに隠れない
      await cdp.ev(`__q.scrollTo(${max})`);
      await sleep(80);
      const b = await cdp.ev(`__q.bottom()`);
      if (!b.atBottom) issues.push(`最下部に届いていない ${JSON.stringify(b)}`);
      if (b.barTop !== null && b.footerBottom > b.barTop + 1) issues.push(`フッター下端 ${b.footerBottom} > バー上端 ${b.barTop}`);
      if (b.barTop !== null && b.copyBottom > b.barTop) issues.push(`©行 ${b.copyBottom} > バー上端 ${b.barTop}`);
      // ナビ：トグルが無いこと。1024px以上でナビが横に出る。それ未満は出ない。ヘッダーは常に1行で崩れない
      const nv = await cdp.ev(`__q.nav()`);
      if (nv.toggle) issues.push('開閉メニューのボタンがある');
      const wantNav = w >= 1024;
      if ((nv.nav !== 'none') !== wantNav) issues.push(`ナビの表示が想定と違う ${JSON.stringify(nv)}（${wantNav ? '出る' : '出さない'}はず）`);
      await cdp.ev(`__q.scrollTo(0)`);
      const hd = await cdp.ev(`__q.header()`);
      if (hd.maxOff > 2) issues.push(`ヘッダーが1行でない（縦の中心のずれ ${hd.maxOff}px）`);
      if (hd.wrap.length) issues.push('ヘッダーの文字が折り返している ' + hd.wrap);
      if (hd.overlap || hd.minGap < 8) issues.push(`ヘッダーの要素が重なる／近すぎる（最小の隙間 ${hd.minGap}px）`);
      if (hd.outR > 0.5 || hd.outL > 0.5) issues.push(`ヘッダーの要素が左右からはみ出す R=${hd.outR} L=${hd.outL}`);
      if (hd.scrollW > hd.vw) issues.push('ヘッダーで横スクロール');
      if (wantNav && (hd.n.nav !== 5 || hd.navGapLogo < 16)) issues.push(`ナビの項目数／ロゴとの間隔 ${hd.n.nav} / ${hd.navGapLogo}`);
      if (!wantNav && hd.n.nav !== 0) issues.push('ナビが出ている');
      const hdrExp = w >= 768 ? 77 : 69;
      if (!(hd.hdrH === hdrExp) && !(w < 768 && h <= 480)) issues.push(`ヘッダーの高さ ${hd.hdrH}（想定 ${hdrExp}）`);
      if (p === 'index') { const exp = w >= 768 ? ['contact.html', 'download.html'] : ['contact.html']; if (JSON.stringify(hd.ctaVisible) !== JSON.stringify(exp)) issues.push(`ヘッダーのCTA ${hd.ctaVisible}（想定 ${exp}）`); }
      headerRows.push(`${w}:${hd.minGap}/${hd.maxOff}`);
      // 横スクロール（モバイル表示では、はみ出しがあるとレイアウト幅 innerWidth が広がるので、指定幅との一致も見る）
      if (o.vw !== w) issues.push(`レイアウト幅が指定幅と違う innerWidth=${o.vw} w=${w}`);
      if (o.count > 0 || o.scrollW > o.vw) issues.push(`横はみ出し scrollW=${o.scrollW} vw=${o.vw} els=${o.els.join(' | ')}`);
      results.push({ w, p, issues, o });
      console.log(`${String(w).padStart(4)} ${p.padEnd(9)} ${issues.length ? 'NG' : 'ok'}  scrollW=${o.scrollW}/${o.vw}  H=${await cdp.ev('document.documentElement.scrollHeight')}` + (issues.length ? '\n      - ' + issues.join('\n      - ') : ''));
    }
  }
} finally {
  await cdp.close();
}
const ng = results.filter((r) => r.issues.some((i) => !i.startsWith('(info)')));
console.log(`\n==== ${results.length} 件中 NG ${ng.length} 件 ====`);
console.log('header minGap/maxOff by width (index+others):', [...new Set(headerRows)].join(' '));

// v14：新しい部品の収まり（320〜1440px）。吹き出しとボタンの左端、プランの横3列（高さ・段・料金の下端）、注記、担当者のチェックリスト・経歴の流れ、フッター
import { launch, SITE, SP, sleep } from './cdp.mjs';
const cdp = await launch(9349);
let bad = 0;
const PROBE = `(() => {
  const R = (e) => e.getBoundingClientRect();
  const out = { vw: innerWidth, sw: document.documentElement.scrollWidth, bubbles: [], works: null, flow: null, cards: [], notes: null, photo: null, tag: null, feat: [], footer: null };
  // 吹き出し：主ボタンの左端にそろう、ボタンのすぐ上（隙間 4〜16px）、画面内
  document.querySelectorAll('.bubble').forEach((b) => {
    const row = b.nextElementSibling; const btn = row.querySelector('a.btn'); const br = R(b), tr = R(btn);
    out.bubbles.push({ where: (b.closest('section') || b.closest('.plans-cta')).className.split(' ')[0], left: Math.round(br.left), btnLeft: Math.round(tr.left), gap: Math.round(tr.top - br.bottom), right: Math.round(br.right), h: Math.round(br.height), vw: innerWidth });
  });
  const wl = document.querySelector('.about .check-list');
  if (wl) { const wr = R(wl.parentElement); out.works = { n: wl.children.length, over: [...wl.querySelectorAll('li')].filter((li) => R(li).right > wr.right + 0.5).length, title: !!document.querySelector('.about .works-title'), lines: [...wl.querySelectorAll('li > span')].map((sp) => Math.round(R(sp).height / parseFloat(getComputedStyle(sp).lineHeight))) }; }
  const fl = document.querySelector('.career-flow');
  if (fl) { const lis = [...fl.children]; out.flow = { dir: getComputedStyle(fl).flexDirection, n: lis.length, tops: lis.map((l) => Math.round(R(l).top)), rights: lis.map((l) => Math.round(R(l).right)), clip: lis.map((l) => { const sp = l.firstElementChild; return R(sp).right > R(l).right - 2 || R(sp).left < R(l).left + 2; }), hs: lis.map((l) => Math.round(R(l).height)), parentRight: Math.round(R(fl.parentElement).right) }; }
  document.querySelectorAll('.plan-card').forEach((c) => {
    const cr = R(c); const kids = [...c.querySelectorAll('h3, p, li, .plan-price span, .k-label, s')];
    const over = kids.filter((k) => { const r = R(k); return r.width > 0 && r.right > cr.right - 1; }).length;
    const bt = c.querySelector('.plan-card__bottom'); const b = R(bt);
    const h3 = c.querySelector('h3'); const lead = c.querySelector('.plan-card__lead'); const price = c.querySelector('.plan-price'); const amt = c.querySelector('.plan-price__amt');
    const pr = R(price); const ar = R(amt);
    const rng = document.createRange(); rng.selectNodeContents(h3); const h3r = rng.getBoundingClientRect();
    out.cards.push({ id: c.id, w: Math.round(cr.width), h: Math.round(cr.height), top: Math.round(cr.top), bottom: Math.round(cr.bottom), over,
      bottomFlush: Math.abs(b.bottom - (cr.bottom - 2)) < 2.5, bandTop: Math.round(b.top), bandBottom: Math.round(b.bottom), bandL: Math.round(b.left - cr.left), bandR: Math.round(cr.right - b.right),
      h3lines: Math.round(h3r.height / parseFloat(getComputedStyle(h3).fontSize) / 1.4 * 10) / 10, h3fs: getComputedStyle(h3).fontSize, leadLines: Math.round(R(lead).height / parseFloat(getComputedStyle(lead).lineHeight)),
      amtIn: ar.right <= b.right - 4 + 0.5, tag: c.querySelector('.plan-card__tag') ? Math.round(R(c.querySelector('.plan-card__tag')).right) : null,
      labels: [...c.querySelectorAll('.k-label')].map((l) => Math.round(R(l).top)), cols: getComputedStyle(c.parentElement).gridTemplateColumns.split(' ').length,
      sections: [...c.querySelectorAll('.plan-card__sec')].map((e) => Math.round(R(e).top)), subgrid: getComputedStyle(c).gridTemplateRows !== 'none' && getComputedStyle(c).display === 'grid' });
  });
  const nt = document.querySelector('.plan-notes'); if (nt) { out.notes = { n: nt.children.length, lines: [...nt.children].map((li) => Math.round(R(li).height / parseFloat(getComputedStyle(li).lineHeight))), right: Math.round(R(nt).right), fs: getComputedStyle(nt.firstElementChild).fontSize }; }
  const ph = document.querySelector('.about .ph'); if (ph) { const r = R(ph); out.photo = { ratio: Math.round(r.width / r.height * 100) / 100, w: Math.round(r.width) }; }
  const rt = document.querySelector('.about .role-tag span'); if (rt) out.tag = { right: Math.round(R(rt).right), parent: Math.round(R(rt.parentElement).right), lines: Math.round(R(rt).height / 24) };
  document.querySelectorAll('.feat-card').forEach((c) => { const h = c.querySelector('h3'); out.feat.push({ top: Math.round(R(c.querySelector('p')).top - R(c).top), h: Math.round(R(c).height), h3h: Math.round(R(h).height) }); });
  const ft = document.querySelector('.site-footer');
  if (ft) {
    const cols = [...ft.querySelectorAll('.footer__brand, .footer__col')].map((e) => R(e));
    const links = [...ft.querySelectorAll('a')].map((a) => R(a)); const lg = ft.querySelector('.logo');
    out.footer = { cols: cols.map((r) => [Math.round(r.left), Math.round(r.right), Math.round(r.top)]), sameRow: new Set(cols.map((r) => Math.round(r.top))).size === 1, minLinkH: Math.round(Math.min(...links.map((r) => r.height))), over: links.filter((r) => r.right > innerWidth + 0.5 || r.left < -0.5).length, logoBg: getComputedStyle(lg).backgroundColor, bg: getComputedStyle(ft).backgroundColor,
      bottom: [...ft.querySelectorAll('.footer__bottom > *')].map((e) => { const r = R(e); return [Math.round(r.left), Math.round(r.right), Math.round((r.top + r.bottom) / 2)]; }), h: Math.round(R(ft).height), headCount: ft.querySelectorAll('.footer__h').length };
  }
  return out;
})()`;
try {
  for (const [w, h, m] of [[320, 568, true], [360, 740, true], [375, 812, true], [414, 896, true], [480, 800, true], [600, 900, true], [639, 900, true], [640, 900, false], [719, 900, true], [768, 1024, false], [899, 800, false], [900, 800, false], [959, 800, false], [960, 800, false], [1023, 800, false], [1024, 800, false], [1025, 800, false], [1100, 800, false], [1199, 800, false], [1280, 800, false], [1440, 900, false]]) {
    await cdp.viewport(w, h, m);
    await cdp.goto(SITE + 'index.html', 500);
    await cdp.ev(`document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-visible')); true`);
    await sleep(500);
    const o = await cdp.ev(PROBE);
    const issues = [];
    if (o.sw > o.vw) issues.push('横はみ出し scrollW=' + o.sw);
    if (o.bubbles.length !== 4) issues.push('吹き出しが4つでない ' + o.bubbles.length);
    for (const b of o.bubbles) {
      if (Math.abs(b.left - b.btnLeft) > 1) issues.push(`吹き出し(${b.where})の左端が主ボタンと違う ${b.left}/${b.btnLeft}`);
      if (b.gap < 4 || b.gap > 18) issues.push(`吹き出し(${b.where})とボタンの隙間 ${b.gap}px`);
      if (b.right > b.vw - 8) issues.push(`吹き出し(${b.where})が画面端に寄りすぎ right=${b.right}`);
      if (b.h > 40) issues.push(`吹き出し(${b.where})が2行に折り返している h=${b.h}`);
    }
    if (!o.works || o.works.n !== 3 || o.works.over || !o.works.title) issues.push('これまで取り組んできたこと：3項目・はみ出しなし・見出しあり ' + JSON.stringify(o.works));
    if (o.works && w >= 768 && o.works.lines.some((x) => x > 2)) issues.push('1文が3行以上（v14：太字の見出し＋1文。1文は2行まで） ' + o.works.lines);
    if (o.flow) {
      const rowMode = w >= 640;
      if ((o.flow.dir === 'row') !== rowMode) issues.push('経歴の流れの向きが想定と違う ' + o.flow.dir);
      if (rowMode && new Set(o.flow.tops).size !== 1) issues.push('経歴の流れが折り返している ' + o.flow.tops);
      if (!rowMode && new Set(o.flow.tops).size !== o.flow.n) issues.push('経歴の流れが縦に並んでいない');
      if (o.flow.rights.some((r) => r > o.flow.parentRight + 0.5)) issues.push('経歴の流れが親からはみ出す ' + o.flow.rights + ' parent=' + o.flow.parentRight);
      if (o.flow.clip.some(Boolean)) issues.push('経歴の流れの文字が箱からはみ出す');
      if (rowMode && o.flow.hs.some((x) => x > 70)) issues.push('経歴の流れの箱が高すぎる（3行以上）' + o.flow.hs);
    }
    // プラン：3枚、1024px以上で3列（高さ・段・料金の帯の上端と下端がそろう）、それ未満は1列
    const colsExp = w >= 1024 ? 3 : 1;
    if (o.cards.length !== 3 || o.cards.some((c) => c.cols !== colsExp)) issues.push(`プランの列数が想定（${colsExp}列）と違う ${o.cards.map((c) => c.cols)}`);
    for (const c of o.cards) {
      if (c.over) issues.push(`${c.id}: カードの右端からはみ出す要素 ${c.over}`);
      if (!c.bottomFlush) issues.push(`${c.id}: 料金の帯がカード下端いっぱいでない`);
      if (c.bandL !== 2 && c.bandL !== 1 || c.bandR < 1 || c.bandR > 3) issues.push(`${c.id}: 料金の帯が左右いっぱいでない L=${c.bandL} R=${c.bandR}`);
      if (!c.amtIn) issues.push(`${c.id}: 料金の金額が帯からはみ出す`);
      if (w >= 360 && c.h3lines > 1.2) issues.push(`${c.id}: プラン名が折り返している ${c.h3lines}行 fs=${c.h3fs}`);
    }
    if (colsExp === 3) {
      const hs = new Set(o.cards.map((c) => c.h)), tops = new Set(o.cards.map((c) => c.top)), bands = new Set(o.cards.map((c) => c.bandTop)), bb = new Set(o.cards.map((c) => c.bandBottom));
      if (hs.size !== 1) issues.push('3枚の高さがそろっていない ' + o.cards.map((c) => c.h));
      if (tops.size !== 1) issues.push('3枚の上端がそろっていない');
      if (bands.size !== 1 || bb.size !== 1) issues.push(`料金の帯の上端／下端がそろっていない top=${o.cards.map((c) => c.bandTop)} bottom=${o.cards.map((c) => c.bandBottom)}`);
      for (let k = 0; k < 3; k++) if (new Set(o.cards.map((c) => c.labels[k])).size !== 1) issues.push(`各段のラベルの位置（${k + 1}番目）が3枚でそろっていない ${o.cards.map((c) => c.labels[k])}`);
      if (!o.cards.every((c) => c.subgrid)) issues.push('subgrid が効いていない');
    }
    if (!o.notes || o.notes.n !== 3 || o.notes.lines.some((x) => x > 2 && w >= 375)) issues.push('プランの注記（3行）' + JSON.stringify(o.notes));
    if (o.notes && o.notes.right > o.vw) issues.push('注記がはみ出す');
    if (o.photo) { const exp = w >= 960 ? 0.8 : 1.6; if (Math.abs(o.photo.ratio - exp) > 0.05) issues.push(`担当者の写真の比率 ${o.photo.ratio}（想定 ${exp}）`); }
    if (o.tag && (o.tag.right > o.tag.parent + 0.5 || o.tag.lines > 1)) issues.push('肩書きのタグが折り返す／はみ出す ' + JSON.stringify(o.tag));
    if (w >= 960 && new Set(o.feat.map((f) => f.top)).size !== 1) issues.push('特長3つの本文の開始位置がそろっていない ' + o.feat.map((f) => f.top));
    // フッター：768px以上は3列が同じ高さから並ぶ、それ未満は縦積み。リンクは44px以上、紺の地、ロゴは白の10%の透明
    const f = o.footer;
    if (!f) issues.push('フッターがない');
    else {
      if (f.headCount !== 2) issues.push('フッターの見出しが2つでない');
      if (w >= 768 && !(f.sameRow && f.cols.length === 3)) issues.push('フッターが3列で並んでいない ' + JSON.stringify(f.cols));
      if (w < 768 && new Set(f.cols.map((c) => c[2])).size !== 3) issues.push('フッターが縦積みでない ' + JSON.stringify(f.cols));
      if (f.minLinkH < 44) issues.push('フッターのリンクの高さが44px未満 ' + f.minLinkH);
      if (f.over) issues.push('フッターのリンクが画面外 ' + f.over);
      if (f.bg !== 'rgb(18, 27, 58)') issues.push('フッターの地が --navy-deep でない ' + f.bg);
      if (!/rgba\(255, 255, 255, 0\.1\)/.test(f.logoBg)) issues.push('フッターのロゴが白の10%の透明でない ' + f.logoBg);
      if (f.bottom.length !== 2 || (w >= 400 && Math.abs(f.bottom[0][2] - f.bottom[1][2]) > 3)) issues.push('フッターの最下段（プライバシーポリシー／©）が1行でない ' + JSON.stringify(f.bottom));
    }
    if (issues.length) bad++;
    console.log(`${String(w).padStart(4)} ${issues.length ? 'NG' : 'ok'}  cards=${o.cards.map((c) => c.w + 'x' + c.h)} h3=${o.cards[0]?.h3fs} footerH=${f?.h} photo=${o.photo?.ratio}` + (issues.length ? '\n      - ' + issues.join('\n      - ') : ''));
  }
} finally { await cdp.close(); }
console.log(bad ? 'NG ' + bad : 'fit all ok');

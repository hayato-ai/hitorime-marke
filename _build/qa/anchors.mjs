import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9337);
const measure = (id) => `(() => {
  const t = document.getElementById('${id}'); const r = t.getBoundingClientRect();
  const hdr = document.querySelector('.site-header').getBoundingClientRect();
  const bar = document.querySelector('.cta-bar'); const barShown = getComputedStyle(bar).display !== 'none';
  return { top: Math.round(r.top), bottom: Math.round(r.bottom), hdrBottom: Math.round(hdr.bottom), barTop: barShown ? Math.round(bar.getBoundingClientRect().top) : null, vh: innerHeight, scrollY: Math.round(scrollY), max: Math.round(document.documentElement.scrollHeight - innerHeight) };
})()`;
let bad = 0;
try {
  for (const [w, h, mobile] of [[375, 812, true], [768, 1024, false], [1023, 800, false], [1024, 800, false], [1280, 800, false], [1440, 900, false]]) {
    await cdp.viewport(w, h, mobile);
    for (const [url, id] of [['contact.html#other', 'other'], ['index.html#service', 'service'], ['index.html#plans', 'plans'], ['index.html#plan-1', 'plan-1'], ['index.html#plan-3', 'plan-3'], ['index.html#about', 'about'], ['index.html#flow', 'flow'], ['index.html#faq', 'faq']]) {
      // 1) URL に直接
      await cdp.goto(SITE + url, 1500);
      let m = await cdp.ev(measure(id));
      const okTop = m.top >= m.hdrBottom - 1 && m.top < m.vh - 60;
      const okBar = m.barTop === null || m.bottom <= m.barTop + 1 || m.top < m.barTop - 60;
      console.log(`${String(w).padStart(4)} direct ${url.padEnd(20)} top=${m.top} hdrBottom=${m.hdrBottom} barTop=${m.barTop} scroll=${m.scrollY}/${m.max} ${okTop && okBar ? 'ok' : 'NG'}`);
      if (!(okTop && okBar)) bad++;
    }
    // 2) 実際のリンクをクリック：フッターの小リンク（その他のお問い合わせ）、ナビ／フッターの「サイト内」（プロフィール → index の各セクションへ）
    await cdp.goto(SITE + 'index.html', 800);
    await cdp.ev(`[...document.querySelectorAll('.site-footer a')].find(a => a.textContent.includes('その他のお問い合わせ')).click(); true`);
    await sleep(1500);
    let url = await cdp.ev('location.href');
    console.log(`${String(w).padStart(4)} click footer link → ${url.replace(SITE, '')}`);
    if (!/contact\.html#other$/.test(url)) bad++;
    for (const [label, id] of [['サービスの特長', 'service'], ['プラン', 'plans'], ['ご支援の流れ', 'flow'], ['よくある質問', 'faq']]) {
      // ヘッダーのナビ（1024px以上だけ出る）
      if (w >= 1024) {
        await cdp.goto(SITE + 'profile.html', 800);
        await cdp.ev(`[...document.querySelectorAll('.site-nav a')].find(a => a.textContent.trim() === ${JSON.stringify(label)}).click(); true`);
        await sleep(1800);
        url = await cdp.ev('location.href');
        const m2 = await cdp.ev(measure(id));
        const okc = new RegExp('(index\\.html)?#' + id + '$').test(url) && m2.top >= m2.hdrBottom - 1 && m2.top < m2.vh - 60;
        console.log(`${String(w).padStart(4)} click header nav ${label} → ${url.replace(SITE, '')} top=${m2.top} hdrBottom=${m2.hdrBottom} ${okc ? 'ok' : 'NG'}`);
        if (!okc) bad++;
      }
      // フッターの「サイト内」（全幅）
      await cdp.goto(SITE + 'profile.html', 800);
      await cdp.ev(`[...document.querySelectorAll('.site-footer .footer__col:nth-of-type(1) a, .site-footer nav a')].find(a => a.textContent.trim() === ${JSON.stringify(label)}).click(); true`);
      await sleep(1800);
      url = await cdp.ev('location.href');
      const m3 = await cdp.ev(measure(id));
      const okf = new RegExp('(index\\.html)?#' + id + '$').test(url) && m3.top >= m3.hdrBottom - 1 && m3.top < m3.vh - 60;
      console.log(`${String(w).padStart(4)} click footer nav ${label} → ${url.replace(SITE, '')} top=${m3.top} hdrBottom=${m3.hdrBottom} ${okf ? 'ok' : 'NG'}`);
      if (!okf) bad++;
    }
    // フッターの TOP・ロゴ・プロフィール・お問い合わせ・プライバシー
    for (const [txt, re] of [['TOP', /\/(index\.html)?$/], ['無料相談', /contact\.html$/], ['サービス資料のダウンロード', /download\.html$/], ['プライバシーポリシー', /privacy\.html$/], ['プロフィール', /profile\.html$/]]) {
      await cdp.goto(SITE + 'contact.html', 600);
      await cdp.ev(`[...document.querySelectorAll('.site-footer a')].find(a => a.textContent.trim() === ${JSON.stringify(txt)}).click(); true`);
      await sleep(900);
      url = await cdp.ev('location.href');
      const okl = re.test(url);
      if (!okl) { bad++; console.log(`${String(w).padStart(4)} click footer ${txt} → ${url.replace(SITE, '')} NG`); }
    }
    // ヘッダーのメニューは無い：トグルが無いこと
    const hasToggle = await cdp.ev(`!!document.getElementById('nav-toggle') || !!document.querySelector('header button')`);
    if (hasToggle) { bad++; console.log(`${String(w).padStart(4)} NG toggle が残っている`); }
  }
} finally { await cdp.close(); }
console.log(bad ? `NG ${bad}` : 'anchors all ok');

// v14：フォーム（FV の資料請求・contact・download）の検証。必須の未入力のその場のエラー表示、メールの形式、設定が空のときの注記（fetch しない）、
// 設定ありのときの HubSpot Forms API への POST（fetch を差し替えて確認：URL・フィールド名・本文）、成功時の置き換え、失敗時のエラー＋メール、横スクロールなし。320〜1440。
import { launch, SITE, sleep } from './cdp.mjs';
const cdp = await launch(9361);
let fails = 0;
const NG = (...a) => { fails++; console.log('  [NG]', ...a); };
const VPS = [[320, 568, true], [375, 812, true], [768, 1024, false], [1024, 768, false], [1440, 900, false]];
const TARGETS = [
  { page: 'index', root: '#hero-form', kind: 'download', pfx: 'hf', consult: false, label: '資料を受け取る' },
  { page: 'contact', root: '#form-frame', kind: 'consult', pfx: 'cf', consult: true, label: '無料相談を申し込む' },
  { page: 'download', root: '#form-frame', kind: 'download', pfx: 'df', consult: false, label: '資料を受け取る' },
];
const NAVY = 'rgb(28, 42, 85)';
try {
  for (const [w, h, mobile] of VPS) {
    await cdp.viewport(w, h, mobile, 1);
    for (const t of TARGETS) {
      const tag = `${t.page}@${w}`;
      await cdp.goto(SITE + t.page + '.html', 900);
      await cdp.ev(`document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-visible')); true`);
      const R = (s) => `document.querySelector('${t.root}').querySelector(${JSON.stringify(s)})`;
      // 0. 構造
      const st = await cdp.ev(`(() => { const f = ${R('form.lead-form')}; return { n: f.querySelectorAll('input,select,textarea').length, btn: f.querySelector('button[type=submit]').textContent.trim(), note: f.querySelector('.lead-form__note').hidden, fail: f.querySelector('.lead-form__fail').hidden, micro: f.querySelector('.lead-form__micro').textContent.trim(), link: f.querySelector('a[href="privacy.html"]') ? 1 : 0 }; })()`);
      if (st.btn !== t.label) NG(tag, 'ボタン文言', st.btn);
      if (!st.note || !st.fail) NG(tag, '最初から注記／失敗の文が出ている');
      if (st.micro !== '入力は1分ほどで完了します。') NG(tag, 'micro', st.micro);
      if (!st.link) NG(tag, 'プライバシーポリシーへのリンクがない');
      if (st.n !== (t.consult ? 7 : 5)) NG(tag, '入力欄の数', st.n);
      // 1. 空のまま送信 → 必須に「入力してください」、任意には出ない
      await cdp.ev(`${R('button[type=submit]')}.click(); true`);
      await sleep(150);
      const e1 = await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const out = {}; for (const fd of f.querySelectorAll('.field')) { const e = fd.querySelector('.field__err'); const c = fd.querySelector('input,select,textarea'); const cs = getComputedStyle(e); out[fd.dataset.field] = { shown: !e.hidden && cs.display !== 'none', text: e.textContent.trim(), color: cs.color, weight: cs.fontWeight, inv: c.getAttribute('aria-invalid') }; } return { out, active: document.activeElement && document.activeElement.name, note: f.querySelector('.lead-form__note').hidden }; })()`);
      for (const n of ['company', 'firstname', 'email']) {
        const o = e1.out[n];
        if (!o.shown || o.text !== '入力してください') NG(tag, n, '必須の未入力のエラーが出ない', JSON.stringify(o));
        if (o.color !== NAVY || +o.weight < 700) NG(tag, n, 'エラーの色／太さが 紺・太字 でない', o.color, o.weight);
        if (o.inv !== 'true') NG(tag, n, 'aria-invalid がない');
        if (/⚠|!|！/.test(o.text)) NG(tag, n, '⚠／感嘆符');
      }
      if (!e1.out.privacy.shown || !e1.out.privacy.text) NG(tag, '同意のエラーが出ない');
      if (e1.out.phone.shown) NG(tag, '任意の電話にエラーが出ている');
      if (t.consult && (e1.out.message.shown || e1.out.consult_type.shown)) NG(tag, '任意の項目にエラーが出ている');
      if (e1.active !== 'company') NG(tag, '最初の未入力の欄にフォーカスが移らない', e1.active);
      if (!e1.note) NG(tag, '検証エラーのときに「設定前」の注記が出ている');
      // 2. メールの形式
      await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const set = (n, v) => { const c = f.querySelector('[name=' + n + ']'); c.value = v; c.dispatchEvent(new Event('input', { bubbles: true })); }; set('company', 'テスト株式会社'); set('firstname', 'テスト 太郎'); set('email', 'abc'); f.querySelector('#${t.pfx}-privacy').click(); const b = f.querySelector('button[type=submit]'); b.click(); })(); true`);
      await sleep(120);
      const e2 = await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const fe = (n) => { const e = f.querySelector('[data-field=' + n + '] .field__err'); return { shown: !e.hidden, text: e.textContent.trim() }; }; return { company: fe('company'), email: fe('email'), privacy: fe('privacy') }; })()`);
      if (e2.company.shown || e2.privacy.shown) NG(tag, '入力した欄／チェックのエラーが消えない', JSON.stringify(e2));
      if (!e2.email.shown || !e2.email.text.includes('形式')) NG(tag, 'メールの形式エラーが出ない', JSON.stringify(e2.email));
      // 直すとその場で消える
      await cdp.ev(`(() => { const c = ${R('[name=email]')}; c.value = 'taro@example.com'; c.dispatchEvent(new Event('input', { bubbles: true })); })(); true`);
      await sleep(80);
      const e3 = await cdp.ev(`!${R('[data-field=email] .field__err')}.hidden`);
      if (e3) NG(tag, '直してもエラーが消えない');
      // 3. 設定が空：送信しない（fetch が呼ばれない）、注記が出る
      await cdp.ev(`window.__calls = []; window.fetch = (u, o) => { window.__calls.push({ u: String(u), b: o && o.body }); return Promise.resolve({ ok: true, status: 200 }); }; true`);
      if (t.consult) await cdp.ev(`(() => { const f = ${R('form.lead-form')}; f.querySelector('[name=consult_type]').value = 'スポットプラン'; f.querySelector('[name=message]').value = '相談です'; })(); true`);
      await cdp.ev(`${R('[name=phone]')}.value = '03-1234-5678'; ${R('button[type=submit]')}.click(); true`);
      await sleep(250);
      const e4 = await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const n = f.querySelector('.lead-form__note'); return { calls: window.__calls.length, note: !n.hidden, text: n.textContent.trim(), formShown: !f.hidden, done: !f.parentNode.querySelector('.lead-form__done').hidden }; })()`);
      if (e4.calls !== 0) NG(tag, '設定が空なのに送信（fetch）された', e4.calls);
      if (!e4.note || e4.text !== '（設定前のため送信されません）') NG(tag, '設定前の注記が出ない', JSON.stringify(e4));
      if (!e4.formShown || e4.done) NG(tag, '設定前なのにフォームが置き換わった');
      // 4. 設定あり：POST の中身
      await cdp.ev(`window.HUBSPOT_PORTAL_ID = '12345'; window.HUBSPOT_FORM_DOWNLOAD = 'aaaa-dl'; window.HUBSPOT_FORM_CONSULT = 'bbbb-co'; ${R('button[type=submit]')}.click(); true`);
      await sleep(400);
      const e5 = await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const d = f.parentNode.querySelector('.lead-form__done'); return { calls: window.__calls, formHidden: f.hidden, doneShown: !d.hidden, doneText: d.textContent.trim(), focus: document.activeElement === d }; })()`);
      if (e5.calls.length !== 1) NG(tag, 'POST が1回でない', e5.calls.length);
      else {
        const c = e5.calls[0];
        const guid = t.kind === 'consult' ? 'bbbb-co' : 'aaaa-dl';
        if (c.u !== `https://api.hsforms.com/submissions/v3/integration/submit/12345/${guid}`) NG(tag, 'URL', c.u);
        const b = JSON.parse(c.b);
        const names = b.fields.map((x) => x.name).join(',');
        const exp = t.consult ? 'company,firstname,email,phone,consult_type,message' : 'company,firstname,email,phone';
        if (names !== exp) NG(tag, 'フィールド名', names);
        const fv = Object.fromEntries(b.fields.map((x) => [x.name, x.value]));
        if (fv.firstname !== 'テスト 太郎' || fv.company !== 'テスト株式会社' || fv.email !== 'taro@example.com' || fv.phone !== '03-1234-5678') NG(tag, '値', JSON.stringify(fv));
        if (t.consult && (fv.consult_type !== 'スポットプラン' || fv.message !== '相談です')) NG(tag, '相談の値', JSON.stringify(fv));
        if (!b.context || !b.legalConsentOptions) NG(tag, 'context／同意の情報がない');
      }
      if (!e5.formHidden || !e5.doneShown || e5.doneText !== 'お申し込みありがとうございます。1営業日以内にメールでご連絡します。') NG(tag, '成功時の置き換え', JSON.stringify(e5));
      // 5. 失敗（500）：エラー文＋メール（【要記入】）。ボタンが戻る。※ 別のページ読み込みで確認
      await cdp.goto(SITE + t.page + '.html', 700);
      await cdp.ev(`document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-visible')); true`);
      await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const set = (n, v) => { const c = f.querySelector('[name=' + n + ']'); c.value = v; }; set('company', 'A'); set('firstname', 'B'); set('email', 'a@b.co'); f.querySelector('#${t.pfx}-privacy').checked = true; window.HUBSPOT_PORTAL_ID = '1'; window.HUBSPOT_FORM_DOWNLOAD = 'x'; window.HUBSPOT_FORM_CONSULT = 'y'; window.fetch = () => Promise.resolve({ ok: false, status: 500 }); f.querySelector('button[type=submit]').click(); })(); true`);
      await sleep(400);
      const e6 = await cdp.ev(`(() => { const f = ${R('form.lead-form')}; const x = f.querySelector('.lead-form__fail'); const b = f.querySelector('button[type=submit]'); return { shown: !x.hidden, hasMail: !!x.querySelector('.todo') && x.textContent.includes('【要記入：メールアドレス】'), text: x.querySelector('p').textContent.trim(), btnDisabled: b.disabled, label: b.textContent.trim(), formShown: !f.hidden }; })()`);
      if (!e6.shown || !e6.hasMail || e6.btnDisabled || !e6.formShown || e6.label !== t.label) NG(tag, '失敗時の表示', JSON.stringify(e6));
      // ネットワークエラー（reject）も同じ
      await cdp.ev(`(() => { const f = ${R('form.lead-form')}; f.querySelector('.lead-form__fail').hidden = true; window.fetch = () => Promise.reject(new Error('net')); f.querySelector('button[type=submit]').click(); })(); true`);
      await sleep(300);
      if (!(await cdp.ev(`!${R('.lead-form__fail')}.hidden`))) NG(tag, 'ネットワークエラーで失敗の表示が出ない');
      // 6. 横スクロール・はみ出し・タップ領域
      const ov = await cdp.ev(`(() => { const de = document.documentElement; const root = document.querySelector('${t.root}'); const rr = root.getBoundingClientRect(); const bad = []; for (const el of root.querySelectorAll('*')) { const cs = getComputedStyle(el); if (cs.display === 'none') continue; const r = el.getBoundingClientRect(); if (r.width && (r.right > rr.right + 0.5 || r.left < rr.left - 0.5)) bad.push(el.tagName + '.' + el.className); } const small = [...root.querySelectorAll('input[type=text],input[type=email],input[type=tel],select,button')].filter(e => e.getBoundingClientRect().height < 44).length; return { sw: de.scrollWidth, cw: de.clientWidth, bad: bad.slice(0, 4), small }; })()`);
      if (ov.sw > ov.cw) NG(tag, '横スクロール', ov.sw, ov.cw);
      if (ov.bad.length) NG(tag, 'カードからはみ出す要素', ov.bad.join(' '));
      if (ov.small) NG(tag, '高さ44px未満の入力欄／ボタン', ov.small);
    }
    // FV の「資料請求はこちら」→ #hero-form
    await cdp.goto(SITE + 'index.html', 900);
    await cdp.ev(`document.querySelector('.hero .btn--ghost').click(); true`);
    await sleep(1400);
    const an = await cdp.ev(`(() => { const r = document.querySelector('#hero-form').getBoundingClientRect(); const hdr = document.querySelector('.site-header').getBoundingClientRect(); return { hash: location.hash, top: Math.round(r.top), hdrB: Math.round(hdr.bottom), vh: innerHeight, bottom: Math.round(r.bottom) }; })()`);
    if (an.hash !== '#hero-form') NG(`index@${w}`, '従ボタンが #hero-form へ飛ばない', an.hash);
    if (an.top < an.hdrB - 2 || an.top > an.vh - 100) NG(`index@${w}`, 'フォームのカードが画面の中に来ない', JSON.stringify(an));
    console.log(`@${w} done`);
  }
} finally { await cdp.close(); }
console.log(fails ? `\nNG ${fails}` : '\nフォーム：全て通過');
process.exit(fails ? 1 : 0);

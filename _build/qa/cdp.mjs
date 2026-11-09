// 最小限の CDP ヘルパー（Node 組み込みの WebSocket / fetch のみ）
import { spawn } from 'node:child_process';
import fs from 'node:fs';

export const SP = new URL('../qa_out', import.meta.url).pathname;
export const SITE = process.env.SITE || 'http://127.0.0.1:8780/';  // python3 -m http.server 8780 --directory <リポジトリ直下>。./ と ./#id を実際の挙動で確かめるため file:// は使わない
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function launch(port = 9333) {
  const profile = `${SP}/_chrome_profile_${port}`;
  fs.rmSync(profile, { recursive: true, force: true });
  const chrome = spawn(CHROME, [
    '--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
    '--disable-extensions', '--allow-file-access-from-files', 'about:blank',
  ], { stdio: 'ignore' });
  let ready = false;
  for (let i = 0; i < 150; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}/json/version`); if (r.ok) { ready = true; break; } } catch {}
    await sleep(100);
  }
  if (!ready) { chrome.kill(); throw new Error('Chrome did not start'); }
  const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
  let id = 0;
  const pending = new Map();
  const listeners = new Set();
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message + " :: " + (pending.__m||""))) : resolve(msg.result);
    } else if (msg.method) {
      for (const l of listeners) l(msg);
    }
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const i = ++id; pending.set(i, { resolve, reject });
    pending.__m = method; ws.send(JSON.stringify({ id: i, method, params }));
  });
  await send('Page.enable');
  await send('Runtime.enable');

  const api = {
    send,
    on(fn) { listeners.add(fn); return () => listeners.delete(fn); },   // v10：CDP のイベントを受ける（ネットワークの確認用）
    async viewport(w, h, mobile = false, dpr) {
      await send('Emulation.setDeviceMetricsOverride', {
        width: w, height: h, deviceScaleFactor: dpr ?? (mobile ? 2 : 1), mobile,
        screenWidth: w, screenHeight: h,
      });
      await send('Emulation.setTouchEmulationEnabled', { enabled: mobile });
    },
    async goto(url, settle = 900) {
      await send('Page.navigate', { url: 'about:blank' });
      await sleep(80);
      const loaded = new Promise((res) => {
        const l = (m) => { if (m.method === 'Page.loadEventFired') { listeners.delete(l); res(); } };
        listeners.add(l);
        setTimeout(() => { listeners.delete(l); res(); }, 15000);
      });
      await send('Page.navigate', { url });
      await loaded;
      await sleep(settle);
    },
    async ev(expression) {
      const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error('JS error: ' + JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails.text));
      return r.result.value;
    },
    async shot(file, clip, beyond = false) {
      const params = { format: 'png', captureBeyondViewport: beyond };
      if (clip) params.clip = { x: clip.x, y: clip.y, width: clip.width, height: clip.height, scale: 1 };
      const r = await send('Page.captureScreenshot', params);
      fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
    },
    async close() { try { ws.close(); } catch {} chrome.kill('SIGKILL'); await sleep(200); fs.rmSync(profile, { recursive: true, force: true }); },
  };
  return api;
}

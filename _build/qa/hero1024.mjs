import { launch, SITE, SP, sleep } from './cdp.mjs';
const cdp = await launch(9344);
try {
  for (const w of [960, 1024, 1199]) {
    await cdp.viewport(w, 800, false, 1);
    await cdp.goto(SITE + 'index.html', 1200);
    await cdp.shot(`${SP}/ref_shots/v14_hero_${w}.png`);
  }
} finally { await cdp.close(); }

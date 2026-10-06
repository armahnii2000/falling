// test_gameplay.mjs
// Connects to Chrome DevTools Protocol to simulate gameplay, test color merges, and take screenshots

import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';

async function wait(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function getWsUrl(port) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json/version`, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const info = JSON.parse(data);
          resolve(info.webSocketDebuggerUrl);
        } catch(e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function run() {
  const port = 9333;
  const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless',
    '--disable-gpu',
    `--remote-debugging-port=${port}`,
    '--window-size=1200,900',
    'http://localhost:8086'
  ]);

  console.log('Chrome launched...');
  await wait(1500);

  let wsUrl;
  for (let i = 0; i < 10; i++) {
    try {
      wsUrl = await getWsUrl(port);
      if (wsUrl) break;
    } catch(e) {
      await wait(500);
    }
  }

  if (!wsUrl) {
    console.error('Failed to get WebSocket debugger URL');
    chrome.kill();
    process.exit(1);
  }

  console.log('Connecting to Chrome CDP...');
  const ws = new WebSocket(wsUrl);

  let msgId = 1;
  const pending = new Map();

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(msg.error);
      else resolve(msg.result);
    }
  };

  const send = (method, params = {}) => {
    return new Promise((resolve, reject) => {
      const id = msgId++;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  };

  await new Promise(r => ws.onopen = r);

  // Discover targets / pages
  const targetsRes = await send('Target.getTargets');
  const pageTarget = targetsRes.targetInfos.find(t => t.type === 'page');

  if (!pageTarget) {
    console.error('No page target found');
    chrome.kill();
    process.exit(1);
  }

  // Attach to page
  const attachRes = await send('Target.attachToTarget', { targetId: pageTarget.targetId, flatten: true });
  const sessionId = attachRes.sessionId;

  const sendSession = (method, params = {}) => {
    return new Promise((resolve, reject) => {
      const id = msgId++;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, sessionId, method, params }));
    });
  };

  await sendSession('Runtime.enable');
  await sendSession('Page.enable');

  console.log('Waiting for game page to load...');
  await wait(1000);

  // Simulate controlled merges in window.airBubbleGame:
  // We simulate:
  // 1. Two Tier 1 Red and Green blocks merging into Tier 2 (Yellow)
  // 2. A Tier 2 Blue block merging with the Tier 2 Yellow into Tier 3 (White Light!)
  console.log('Injecting controlled Suika merges to test RGB additive synthesis...');

  const evalRes = await sendSession('Runtime.evaluate', {
    expression: `
      (() => {
        const game = window.airBubbleGame;
        if (!game) return { error: 'Game not found' };

        // 1. First merge: Tier 1 Red + Tier 1 Green -> Tier 2 Yellow
        const b1 = { id: 101, tier: 1, r: 1, g: 0, b: 0, x: 250, y: 150, vy: 0, size: 28, hw: 14, hh: 14, wobbleX: 1, wobbleY: 1 };
        const b2 = { id: 102, tier: 1, r: 0, g: 1, b: 0, x: 250, y: 150, vy: 0, size: 28, hw: 14, hh: 14, wobbleX: 1, wobbleY: 1 };
        game.onMerge(b1, b2);

        // 2. Second merge: Tier 2 Yellow + Tier 2 Blue -> Tier 3 White!
        const b3 = { id: 103, tier: 2, r: 1, g: 1, b: 0, x: 280, y: 120, vy: 0, size: 56, hw: 28, hh: 28, wobbleX: 1, wobbleY: 1 };
        const b4 = { id: 104, tier: 2, r: 0, g: 0, b: 2, x: 280, y: 120, vy: 0, size: 56, hw: 28, hh: 28, wobbleX: 1, wobbleY: 1 };
        game.onMerge(b3, b4);

        // 3. Third merge: another tier 2 merge to build more units
        const b5 = { id: 105, tier: 2, r: 2, g: 0, b: 0, x: 200, y: 100, vy: 0, size: 56, hw: 28, hh: 28, wobbleX: 1, wobbleY: 1 };
        const b6 = { id: 106, tier: 2, r: 0, g: 2, b: 0, x: 200, y: 100, vy: 0, size: 56, hw: 28, hh: 28, wobbleX: 1, wobbleY: 1 };
        game.onMerge(b5, b6);

        // 4. Fourth merge: blue units to bring R, G, B into 100% Pure White Equilibrium! (R:4, G:4, B:4)
        const b7 = { id: 107, tier: 1, r: 0, g: 0, b: 1, x: 300, y: 90, vy: 0, size: 28, hw: 14, hh: 14, wobbleX: 1, wobbleY: 1 };
        const b8 = { id: 108, tier: 1, r: 0, g: 0, b: 1, x: 300, y: 90, vy: 0, size: 28, hw: 14, hh: 14, wobbleX: 1, wobbleY: 1 };
        game.onMerge(b7, b8);

        // 5. Test Aim Forecast with Multi-hop Combo Cascade:
        // Set readyBubble to a Tier 2 Blue bubble (b=2)
        game.readyBubble = { tier: 2, r: 0, g: 0, b: 2, colorName: 'blue' };

        // Position bubbles without pre-existing collisions:
        // Target: Tier 2 Yellow [R:1 G:1 B:0] at x=240, y=180
        // Neighbor 1: Tier 3 Cyan [R:0 G:1 B:1] directly above at x=240, y=110
        // Result: Ready(T2) + Target(T2) -> New T3 [R:1 G:1 B:2].
        // Then New T3 touches Neighbor 1 (T3) -> Cascades into T4 [R:1 G:2 B:3] (COMBO x2)!
        const targetB = { id: 201, tier: 2, r: 1, g: 1, b: 0, x: 240, y: 180, vy: 0, size: 56, hw: 28, hh: 28, wobbleX: 1, wobbleY: 1 };
        const neighborB = { id: 202, tier: 3, r: 0, g: 1, b: 1, x: 240, y: 110, vy: 0, size: 84, hw: 42, hh: 42, wobbleX: 1, wobbleY: 1 };
        game.physics.bubbles.push(targetB);
        game.physics.bubbles.push(neighborB);

        // Aim launcher directly at x = 240
        game.launcherX = 240;

        // Calculate forecast BEFORE physics step modifies positions
        const comboForecast = game.calculateAimForecast();

        // Run update so DOM and Canvas render with this forecast and updated hero orb
        game.updateCumulativeHero();
        game.updateShotForecastCard(comboForecast);
        game.render();
        game.isPaused = true;
        const forecast = comboForecast;

        // Read DOM elements
        const orb = document.getElementById('cumulative-color-orb');
        const orbNum = document.getElementById('cumulative-orb-number');
        const forecastCard = document.getElementById('shot-forecast-card');
        const forecastBadge = document.getElementById('forecast-action-badge');
        const forecastTarget = document.getElementById('forecast-target-desc');
        const forecastTier = document.getElementById('forecast-res-tier');
        const fBadgeR = document.getElementById('f-badge-r');
        const fBadgeG = document.getElementById('f-badge-g');
        const fBadgeB = document.getElementById('f-badge-b');
        const forecastDesc = document.getElementById('forecast-outcome-desc');

        return {
          cumulativeR: game.cumulativeR,
          cumulativeG: game.cumulativeG,
          cumulativeB: game.cumulativeB,
          totalMerges: game.totalMerges,
          orbNumber: orbNum ? orbNum.textContent : null,
          forecast: {
            willMerge: forecast.willMerge,
            comboCount: forecast.comboCount,
            finalTier: forecast.finalTier,
            expectedR: forecast.expectedR,
            expectedG: forecast.expectedG,
            expectedB: forecast.expectedB,
            chainEvents: forecast.chainEvents
          },
          domForecast: {
            badgeText: forecastBadge ? forecastBadge.textContent : null,
            targetText: forecastTarget ? forecastTarget.textContent : null,
            tierText: forecastTier ? forecastTier.textContent : null,
            rText: fBadgeR ? fBadgeR.textContent : null,
            gText: fBadgeG ? fBadgeG.textContent : null,
            bText: fBadgeB ? fBadgeB.textContent : null,
            descText: forecastDesc ? forecastDesc.textContent : null
          }
        };
      })()
    `,
    returnByValue: true
  });

  console.log('Simulation Results:', JSON.stringify(evalRes.result.value, null, 2));

  // Take screenshot
  console.log('Capturing verified proof screenshot...');
  const shotRes = await sendSession('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('web/proof_cumulative_color_orb_in_action.png', Buffer.from(shotRes.data, 'base64'));
  console.log('Screenshot saved to web/proof_cumulative_color_orb_in_action.png');

  ws.close();
  chrome.kill();
  process.exit(0);
}

run().catch(err => {
  console.error('Error running test:', err);
  process.exit(1);
});

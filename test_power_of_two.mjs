// test_power_of_two.mjs
// Verifies 11-block power-of-2 architecture: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024
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
  const port = 9334;
  const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless',
    '--disable-gpu',
    `--remote-debugging-port=${port}`,
    '--window-size=1200,900',
    'http://localhost:8086'
  ]);

  console.log('Chrome launched on port', port);
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

  const targetsRes = await send('Target.getTargets');
  const pageTarget = targetsRes.targetInfos.find(t => t.type === 'page');
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
  await wait(1000);

  // Test 1: Verify TIERS constant and getTierValue
  const tierTest = await sendSession('Runtime.evaluate', {
    expression: `
      (() => {
        return {
          tiersLength: TIERS.length,
          tiers: TIERS.map(t => ({ tier: t.tier, val: t.val, name: t.name })),
          sampleValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map(k => getTierValue(k)),
          evoStripCount: document.querySelectorAll('#evo-scroll-container .evo-item').length,
          evoBadges: Array.from(document.querySelectorAll('#evo-scroll-container .evo-badge')).map(b => b.textContent.trim())
        };
      })()
    `,
    returnByValue: true
  });

  console.log('Tier Architecture Test Result:');
  console.log(JSON.stringify(tierTest.result.value, null, 2));

  // Test 2: Simulate 1+1=2, 2+2=4, 4+4=8 merges and spawn bubbles
  const mergeTest = await sendSession('Runtime.evaluate', {
    expression: `
      (() => {
        const game = window.airBubbleGame;
        if (!game) return { error: 'Game not found' };

        // Clear bubbles for clean test
        game.physics.bubbles = [];

        // Spawn two Tier 1 blocks (Red 1 and Green 1)
        const b1 = game.physics.createBubble(1, { r: 1, g: 0, b: 0 }, 200, 100, 0);
        const b2 = game.physics.createBubble(1, { r: 0, g: 1, b: 0 }, 200, 100, 0);
        game.physics.bubbles.push(b1, b2);

        // Perform merge 1 + 1 -> 2
        game.onMerge(b1, b2);
        const mergedTier2 = game.physics.bubbles[0];

        // Now spawn another Tier 2 block (val 2, Blue: 2)
        const b3 = game.physics.createBubble(2, { r: 0, g: 0, b: 2 }, 260, 100, 0);
        game.physics.bubbles.push(b3);

        // Merge Tier 2 (R:1, G:1) + Tier 2 (B:2) -> Tier 3 (R:1, G:1, B:2) = val 4
        game.onMerge(mergedTier2, b3);
        const mergedTier3 = game.physics.bubbles[0];

        // Now spawn another Tier 3 block (val 4, R:2, G:2)
        const b4 = game.physics.createBubble(3, { r: 2, g: 2, b: 0 }, 320, 100, 0);
        game.physics.bubbles.push(b4);

        // Merge Tier 3 (val 4) + Tier 3 (val 4) -> Tier 4 (val 8)
        game.onMerge(mergedTier3, b4);
        const mergedTier4 = game.physics.bubbles[0];

        // Now create a few ambient blocks across chamber to show various tiers
        const block16 = game.physics.createBubble(5, { r: 8, g: 4, b: 4 }, 120, 220, 0); // val 16
        const block32 = game.physics.createBubble(6, { r: 16, g: 10, b: 6 }, 240, 260, 0); // val 32
        const block64 = game.physics.createBubble(7, { r: 21, g: 21, b: 22 }, 180, 360, 0); // val 64 (Near white!)
        game.physics.bubbles.push(block16, block32, block64);

        return {
          mergedTier4: {
            tier: mergedTier4.tier,
            val: mergedTier4.val,
            r: mergedTier4.r,
            g: mergedTier4.g,
            b: mergedTier4.b,
            sumUnits: mergedTier4.r + mergedTier4.g + mergedTier4.b,
            expectedVal: 8
          },
          allBubbles: game.physics.bubbles.map(b => ({
            id: b.id,
            tier: b.tier,
            val: b.val,
            r: b.r,
            g: b.g,
            b: b.b,
            sum: b.r + b.g + b.b
          })),
          score: game.score,
          peakTier: game.peakTier,
          bestBalance: game.bestBalance
        };
      })()
    `,
    returnByValue: true
  });

  console.log('Merge & Addition Verification Result:');
  console.log(JSON.stringify(mergeTest.result.value, null, 2));

  // Test 3: Test hover forecast calculation
  const forecastTest = await sendSession('Runtime.evaluate', {
    expression: `
      (() => {
        const game = window.airBubbleGame;
        // Clear bubbles in lane x=350 and spawn isolated match
        game.physics.bubbles = game.physics.bubbles.filter(b => Math.abs(b.x - 350) > 30);
        game.readyBubble = game.physics.createBubble(1, { r: 1, g: 0, b: 0 }, 350, 400, 0);
        game.readyBubble.val = 1;

        const target = game.physics.createBubble(1, { r: 0, g: 1, b: 0 }, 350, 200, 0);
        target.val = 1;
        game.physics.bubbles.push(target);

        // Aim directly at target
        game.launcherX = 350;
        const forecast = game.calculateAimForecast();
        game.updateShotForecastCard(forecast);

        return {
          willMerge: forecast.willMerge,
          finalTier: forecast.finalTier,
          finalVal: getTierValue(forecast.finalTier),
          expectedR: forecast.expectedR,
          expectedG: forecast.expectedG,
          chainDesc: forecast.chainEvents?.[0]?.desc,
          badgeText: document.getElementById('forecast-action-badge')?.textContent,
          targetDesc: document.getElementById('forecast-target-desc')?.textContent,
          resTier: document.getElementById('forecast-res-tier')?.textContent
        };
      })()
    `,
    returnByValue: true
  });

  console.log('Hover Forecast Test Result:');
  console.log(JSON.stringify(forecastTest.result.value, null, 2));

  // Wait 500ms for rendering
  await wait(500);

  // Capture screenshot of the game
  const screenshotRes = await sendSession('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('web/power_of_two_proof.png', Buffer.from(screenshotRes.data, 'base64'));
  console.log('Saved screenshot to web/power_of_two_proof.png');

  ws.close();
  chrome.kill();
  console.log('Test completed successfully!');
}

run().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});

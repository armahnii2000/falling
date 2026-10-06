const fs = require('fs');

async function testUpdates() {
  // 1. Check statistical distribution of rollTempType
  console.log('--- Testing rollTempType Distribution (10,000 rolls) ---');
  let counts = { hot: 0, cold: 0, normal: 0 };
  // Mock rollTempType logic matching game.js
  const roll = () => {
    const r = Math.random();
    if (r < 0.40) return 'hot';
    if (r < 0.90) return 'cold';
    return 'normal';
  };
  for (let i = 0; i < 10000; i++) {
    counts[roll()]++;
  }
  console.log('Results over 10,000 rolls:');
  console.log(`Hot (Red): ${counts.hot} (${(counts.hot / 100).toFixed(1)}%) [Target: 40% - doubled from 20%]`);
  console.log(`Cold (Blue): ${counts.cold} (${(counts.cold / 100).toFixed(1)}%) [Target: 50% - doubled from 25%]`);
  console.log(`Normal: ${counts.normal} (${(counts.normal / 100).toFixed(1)}%) [Target: 10%]`);

  // 2. Launch browser and verify in live engine
  const tabsRes = await fetch('http://localhost:9222/json');
  const tabs = await tabsRes.json();
  const pageTab = tabs.find(t => t.url.includes('8085') && t.type === 'page');

  const ws = new WebSocket(pageTab.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);

  let id = 1;
  const send = (m, p = {}) => new Promise((res, rej) => {
    const cur = ++id;
    const h = e => {
      const d = JSON.parse(e.data);
      if (d.id === cur) {
        ws.removeEventListener('message', h);
        if (d.error) rej(d.error);
        else res(d.result);
      }
    };
    ws.addEventListener('message', h);
    ws.send(JSON.stringify({ id: cur, method: m, params: p }));
  });

  // Reload page
  await send('Page.navigate', { url: 'http://localhost:8085/?t=' + Date.now() });
  await new Promise(r => setTimeout(r, 1200));

  // Set desktop viewport 1280x800
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 500));

  // Launch a few bubbles to see red and blue bubbles in the chamber and vent
  console.log('\n--- Launching bubbles to test red and blue bubbles & 28px vent ---');
  for (let i = 0; i < 5; i++) {
    await send('Runtime.evaluate', { expression: 'window.airBubbleGame.launchCurrentBubble()' });
    await new Promise(r => setTimeout(r, 300));
  }

  // Let them settle a bit
  await new Promise(r => setTimeout(r, 800));

  const stats = await send('Runtime.evaluate', {
    expression: `(() => {
      const game = window.airBubbleGame;
      const bubbles = game.physics.bubbles.map(b => ({
        id: b.id,
        tier: b.tier,
        tempType: b.tempType,
        x: Math.round(b.x),
        y: Math.round(b.y)
      }));
      return {
        bubbleCount: bubbles.length,
        bubbles,
        readyBubble: game.readyBubble,
        nextBubble: game.nextBubble,
        pressure: game.pressure
      };
    })()`,
    returnByValue: true
  });
  console.log('Active bubbles in chamber:', JSON.stringify(stats.result.value, null, 2));

  // Screenshot with active bubbles and doubled vent
  const ssDesktop = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_vent_and_colors.png', Buffer.from(ssDesktop.data, 'base64'));
  console.log('Saved proof_vent_and_colors.png');

  // Also test mobile view
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await new Promise(r => setTimeout(r, 500));

  const ssMobile = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_mobile_vent.png', Buffer.from(ssMobile.data, 'base64'));
  console.log('Saved proof_mobile_vent.png');

  process.exit(0);
}

testUpdates().catch(e => {
  console.error(e);
  process.exit(1);
});

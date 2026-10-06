const fs = require('fs');

async function testLayout() {
  const tabsRes = await fetch('http://localhost:9222/json');
  const tabs = await tabsRes.json();
  const pageTab = tabs.find(t => t.url.includes('8085') && t.type === 'page');
  console.log('Using page:', pageTab.url);

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

  // Navigate to fresh reload
  await send('Page.navigate', { url: 'http://localhost:8085/?t=' + Date.now() });
  await new Promise(r => setTimeout(r, 1000));

  // Test 1: Desktop 1280x800
  console.log('\n--- Testing Desktop 1280x800 ---');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 500));

  let info = await send('Runtime.evaluate', {
    expression: `(() => {
      const gv = document.getElementById('game-view').getBoundingClientRect();
      const chamber = window.airBubbleGame.physics.chamber;
      return {
        gameViewHeight: gv.height,
        chamberH: chamber.h,
        chamberY: chamber.y,
        cellSize: window.airBubbleGame.physics.cellSize,
        ceilingMargin: chamber.y,
        floorMargin: gv.height - (chamber.y + chamber.h),
        sliderWrapWidth: document.getElementById('slider-wrap').offsetWidth,
        btnLaunchWidth: document.getElementById('btn-launch').offsetWidth
      };
    })()`,
    returnByValue: true
  });
  console.log('Desktop 1280x800 layout metrics:', info.result.value);

  let ss = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_desktop_1280x800.png', Buffer.from(ss.data, 'base64'));

  // Test 2: Trigger Game Over, then click 'Start Fresh Funding Round'
  console.log('\n--- Testing Fresh Round Restart on Desktop ---');
  await send('Runtime.evaluate', { expression: 'window.airBubbleGame.triggerOverpressure()' });
  await new Promise(r => setTimeout(r, 400));

  let ssModal = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_modal.png', Buffer.from(ssModal.data, 'base64'));

  // Click Restart button inside modal
  await send('Runtime.evaluate', {
    expression: `(() => {
      document.getElementById('btn-modal-restart').click();
    })()`
  });
  await new Promise(r => setTimeout(r, 500));

  let afterRestartInfo = await send('Runtime.evaluate', {
    expression: `(() => {
      const gv = document.getElementById('game-view').getBoundingClientRect();
      const chamber = window.airBubbleGame.physics.chamber;
      return {
        windowScrollY: window.scrollY,
        appContainerScrollTop: document.getElementById('app-container').scrollTop,
        gameViewScrollTop: document.getElementById('game-view').scrollTop,
        gameViewHeight: gv.height,
        chamberH: chamber.h,
        chamberY: chamber.y,
        cellSize: window.airBubbleGame.physics.cellSize,
        ceilingMargin: chamber.y,
        floorMargin: gv.height - (chamber.y + chamber.h)
      };
    })()`,
    returnByValue: true
  });
  console.log('After Fresh Round Click metrics:', afterRestartInfo.result.value);

  let ssFresh = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_fresh_round.png', Buffer.from(ssFresh.data, 'base64'));

  // Test 3: Short Desktop Window (1200x650)
  console.log('\n--- Testing Short Desktop 1200x650 ---');
  await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 650, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 500));

  let info650 = await send('Runtime.evaluate', {
    expression: `(() => {
      const gv = document.getElementById('game-view').getBoundingClientRect();
      const chamber = window.airBubbleGame.physics.chamber;
      return {
        gameViewHeight: gv.height,
        chamberH: chamber.h,
        chamberY: chamber.y,
        cellSize: window.airBubbleGame.physics.cellSize,
        ceilingMargin: chamber.y,
        floorMargin: gv.height - (chamber.y + chamber.h)
      };
    })()`,
    returnByValue: true
  });
  console.log('Short Desktop 1200x650 metrics:', info650.result.value);

  let ss650 = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_desktop_650.png', Buffer.from(ss650.data, 'base64'));

  // Test 4: Mobile iPhone Viewport (390x844)
  console.log('\n--- Testing Mobile Portrait 390x844 ---');
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await new Promise(r => setTimeout(r, 500));

  let infoMobile = await send('Runtime.evaluate', {
    expression: `(() => {
      const gv = document.getElementById('game-view').getBoundingClientRect();
      const chamber = window.airBubbleGame.physics.chamber;
      return {
        gameViewHeight: gv.height,
        chamberH: chamber.h,
        chamberY: chamber.y,
        cellSize: window.airBubbleGame.physics.cellSize,
        ceilingMargin: chamber.y,
        floorMargin: gv.height - (chamber.y + chamber.h)
      };
    })()`,
    returnByValue: true
  });
  console.log('Mobile 390x844 metrics:', infoMobile.result.value);

  let ssMobile = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('/Users/georgearmah/air-bubble/web/proof_mobile_390x844.png', Buffer.from(ssMobile.data, 'base64'));

  console.log('\nVerification complete! All screenshots saved.');
  process.exit(0);
}

testLayout().catch(e => {
  console.error(e);
  process.exit(1);
});

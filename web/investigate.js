const fs = require('fs');

async function main() {
  const tabsRes = await fetch('http://localhost:9222/json');
  const tabs = await tabsRes.json();
  let targetTab = tabs.find(t => t.url.includes('8085'));
  if (!targetTab) targetTab = tabs[0];

  console.log('Target tab:', targetTab.url);
  const ws = new WebSocket(targetTab.webSocketDebuggerUrl);

  await new Promise((resolve) => ws.onopen = resolve);

  let msgId = 1;
  function callCDP(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++msgId;
      const handler = (evt) => {
        const msg = JSON.parse(evt.data);
        if (msg.id === id) {
          ws.removeEventListener('message', handler);
          if (msg.error) reject(msg.error);
          else resolve(msg.result);
        }
      };
      ws.addEventListener('message', handler);
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  // Test various desktop viewport sizes: 1280x800, 1024x768, 1280x700, 1280x600
  const viewports = [
    { w: 1280, h: 800, label: '800h' },
    { w: 1280, h: 700, label: '700h' },
    { w: 1280, h: 600, label: '600h' }
  ];

  for (const vp of viewports) {
    console.log(`\n================ Testing Viewport ${vp.w}x${vp.h} (${vp.label}) ================`);
    await callCDP('Emulation.setDeviceMetricsOverride', {
      width: vp.w,
      height: vp.h,
      deviceScaleFactor: 1,
      mobile: false
    });

    // Wait a brief moment for resize event to fire and settle
    await new Promise(r => setTimeout(r, 200));

    const evalRes = await callCDP('Runtime.evaluate', {
      expression: `(() => {
        const getBox = (id) => {
          const el = document.getElementById(id);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return {
            id,
            top: Math.round(r.top),
            bottom: Math.round(r.bottom),
            height: Math.round(r.height),
            scrollTop: el.scrollTop
          };
        };
        const game = window.airBubbleGame;
        return {
          windowHeight: window.innerHeight,
          docScrollTop: document.documentElement.scrollTop,
          bodyScrollTop: document.body.scrollTop,
          appContainer: getBox('app-container'),
          header: getBox('header-bar'),
          stats: getBox('stats-banner'),
          controls: getBox('controls-top'),
          gameView: getBox('game-view'),
          launcher: getBox('launcher-bar'),
          evoStrip: getBox('evolution-strip'),
          chamber: game ? game.physics.chamber : null,
          chamberGlobalY: game && game.physics.chamber ? Math.round(document.getElementById('game-view').getBoundingClientRect().top + game.physics.chamber.y) : null,
          controlsBottom: Math.round(document.getElementById('controls-top').getBoundingClientRect().bottom)
        };
      })()`,
      returnByValue: true
    });

    console.log('Layout at start:', JSON.stringify(evalRes.result.value, null, 2));

    // Now trigger game over
    await callCDP('Runtime.evaluate', {
      expression: `window.airBubbleGame.triggerOverpressure()`
    });

    await new Promise(r => setTimeout(r, 200));

    // Inspect layout during game over modal
    const evalOver = await callCDP('Runtime.evaluate', {
      expression: `(() => {
        const modal = document.getElementById('game-over-modal');
        const card = modal.querySelector('.modal-card');
        const modalR = modal.getBoundingClientRect();
        const cardR = card.getBoundingClientRect();
        return {
          modalBox: { top: modalR.top, bottom: modalR.bottom, height: modalR.height },
          cardBox: { top: cardR.top, bottom: cardR.bottom, height: cardR.height },
          appScrollTop: document.getElementById('app-container').scrollTop,
          gameViewScrollTop: document.getElementById('game-view').scrollTop,
          docScrollTop: document.documentElement.scrollTop
        };
      })()`,
      returnByValue: true
    });
    console.log('Layout during Game Over Modal:', JSON.stringify(evalOver.result.value, null, 2));

    // Now click 'Start Fresh Funding Round'
    await callCDP('Runtime.evaluate', {
      expression: `(() => {
        const btn = document.getElementById('btn-modal-restart');
        btn.click();
      })()`
    });

    await new Promise(r => setTimeout(r, 200));

    // Inspect layout after clicking Start Fresh Funding Round
    const evalAfterRestart = await callCDP('Runtime.evaluate', {
      expression: `(() => {
        const getBox = (id) => {
          const el = document.getElementById(id);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return {
            id,
            top: Math.round(r.top),
            bottom: Math.round(r.bottom),
            height: Math.round(r.height),
            scrollTop: el.scrollTop
          };
        };
        const game = window.airBubbleGame;
        const gvR = document.getElementById('game-view').getBoundingClientRect();
        return {
          appContainer: getBox('app-container'),
          gameView: getBox('game-view'),
          docScrollTop: document.documentElement.scrollTop,
          chamber: game ? game.physics.chamber : null,
          chamberGlobalY: game && game.physics.chamber ? Math.round(gvR.top + game.physics.chamber.y) : null,
          controlsBottom: Math.round(document.getElementById('controls-top').getBoundingClientRect().bottom),
          overlap: (game && game.physics.chamber) ? (document.getElementById('controls-top').getBoundingClientRect().bottom - (gvR.top + game.physics.chamber.y)) : null
        };
      })()`,
      returnByValue: true
    });
    console.log('Layout after Fresh Round Restart:', JSON.stringify(evalAfterRestart.result.value, null, 2));

    const ss = await callCDP('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`/Users/georgearmah/air-bubble/web/screenshot_${vp.label}.png`, Buffer.from(ss.data, 'base64'));
    console.log(`Saved screenshot_${vp.label}.png`);
  }

  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});

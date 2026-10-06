import urllib.request
import json
import asyncio
import websockets
import base64
import sys

async def run_investigation():
    # Get tabs
    req = urllib.request.urlopen("http://localhost:9222/json")
    tabs = json.loads(req.read().decode())
    target_tab = None
    for tab in tabs:
        if "8085" in tab.get("url", ""):
            target_tab = tab
            break
    if not target_tab:
        target_tab = tabs[0]

    ws_url = target_tab["webSocketDebuggerUrl"]
    print("Connecting to:", ws_url)

    async with websockets.connect(ws_url) as ws:
        msg_id = 1
        async def call_cdp(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method, "params": params or {}}
            await ws.send(json.dumps(payload))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == msg_id:
                    return resp.get("result", {})

        # Set viewport to typical desktop size, e.g. 1280x800
        await call_cdp("Emulation.setDeviceMetricsOverride", {
            "width": 1280,
            "height": 800,
            "deviceScaleFactor": 1,
            "mobile": False
        })

        # Evaluate layout state
        eval_script = """
        (() => {
            const getBox = (id) => {
                const el = document.getElementById(id);
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return { id, top: r.top, bottom: r.bottom, height: r.height, scrollTop: el.scrollTop };
            };
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
                chamber: window.airBubbleGame ? window.airBubbleGame.physics.chamber : null
            };
        })()
        """
        res = await call_cdp("Runtime.evaluate", {"expression": eval_script, "returnByValue": True})
        print("Initial layout:")
        print(json.dumps(res.get("result", {}).get("value", {}), indent=2))

        # Now simulate Game Over
        trigger_over = """
        (() => {
            window.airBubbleGame.triggerOverpressure();
            return {
                appScrollTop: document.getElementById('app-container').scrollTop,
                gameViewScrollTop: document.getElementById('game-view').scrollTop,
                docScrollTop: document.documentElement.scrollTop
            };
        })()
        """
        res_over = await call_cdp("Runtime.evaluate", {"expression": trigger_over, "returnByValue": True})
        print("After Game Over:")
        print(json.dumps(res_over.get("result", {}).get("value", {}), indent=2))

        # Now simulate clicking 'Start Fresh Funding Round'
        click_restart = """
        (() => {
            const btn = document.getElementById('btn-modal-restart');
            btn.click();
            return {
                appScrollTop: document.getElementById('app-container').scrollTop,
                gameViewScrollTop: document.getElementById('game-view').scrollTop,
                docScrollTop: document.documentElement.scrollTop,
                gameViewBox: (() => {
                    const r = document.getElementById('game-view').getBoundingClientRect();
                    return { top: r.top, bottom: r.bottom, height: r.height };
                })(),
                chamber: window.airBubbleGame ? window.airBubbleGame.physics.chamber : null
            };
        })()
        """
        res_restart = await call_cdp("Runtime.evaluate", {"expression": click_restart, "returnByValue": True})
        print("After Start Fresh Round:")
        print(json.dumps(res_restart.get("result", {}).get("value", {}), indent=2))

        # Take screenshot
        ss = await call_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in ss:
            with open("/Users/georgearmah/air-bubble/web/after_fresh_round.png", "wb") as f:
                f.write(base64.b64decode(ss["data"]))
            print("Screenshot saved to /Users/georgearmah/air-bubble/web/after_fresh_round.png")

asyncio.run(run_investigation())

// Into the Darkness — Core Game & Dual-Layer Engine
// Subtractive CMY Ink Blending + Downward Gravity + Sinking Notifications + Layer Swap

class DarknessGame {
  constructor() {
    this.canvas = document.getElementById('game-canvas');
    this.ctx = this.canvas.getContext('2d');
    
    // Game State
    this.score = 0;
    this.highestTier = 1;
    this.peakBlackness = 0; // 0 to 100%
    this.combo = 1;
    this.lastMergeTime = 0;
    this.isPaused = false;
    this.isPhoneFocus = false;
    this.theme = 'sumi'; // 'sumi' | 'amber_crt' | 'nordic' | 'classic'

    // Chamber & Physics
    this.gravity = 980; // px/s² downwards
    this.restitution = 0.22;
    this.friction = 0.85;
    this.blocks = [];
    this.nextBlock = null;
    this.currentBlock = null;
    this.cooldown = 0;
    this.aimX = 0.5; // normalized 0..1 across chamber

    // Narrative Notifications Queue
    this.notificationsQueue = [
      { score: 200, app: 'MESSAGES', from: 'Wife', msg: "Leo, are you coming to bed? It's almost 3:30 AM.", icon: '💬', color: '#25D366' },
      { score: 600, app: 'SLACK', from: 'Apex Tech', msg: "Security: System access revoked for user l_vance.", icon: '⚡', color: '#E01E5A' },
      { score: 1200, app: 'CHASE', from: 'Banking', msg: "Account Alert: Mortgage auto-debit pending insufficient funds.", icon: '⚠️', color: '#FF9500' },
      { score: 2400, app: 'NEWS', from: 'TechCrunch', msg: "Apex Technologies initiates surprise overnight workforce reduction.", icon: '📰', color: '#00F0FF' },
      { score: 4800, app: 'MESSAGES', from: 'Wife', msg: "Leo, please... whatever is happening, we will get through this.", icon: '❤️', color: '#FF2D55' },
    ];
    this.activeNotification = null;

    // Dimensions
    this.chamber = { x: 30, y: 190, w: 320, h: 480 };
    this.unitSize = 22; // size of 1x1 block in pixels

    // Web Audio Synthesizer
    this.initAudio();

    // Setup
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.setupInputs();
    this.spawnNextBlock();
    this.takeNextBlock();

    // Start Loop
    this.lastTime = performance.now();
    requestAnimationFrame((t) => this.loop(t));
  }

  // --- AUDIO SYNTHESIS (Zero cloud credits) ----------------------------------
  initAudio() {
    this.audioCtx = null;
    const unlock = () => {
      if (!this.audioCtx) {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      window.removeEventListener('click', unlock);
      window.removeEventListener('keydown', unlock);
    };
    window.addEventListener('click', unlock);
    window.addEventListener('keydown', unlock);
  }

  playDropSound() {
    if (!this.audioCtx) return;
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(320, this.audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(120, this.audioCtx.currentTime + 0.12);
    gain.gain.setValueAtTime(0.18, this.audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.12);
    osc.connect(gain);
    gain.connect(this.audioCtx.destination);
    osc.start();
    osc.stop(this.audioCtx.currentTime + 0.12);
  }

  playMergeSound(tier) {
    if (!this.audioCtx) return;
    // Lower, deeper resonance as blocks grow toward Black
    const baseFreq = Math.max(65, 440 - (tier * 32));
    const osc = this.audioCtx.createOscillator();
    const sub = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(baseFreq, this.audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.5, this.audioCtx.currentTime + 0.25);

    sub.type = 'triangle';
    sub.frequency.setValueAtTime(baseFreq * 0.5, this.audioCtx.currentTime);

    gain.gain.setValueAtTime(0.28, this.audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.3);

    osc.connect(gain);
    sub.connect(gain);
    gain.connect(this.audioCtx.destination);

    osc.start();
    sub.start();
    osc.stop(this.audioCtx.currentTime + 0.3);
    sub.stop(this.audioCtx.currentTime + 0.3);
  }

  playSwapSound() {
    if (!this.audioCtx) return;
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(600, this.audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(300, this.audioCtx.currentTime + 0.2);
    gain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(this.audioCtx.destination);
    osc.start();
    osc.stop(this.audioCtx.currentTime + 0.2);
  }

  playSinkSound() {
    if (!this.audioCtx) return;
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(180, this.audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(60, this.audioCtx.currentTime + 0.35);
    gain.gain.setValueAtTime(0.25, this.audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.35);
    osc.connect(gain);
    gain.connect(this.audioCtx.destination);
    osc.start();
    osc.stop(this.audioCtx.currentTime + 0.35);
  }

  // --- SUBTRACTIVE CMY INK MODEL ---------------------------------------------
  // Base Spawns: Pure Cyan, Pure Magenta, Pure Yellow
  rollBaseInk() {
    const r = Math.random();
    if (r < 0.34) return { c: 1.0, m: 0.0, y: 0.0, tier: 1 }; // Pure Cyan
    if (r < 0.67) return { c: 0.0, m: 1.0, y: 0.0, tier: 1 }; // Pure Magenta
    return { c: 0.0, m: 0.0, y: 1.0, tier: 1 };               // Pure Yellow
  }

  cmyToRgb(c, m, y) {
    // Standard subtractive formula: R = 1 - C, G = 1 - M, B = 1 - Y
    const r = Math.max(0, Math.min(255, Math.round((1.0 - c) * 255)));
    const g = Math.max(0, Math.min(255, Math.round((1.0 - m) * 255)));
    const b = Math.max(0, Math.min(255, Math.round((1.0 - y) * 255)));
    return `rgb(${r}, ${g}, ${b})`;
  }

  // --- RESIZE & CHAMBER GEOMETRY ---------------------------------------------
  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;

    this.cols = 24; // Option A: 24 columns
    this.rows = 36; // Option A: 36 rows (2:3 aspect ratio)

    const padX = 20;
    const topY = 185; // below slider track
    const maxAvailableH = rect.height - topY - 110;
    const maxAvailableW = rect.width - (padX * 2);

    // Calculate integer pixel unit size maintaining exact 24x36 (2:3) grid
    const unitFromW = Math.floor(maxAvailableW / this.cols);
    const unitFromH = Math.floor(maxAvailableH / this.rows);
    this.unitSize = Math.max(8, Math.min(unitFromW, unitFromH));

    const chamberW = this.cols * this.unitSize;
    const chamberH = this.rows * this.unitSize;
    const stageLeft = Math.floor((rect.width - chamberW) / 2);

    this.chamber = {
      x: stageLeft,
      y: topY,
      w: chamberW,
      h: chamberH
    };
  }

  // --- INPUT CONTROLS --------------------------------------------------------
  setupInputs() {
    const slider = document.getElementById('aim-slider');
    slider.addEventListener('input', (e) => {
      this.aimX = parseFloat(e.target.value) / 100.0;
    });

    // Tap canvas to drop block
    this.canvas.addEventListener('pointerdown', (e) => {
      if (this.isPhoneFocus) return;
      const rect = this.canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left - this.chamber.x) / this.chamber.w;
      this.aimX = Math.max(0.05, Math.min(0.95, x));
      slider.value = this.aimX * 100;
      this.dropCurrentBlock();
    });

    // Keyboard controls
    window.addEventListener('keydown', (e) => {
      if (e.code === 'ArrowLeft' || e.key === 'a') {
        this.aimX = Math.max(0.05, this.aimX - 0.05);
        slider.value = this.aimX * 100;
      } else if (e.code === 'ArrowRight' || e.key === 'd') {
        this.aimX = Math.min(0.95, this.aimX + 0.05);
        slider.value = this.aimX * 100;
      } else if (e.code === 'Space' || e.code === 'ArrowDown' || e.key === 'w') {
        this.dropCurrentBlock();
      } else if (e.key === 's' || e.key === 'S') {
        this.toggleLayerSwap();
      }
    });

    // SWAP Button trigger
    const swapBtn = document.getElementById('btn-swap');
    if (swapBtn) {
      swapBtn.addEventListener('click', () => this.toggleLayerSwap());
    }

    // Floating Notification Tap (Sinking mechanic!)
    const notifCard = document.getElementById('floating-notification');
    if (notifCard) {
      notifCard.addEventListener('click', () => this.sinkActiveNotification());
    }

    // Theme Switcher Buttons
    document.querySelectorAll('.theme-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const selected = e.target.dataset.theme;
        this.setTheme(selected);
      });
    });

    // Glass Opacity Slider (Translucency Control)
    const opacitySlider = document.getElementById('glass-opacity-slider');
    const opacityVal = document.getElementById('glass-opacity-val');
    if (opacitySlider && opacityVal) {
      opacitySlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        opacityVal.textContent = `${val}%`;
        const layerGlass = document.getElementById('layer-glass');
        if (layerGlass) {
          layerGlass.style.opacity = (val / 100).toFixed(2);
        }
      });
    }
  }

  setTheme(themeName) {
    this.theme = themeName;
    document.body.className = `mode-${this.isPhoneFocus ? 'phone' : 'game'} theme-${themeName}`;
    document.querySelectorAll('.theme-tab-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.theme === themeName);
    });
  }

  // --- LAYER SWAP MECHANIC ---------------------------------------------------
  toggleLayerSwap() {
    this.isPhoneFocus = !this.isPhoneFocus;
    this.playSwapSound();
    document.body.className = `mode-${this.isPhoneFocus ? 'phone' : 'game'} theme-${this.theme}`;
  }

  // --- SINKING NOTIFICATION MECHANIC -----------------------------------------
  triggerNotification(item) {
    this.activeNotification = item;
    const card = document.getElementById('floating-notification');
    if (!card) return;

    document.getElementById('notif-badge').textContent = item.app;
    document.getElementById('notif-title').textContent = item.from;
    document.getElementById('notif-msg').textContent = item.msg;

    card.classList.remove('hidden', 'sinking');
  }

  sinkActiveNotification() {
    if (!this.activeNotification) return;
    this.playSinkSound();

    const card = document.getElementById('floating-notification');
    card.classList.add('sinking');

    // Add to Phone Screen notifications tray in Layer 1!
    setTimeout(() => {
      card.classList.add('hidden');
      const tray = document.getElementById('phone-notifications-tray');
      if (tray) {
        const sunk = document.createElement('div');
        sunk.className = 'sunk-card';
        sunk.innerHTML = `
          <div class="sunk-icon" style="background: ${this.activeNotification.color}22; color: ${this.activeNotification.color};">
            ${this.activeNotification.icon}
          </div>
          <div class="sunk-info">
            <div class="sunk-title">
              ${this.activeNotification.from}
              <span>Just now</span>
            </div>
            <div class="sunk-body">${this.activeNotification.msg}</div>
          </div>
        `;
        tray.prepend(sunk);
      }
      this.activeNotification = null;
    }, 400);
  }

  // --- SPAWN & DROP ----------------------------------------------------------
  spawnNextBlock() {
    const ink = this.rollBaseInk();
    const sizePx = ink.tier * this.unitSize;
    this.nextBlock = {
      tier: ink.tier,
      c: ink.c,
      m: ink.m,
      y: ink.y,
      size: sizePx,
      color: this.cmyToRgb(ink.c, ink.m, ink.y)
    };
  }

  takeNextBlock() {
    this.currentBlock = this.nextBlock;
    this.spawnNextBlock();
  }

  dropCurrentBlock() {
    if (!this.currentBlock || this.cooldown > 0) return;
    this.playDropSound();

    const spawnX = this.chamber.x + this.aimX * (this.chamber.w - this.currentBlock.size);
    const spawnY = this.chamber.y - 10;

    this.blocks.push({
      x: spawnX,
      y: spawnY,
      vx: 0,
      vy: 120, // initial downward push
      size: this.currentBlock.size,
      tier: this.currentBlock.tier,
      c: this.currentBlock.c,
      m: this.currentBlock.m,
      yInk: this.currentBlock.y,
      color: this.currentBlock.color,
      settled: false,
      age: 0
    });

    this.currentBlock = null;
    this.cooldown = 0.22; // delay before next block readies
    setTimeout(() => this.takeNextBlock(), 200);
  }

  // --- MAIN SIMULATION LOOP --------------------------------------------------
  loop(timestamp) {
    const dt = Math.min((timestamp - this.lastTime) / 1000.0, 0.05);
    this.lastTime = timestamp;

    if (!this.isPaused) {
      this.update(dt);
      this.render();
    }

    requestAnimationFrame((t) => this.loop(t));
  }

  update(dt) {
    if (this.cooldown > 0) this.cooldown -= dt;

    // Check notifications threshold
    if (!this.activeNotification && this.notificationsQueue.length > 0) {
      if (this.score >= this.notificationsQueue[0].score) {
        const item = this.notificationsQueue.shift();
        this.triggerNotification(item);
      }
    }

    // Step Physics
    const ch = this.chamber;
    for (let i = 0; i < this.blocks.length; i++) {
      const b = this.blocks[i];
      b.age += dt;

      // Downward gravity
      b.vy += this.gravity * dt;
      b.x += b.vx * dt;
      b.y += b.vy * dt;

      // Air resistance
      b.vx *= 0.985;
      b.vy *= 0.99;

      // Wall Collisions
      if (b.x < ch.x) {
        b.x = ch.x;
        b.vx = -b.vx * this.restitution;
      } else if (b.x + b.size > ch.x + ch.w) {
        b.x = ch.x + ch.w - b.size;
        b.vx = -b.vx * this.restitution;
      }

      // Floor Collision
      if (b.y + b.size > ch.y + ch.h) {
        b.y = ch.y + ch.h - b.size;
        b.vy = -b.vy * this.restitution;
        b.vx *= this.friction;
        if (Math.abs(b.vy) < 20) b.vy = 0;
      }
    }

    // Block-to-Block Collisions & Merging
    for (let i = 0; i < this.blocks.length; i++) {
      for (let j = i + 1; j < this.blocks.length; j++) {
        const b1 = this.blocks[i];
        const b2 = this.blocks[j];
        this.resolveBlockCollision(b1, b2, i, j);
      }
    }
  }

  // --- COLLISION & CMY MERGE RESOLVER ----------------------------------------
  resolveBlockCollision(b1, b2, idx1, idx2) {
    // AABB Overlap check
    const overlapX = (b1.size / 2 + b2.size / 2) - Math.abs((b1.x + b1.size/2) - (b2.x + b2.size/2));
    const overlapY = (b1.size / 2 + b2.size / 2) - Math.abs((b1.y + b1.size/2) - (b2.y + b2.size/2));

    if (overlapX > 0 && overlapY > 0) {
      // Check if mergeable: Identical Tier!
      if (b1.tier === b2.tier && b1.tier < 11) {
        this.mergeBlocks(idx1, idx2);
        return;
      }

      // Solid Box Pushout Collision
      if (overlapX < overlapY) {
        const sign = (b1.x + b1.size/2) < (b2.x + b2.size/2) ? -1 : 1;
        b1.x += (overlapX / 2) * sign;
        b2.x -= (overlapX / 2) * sign;
        const tempVx = b1.vx;
        b1.vx = b2.vx * this.restitution;
        b2.vx = tempVx * this.restitution;
      } else {
        const sign = (b1.y + b1.size/2) < (b2.y + b2.size/2) ? -1 : 1;
        b1.y += (overlapY / 2) * sign;
        b2.y -= (overlapY / 2) * sign;
        const tempVy = b1.vy;
        b1.vy = b2.vy * this.restitution;
        b2.vy = tempVy * this.restitution;
      }
    }
  }

  mergeBlocks(idx1, idx2) {
    const b1 = this.blocks[idx1];
    const b2 = this.blocks[idx2];

    const nextTier = b1.tier + 1;
    // Subtractive CMY Combination: C = c1 + c2, M = m1 + m2, Y = y1 + y2
    const nextC = Math.min(1.0, b1.c + b2.c);
    const nextM = Math.min(1.0, b1.m + b2.m);
    const nextY = Math.min(1.0, b1.yInk + b2.yInk);
    const nextColor = this.cmyToRgb(nextC, nextM, nextY);

    // Midpoint spawn
    const midX = (b1.x + b2.x) / 2;
    const midY = (b1.y + b2.y) / 2;
    const nextSize = nextTier * this.unitSize;

    // Remove parents
    this.blocks.splice(Math.max(idx1, idx2), 1);
    this.blocks.splice(Math.min(idx1, idx2), 1);

    // Spawn child
    this.blocks.push({
      x: midX,
      y: midY,
      vx: 0,
      vy: -60, // slight merge hop
      size: nextSize,
      tier: nextTier,
      c: nextC,
      m: nextM,
      yInk: nextY,
      color: nextColor,
      settled: false,
      age: 0
    });

    // Score & Blackness Tracking
    this.score += nextTier * 50;
    this.highestTier = Math.max(this.highestTier, nextTier);
    const currentBlack = Math.round(Math.min(nextC, nextM, nextY) * 100);
    this.peakBlackness = Math.max(this.peakBlackness, currentBlack);

    this.playMergeSound(nextTier);
    this.updateHUD();
  }

  updateHUD() {
    document.getElementById('hud-score-val').textContent = this.score.toLocaleString();
    document.getElementById('hud-tier-val').textContent = `TIER ${this.highestTier}`;
    document.getElementById('hud-black-val').textContent = `${this.peakBlackness}%`;
  }

  // --- TRANSPARENT RENDERING -------------------------------------------------
  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const limitY = this.chamber.y + 6 * this.unitSize;

    // 0. Draw Limit / Overflow Danger Line
    this.ctx.save();
    if (this.theme === 'sumi') {
      // Cinnabar red brushstroke limit line
      this.ctx.fillStyle = '#b83b26';
      this.ctx.fillRect(this.chamber.x, limitY - 1.5, this.chamber.w, 3);
      this.ctx.fillStyle = 'rgba(184, 59, 38, 0.75)';
      this.ctx.font = 'bold 10px serif';
      this.ctx.textAlign = 'right';
      this.ctx.fillText('朱 DENSITY LIMIT', this.chamber.x + this.chamber.w - 8, limitY - 6);
    } else if (this.theme === 'amber_crt') {
      // Dashed amber phosphor CRT warning line
      this.ctx.setLineDash([6, 4]);
      this.ctx.strokeStyle = '#ffb000';
      this.ctx.lineWidth = 1.5;
      this.ctx.beginPath();
      this.ctx.moveTo(this.chamber.x, limitY);
      this.ctx.lineTo(this.chamber.x + this.chamber.w, limitY);
      this.ctx.stroke();
      this.ctx.setLineDash([]);
      this.ctx.fillStyle = '#ffb000';
      this.ctx.font = '10px "JetBrains Mono", monospace';
      this.ctx.textAlign = 'right';
      this.ctx.fillText('[DANGER_LIMIT]', this.chamber.x + this.chamber.w - 8, limitY - 6);
    } else if (this.theme === 'nordic') {
      // Recessed optical red LED bar
      this.ctx.fillStyle = 'rgba(235, 60, 60, 0.85)';
      this.ctx.fillRect(this.chamber.x, limitY, this.chamber.w, 2);
      this.ctx.fillStyle = '#8b949e';
      this.ctx.font = '700 9px "JetBrains Mono", sans-serif';
      this.ctx.textAlign = 'right';
      this.ctx.fillText('LIMIT', this.chamber.x + this.chamber.w - 8, limitY - 6);
    } else {
      // Classic dashed line
      this.ctx.setLineDash([4, 4]);
      this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.moveTo(this.chamber.x, limitY);
      this.ctx.lineTo(this.chamber.x + this.chamber.w, limitY);
      this.ctx.stroke();
      this.ctx.setLineDash([]);
    }
    this.ctx.restore();

    // 1. Draw Dropper Guide Line & Ready Block
    if (this.currentBlock) {
      const dropX = this.chamber.x + this.aimX * (this.chamber.w - this.currentBlock.size) + (this.currentBlock.size / 2);
      const topY = this.chamber.y - 40;

      // Guide Line
      this.ctx.save();
      this.ctx.beginPath();
      if (this.theme === 'sumi') {
        this.ctx.strokeStyle = 'rgba(30, 25, 20, 0.55)';
        this.ctx.lineWidth = 1.2;
      } else if (this.theme === 'amber_crt') {
        this.ctx.setLineDash([3, 3]);
        this.ctx.strokeStyle = 'rgba(255, 176, 0, 0.5)';
        this.ctx.lineWidth = 1.2;
      } else if (this.theme === 'nordic') {
        this.ctx.strokeStyle = 'rgba(200, 210, 220, 0.4)';
        this.ctx.lineWidth = 1;
      } else {
        this.ctx.setLineDash([4, 4]);
        this.ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
        this.ctx.lineWidth = 1.5;
      }
      this.ctx.moveTo(dropX, topY + 20);
      this.ctx.lineTo(dropX, this.chamber.y + this.chamber.h);
      this.ctx.stroke();
      this.ctx.restore();

      // Ready Block at dropper
      this.renderBlock(dropX - this.currentBlock.size / 2, topY, this.currentBlock.size, this.currentBlock.color, this.currentBlock.tier);
    }

    // 2. Draw Stacked Blocks
    for (const b of this.blocks) {
      this.renderBlock(b.x, b.y, b.size, b.color, b.tier);
    }
  }

  renderBlock(x, y, size, color, tier) {
    if (this.theme === 'sumi') {
      this.renderSumiBlock(x, y, size, tier);
    } else if (this.theme === 'amber_crt') {
      this.renderCrtBlock(x, y, size, tier);
    } else if (this.theme === 'nordic') {
      this.renderNordicBlock(x, y, size, tier);
    } else {
      this.render3DCube(x, y, size, color, tier);
    }
  }

  // --- THEME 1: SUMI INK & MINERAL STONE ------------------------------------
  renderSumiBlock(x, y, size, tier) {
    const ctx = this.ctx;
    const sumiColors = [
      '', '#cfa856', '#b83b26', '#2a4b7c', '#202c4b',
      '#2f6345', '#5c3a21', '#3a3d45', '#252528', '#18181b', '#0d0d0f', '#050505'
    ];
    const fill = sumiColors[Math.min(tier, 11)];

    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 4;

    // Base rough stone
    ctx.fillStyle = fill;
    ctx.beginPath();
    ctx.roundRect(x, y, size, size, 4);
    ctx.fill();
    ctx.restore();

    // Natural stone texture / gold rim for monolith
    if (tier >= 11) {
      ctx.strokeStyle = '#d4af37'; // Raw gold leaf rim
      ctx.lineWidth = 2.5;
      ctx.strokeRect(x, y, size, size);
    } else {
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.35)';
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, size, size);
    }

    // Ink calligraphic numeral
    ctx.fillStyle = (tier === 1 ? '#2b2112' : '#f5f0e6');
    ctx.font = `bold ${Math.max(12, Math.floor(size * 0.36))}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(tier.toString(), x + size / 2, y + size / 2);
  }

  // --- THEME 2: AMBER PHOSPHOR CRT TERMINAL ----------------------------------
  renderCrtBlock(x, y, size, tier) {
    const ctx = this.ctx;
    const alpha = 0.08 + Math.min(tier, 11) * 0.05;

    ctx.save();
    // Warm phosphor glow
    ctx.shadowColor = '#ffb000';
    ctx.shadowBlur = tier >= 11 ? 14 : 7;

    // Glowing phosphor fill
    ctx.fillStyle = `rgba(255, 176, 0, ${alpha})`;
    ctx.fillRect(x, y, size, size);

    // Sharp phosphor wireframe outline
    ctx.strokeStyle = '#ffb000';
    ctx.lineWidth = tier >= 11 ? 2.5 : 1.5;
    ctx.strokeRect(x, y, size, size);
    ctx.restore();

    // Internal wireframe grid
    if (tier > 1) {
      ctx.strokeStyle = 'rgba(255, 176, 0, 0.35)';
      ctx.lineWidth = 1;
      const cellPx = size / tier;
      for (let c = 1; c < tier; c++) {
        ctx.beginPath();
        ctx.moveTo(x + c * cellPx, y);
        ctx.lineTo(x + c * cellPx, y + size);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y + c * cellPx);
        ctx.lineTo(x + size, y + c * cellPx);
        ctx.stroke();
      }
    }

    // Dot matrix / CRT Monospace numeral
    ctx.fillStyle = '#ffb000';
    ctx.font = `bold ${Math.max(11, Math.floor(size * 0.32))}px "JetBrains Mono", monospace`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`[${tier}]`, x + size / 2, y + size / 2);
  }

  // --- THEME 3: NORDIC BRUTALISM & HONED OBSIDIAN ----------------------------
  renderNordicBlock(x, y, size, tier) {
    const ctx = this.ctx;
    const nordicColors = [
      '', '#b55b3d', '#4a4e54', '#878c90', '#bcc2c7',
      '#383d42', '#26292c', '#1e1f22', '#18191b', '#121315', '#0a0a0c', '#000000'
    ];
    const fill = nordicColors[Math.min(tier, 11)];

    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 6;

    // Chamfered stone / obsidian monolith
    ctx.fillStyle = fill;
    ctx.fillRect(x, y, size, size);
    ctx.restore();

    // Specular Chamfer Rim
    ctx.strokeStyle = (tier >= 11 ? 'rgba(255, 255, 255, 0.45)' : 'rgba(255, 255, 255, 0.12)');
    ctx.lineWidth = (tier >= 11 ? 1.8 : 1);
    ctx.strokeRect(x, y, size, size);

    // Architectural Subdivisions
    if (tier > 1) {
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
      ctx.lineWidth = 1;
      const cellPx = size / tier;
      for (let c = 1; c < tier; c++) {
        ctx.beginPath();
        ctx.moveTo(x + c * cellPx, y);
        ctx.lineTo(x + c * cellPx, y + size);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y + c * cellPx);
        ctx.lineTo(x + size, y + c * cellPx);
        ctx.stroke();
      }
    }

    // Laser-etched typography
    ctx.fillStyle = (tier >= 11 ? '#ffffff' : (tier === 1 ? '#ffffff' : '#e6edf3'));
    ctx.font = `700 ${Math.max(11, Math.floor(size * 0.32))}px "Plus Jakarta Sans", -apple-system, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(tier.toString(), x + size / 2, y + size / 2);
  }

  // 3D Beveled Cube Renderer
  render3DCube(x, y, size, color, tier) {
    const ctx = this.ctx;
    const r = 4; // corner radius
    const bevel = Math.max(2, Math.floor(size * 0.08));

    // Outer Drop Shadow
    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.45)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetX = 3;
    ctx.shadowOffsetY = 5;

    // Main Cube Base
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect(x, y, size, size, r);
    ctx.fill();
    ctx.restore();

    // Top & Left Specular Bevel (Glossy reflection)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + size, y);
    ctx.lineTo(x + size - bevel, y + bevel);
    ctx.lineTo(x + bevel, y + bevel);
    ctx.lineTo(x + bevel, y + size - bevel);
    ctx.lineTo(x, y + size);
    ctx.closePath();
    ctx.fill();

    // Bottom & Right Inner Shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    ctx.beginPath();
    ctx.moveTo(x + size, y);
    ctx.lineTo(x + size, y + size);
    ctx.lineTo(x, y + size);
    ctx.lineTo(x + bevel, y + size - bevel);
    ctx.lineTo(x + size - bevel, y + size - bevel);
    ctx.lineTo(x + size - bevel, y + bevel);
    ctx.closePath();
    ctx.fill();

    // Sub-grid Lines for larger multi-cell blocks (N x N)
    if (tier > 1) {
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.25)';
      ctx.lineWidth = 1;
      const cellPx = size / tier;
      for (let c = 1; c < tier; c++) {
        // Vertical divider
        ctx.beginPath();
        ctx.moveTo(x + c * cellPx, y + bevel);
        ctx.lineTo(x + c * cellPx, y + size - bevel);
        ctx.stroke();
        // Horizontal divider
        ctx.beginPath();
        ctx.moveTo(x + bevel, y + c * cellPx);
        ctx.lineTo(x + size - bevel, y + c * cellPx);
        ctx.stroke();
      }
    }

    // Number Label in center
    ctx.fillStyle = (tier === 11 || color === 'rgb(0, 0, 0)') ? '#ffffff' : '#ffffff';
    ctx.font = `bold ${Math.max(11, Math.floor(size * 0.32))}px "JetBrains Mono", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
    ctx.shadowBlur = 4;
    ctx.fillText(tier.toString(), x + size / 2, y + size / 2);
    ctx.shadowBlur = 0;
  }
}

// Instantiate on Load
window.addEventListener('DOMContentLoaded', () => {
  window.darkness = new DarknessGame();
});

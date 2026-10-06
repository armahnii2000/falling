// A.I.r Bubbles — n×n Grid Edition Game Controller
// Implements full inverted buoyancy, 12-tier grid bubbles, temperature rules,
// Lake Ellem score reservoir, and tactile push-out dynamics.

const TIERS = [
  { tier: 1,  name: "Photon",       sub: "Primary Spark" },
  { tier: 2,  name: "Chroma",       sub: "Dual Spectrum" },
  { tier: 3,  name: "Prism",        sub: "Tri-Color Mix" },
  { tier: 4,  name: "Spectra",      sub: "Harmonic Wave" },
  { tier: 5,  name: "Lumen",        sub: "Amplified Light" },
  { tier: 6,  name: "Candela",      sub: "Focused Beam" },
  { tier: 7,  name: "Aurora",       sub: "Atmospheric Glow" },
  { tier: 8,  name: "Corona",       sub: "Stellar Halo" },
  { tier: 9,  name: "Helios",       sub: "Solar Core" },
  { tier: 10, name: "Supernova",    sub: "Radiant Burst" },
  { tier: 11, name: "Quasar",       sub: "Hyperluminal Apex" },
  { tier: 12, name: "White Singularity", sub: "100% Equilibrium" }
];

class AirBubbleGame {
  constructor() {
    this.canvas = document.getElementById('game-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.nextCanvas = document.getElementById('next-canvas');
    this.nextCtx = this.nextCanvas.getContext('2d');

    this.physics = new window.PhysicsEngine();
    this.sound = window.soundEngine;

    // Game state
    this.score = 0;
    this.blocksLaunched = 0;
    this.combo = 1;
    this.lastMergeTime = 0;
    this.comboWindow = 0.95; // seconds
    this.totalMerges = 0;
    this.peakTier = 1;
    this.isGameOver = false;
    this.isWon = false;
    this.isPaused = false;
    this.dangerTimer = 3.0;
    this.settleTimer = 0.0;

    // RGB Chromatic Equilibrium State
    this.cumulativeR = 0;
    this.cumulativeG = 0;
    this.cumulativeB = 0;
    this.bestBalance = 0;
    this.bestBalanceTier = 1;
    this.whiteBubblesCreated = 0;

    // Launcher state
    this.launcherX = 0;
    this.aimPercent = 50;
    this.launchCooldown = 0;
    this.readyBubble = null;
    this.nextBubble = null;

    // Visuals & Effects
    this.particles = [];
    this.popups = [];
    this.shockwaves = [];
    this.cameraTrauma = 0;
    this.gameTime = 0;

    // UI elements
    this.uiScore = document.getElementById('val-score');
    this.uiCombo = document.getElementById('val-combo');
    this.uiPressure = document.getElementById('val-pressure');
    this.uiPressureStatus = document.getElementById('val-pressure-status');
    this.uiBlocks = document.getElementById('val-blocks');
    this.uiPushCounter = document.getElementById('push-counter');
    this.uiDangerBanner = document.getElementById('danger-banner');
    this.uiDangerTimer = document.getElementById('danger-timer-val');
    this.sliderWrap = document.getElementById('slider-wrap');
    this.aimSlider = document.getElementById('aim-slider');
    this.btnLaunch = document.getElementById('btn-launch');

    this.init();
  }

  init() {
    this.resize();
    window.addEventListener('resize', () => this.resize());

    // Roll initial bubbles
    this.readyBubble = this.rollSpawn();
    this.nextBubble = this.rollSpawn();

    this.setupInputs();
    this.setupUI();
    this.renderEvolutionStrip();
    this.renderNextPreview();
    this.generateQRCode();

    // Start loop
    let lastT = performance.now();
    const loop = (now) => {
      const dt = Math.min((now - lastT) / 1000, 0.05);
      lastT = now;
      this.update(dt);
      this.render();
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = Math.floor(rect.width * dpr);
    this.canvas.height = Math.floor(rect.height * dpr);
    this.ctx.resetTransform?.();
    this.ctx.scale(dpr, dpr);

    this.viewWidth = rect.width;
    this.viewHeight = rect.height;

    this.physics.updateDimensions(this.viewWidth, this.viewHeight);
    this.updateSliderAlignment();
    this.updateLauncherPos();
  }

  // Exactly align the slider and launch button with the grid chamber width and position
  updateSliderAlignment() {
    const chamber = this.physics.chamber;
    if (this.sliderWrap) {
      this.sliderWrap.style.width = `${chamber.w}px`;
      this.sliderWrap.style.marginLeft = `${chamber.x}px`;
    }
    if (this.btnLaunch) {
      this.btnLaunch.style.width = `${chamber.w}px`;
      this.btnLaunch.style.marginLeft = `${chamber.x}px`;
    }
  }

  getBubbleColor(b) {
    const r = (b && b.r) || 0;
    const g = (b && b.g) || 0;
    const bVal = (b && b.b) || 0;
    const max = Math.max(r, g, bVal);

    if (max === 0) {
      return {
        css: '#888888',
        glow: 'rgba(255,255,255,0.2)',
        border: 'rgba(255,255,255,0.4)',
        text: '#ffffff',
        balance: 0,
        isWhite: false,
        R: 128, G: 128, B: 128,
        colorName: 'Void'
      };
    }

    // Optical RGB light mix: scaled relative to dominant channel
    const R = Math.round((r / max) * 255);
    const G = Math.round((g / max) * 255);
    const B = Math.round((bVal / max) * 255);

    const min = Math.min(r, g, bVal);
    // Chromatic Balance / Whiteness percentage:
    // When min == max (and min > 0), all 3 channels are identical -> 100% White!
    const balance = Math.round((min / max) * 100);
    const isWhite = (balance >= 95 && r > 0 && g > 0 && bVal > 0);

    // Perceived luminance for high-contrast legible text
    const lum = (0.299 * R + 0.587 * G + 0.114 * B) / 255;
    const text = lum > 0.62 ? '#060d1b' : '#ffffff';

    let colorName = '';
    if (isWhite) {
      colorName = 'White Light';
    } else if (r > 0 && g === 0 && bVal === 0) {
      colorName = 'Pure Red';
    } else if (g > 0 && r === 0 && bVal === 0) {
      colorName = 'Pure Green';
    } else if (bVal > 0 && r === 0 && g === 0) {
      colorName = 'Pure Blue';
    } else if (r === g && bVal === 0) {
      colorName = 'Yellow (R+G)';
    } else if (r === bVal && g === 0) {
      colorName = 'Magenta (R+B)';
    } else if (g === bVal && r === 0) {
      colorName = 'Cyan (G+B)';
    } else if (balance >= 75) {
      colorName = 'Near-White';
    } else if (r >= g && r >= bVal) {
      colorName = g > bVal ? 'Warm Amber' : 'Rose Violet';
    } else if (g >= r && g >= bVal) {
      colorName = r > bVal ? 'Lime Green' : 'Aquamarine';
    } else {
      colorName = r > g ? 'Deep Violet' : 'Electric Cyan';
    }

    return {
      css: `rgb(${R}, ${G}, ${B})`,
      glow: isWhite ? 'rgba(255, 255, 255, 0.95)' : `rgba(${R}, ${G}, ${B}, 0.85)`,
      border: isWhite ? '#ffffff' : (balance > 60 ? 'rgba(255, 255, 255, 0.9)' : `rgba(${Math.min(255, R + 50)}, ${Math.min(255, G + 50)}, ${Math.min(255, B + 50)}, 0.85)`),
      text: text,
      balance: balance,
      isWhite: isWhite,
      R: R,
      G: G,
      B: B,
      rCount: r,
      gCount: g,
      bCount: bVal,
      colorName: colorName
    };
  }

  rollSpawnTier() {
    const r = Math.random() * 100;
    if (r < 55) return 1;
    if (r < 85) return 2;
    return 3;
  }

  rollSpawnColor() {
    const r = Math.random();
    if (r < 0.3333) return 'red';
    if (r < 0.6666) return 'green';
    return 'blue';
  }

  rollSpawn() {
    const tier = this.rollSpawnTier();
    const color = this.rollSpawnColor();
    return {
      tier: tier,
      colorName: color,
      r: color === 'red' ? tier : 0,
      g: color === 'green' ? tier : 0,
      b: color === 'blue' ? tier : 0
    };
  }

  updateLauncherPos() {
    const chamber = this.physics.chamber;
    const currentTier = this.readyBubble ? this.readyBubble.tier : 1;
    const halfWidth = (currentTier * this.physics.cellSize) / 2;
    const minX = chamber.x + halfWidth + 4;
    const maxX = chamber.x + chamber.w - halfWidth - 4;
    this.launcherX = minX + (this.aimPercent / 100) * (maxX - minX);
  }

  setupInputs() {
    // Slider aiming
    this.aimSlider.addEventListener('input', (e) => {
      this.aimPercent = parseFloat(e.target.value);
      this.updateLauncherPos();
    });

    // Touch & Mouse drag directly on canvas
    let isDragging = false;
    const handlePointerMove = (clientX) => {
      const rect = this.canvas.getBoundingClientRect();
      const relX = clientX - rect.left;
      const chamber = this.physics.chamber;
      const pct = ((relX - chamber.x) / chamber.w) * 100;
      this.aimPercent = Math.max(0, Math.min(100, pct));
      this.aimSlider.value = this.aimPercent;
      this.updateLauncherPos();
    };

    this.canvas.addEventListener('pointerdown', (e) => {
      if (this.isGameOver) return;
      isDragging = true;
      handlePointerMove(e.clientX);
    });

    window.addEventListener('pointermove', (e) => {
      if (isDragging) {
        handlePointerMove(e.clientX);
      }
    });

    window.addEventListener('pointerup', () => {
      if (isDragging) {
        isDragging = false;
      }
    });

    // Launch button
    this.btnLaunch.addEventListener('click', () => {
      this.launchCurrentBubble();
    });

    // Keyboard support
    window.addEventListener('keydown', (e) => {
      if (this.isGameOver) {
        if (e.key === 'r' || e.key === 'R') this.restart();
        return;
      }
      if (e.key === 'ArrowLeft' || e.key === 'a') {
        this.aimPercent = Math.max(0, this.aimPercent - 5);
        this.aimSlider.value = this.aimPercent;
        this.updateLauncherPos();
      } else if (e.key === 'ArrowRight' || e.key === 'd') {
        this.aimPercent = Math.min(100, this.aimPercent + 5);
        this.aimSlider.value = this.aimPercent;
        this.updateLauncherPos();
      } else if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w') {
        this.launchCurrentBubble();
      } else if (e.key === 'r' || e.key === 'R') {
        this.restart();
      }
    });
  }

  setupUI() {
    // Sound button
    const btnSound = document.getElementById('btn-sound');
    btnSound.addEventListener('click', () => {
      const muted = this.sound.toggleMute();
      btnSound.textContent = muted ? '🔇' : '🔊';
    });

    // Restart button
    document.getElementById('btn-restart').addEventListener('click', () => this.restart());
    document.getElementById('btn-modal-restart').addEventListener('click', () => this.restart());

    // Info modal
    const infoModal = document.getElementById('info-modal');
    document.getElementById('btn-info').addEventListener('click', () => {
      infoModal.classList.remove('hidden');
    });
    document.getElementById('btn-close-info').addEventListener('click', () => {
      infoModal.classList.add('hidden');
    });

    // Mode buttons (Grid vs Circle)
    const modeButtons = document.querySelectorAll('.seg-btn');
    modeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        modeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.physics.mode = btn.dataset.mode;
      });
    });
  }

  launchCurrentBubble() {
    if (this.isGameOver || this.isWon || this.launchCooldown > 0 || !this.readyBubble) return;

    this.blocksLaunched++;
    this.sound.playLaunch();
    this.launchCooldown = 0.18;

    const chamber = this.physics.chamber;
    const ventLength = 28; // Doubled length vent
    const spawnY = chamber.y + chamber.h - ventLength - 4 - (this.readyBubble.tier * this.physics.cellSize) / 2;

    const b = this.physics.createBubble(
      this.readyBubble.tier,
      {
        r: this.readyBubble.r,
        g: this.readyBubble.g,
        b: this.readyBubble.b,
        colorName: this.readyBubble.colorName
      },
      this.launcherX,
      spawnY,
      -820 // Upward launch speed
    );
    this.physics.bubbles.push(b);

    // Camera punch
    this.cameraTrauma = Math.min(1.0, this.cameraTrauma + 0.15);

    // Spawn launcher bubbles at elongated vent nozzle tip using bubble color
    const colorInfo = this.getBubbleColor(this.readyBubble);
    const moteColor = colorInfo.glow;

    for (let i = 0; i < 8; i++) {
      this.particles.push({
        x: this.launcherX + (Math.random() - 0.5) * 18,
        y: chamber.y + chamber.h - ventLength,
        vx: (Math.random() - 0.5) * 70,
        vy: -150 - Math.random() * 160,
        r: 2 + Math.random() * 3,
        color: moteColor,
        life: 0.45
      });
    }

    // Shift next to ready, and roll new next
    this.readyBubble = this.nextBubble;
    this.nextBubble = this.rollSpawn();
    this.updateLauncherPos();
    this.renderNextPreview();
  }

  onMerge(b1, b2) {
    const nextTier = b1.tier + 1;
    this.totalMerges++;
    this.peakTier = Math.max(this.peakTier, nextTier);

    // 1. Combo calculation (0.95s window)
    if (this.gameTime - this.lastMergeTime <= this.comboWindow) {
      this.combo++;
    } else {
      this.combo = 1;
    }
    this.lastMergeTime = this.gameTime;

    // 2. Cumulative RGB Unit Addition (Color Inheritance)
    const newR = (b1.r || 0) + (b2.r || 0);
    const newG = (b1.g || 0) + (b2.g || 0);
    const newB = (b1.b || 0) + (b2.b || 0);

    // Global gauge harvest addition
    this.cumulativeR += (b1.r || 0) + (b2.r || 0);
    this.cumulativeG += (b1.g || 0) + (b2.g || 0);
    this.cumulativeB += (b1.b || 0) + (b2.b || 0);

    // Evaluate color & chromatic equilibrium
    const colorInfo = this.getBubbleColor({ r: newR, g: newG, b: newB });

    // Track best white equilibrium
    if (colorInfo.balance > this.bestBalance || (colorInfo.balance === this.bestBalance && nextTier > this.bestBalanceTier)) {
      this.bestBalance = colorInfo.balance;
      this.bestBalanceTier = nextTier;
    }
    if (colorInfo.isWhite) {
      this.whiteBubblesCreated++;
    }

    // 3. Score calculation: resulting tier * combo + Whiteness Purity Bonus
    const basePts = nextTier * this.combo * 10;
    const whitenessMult = 1.0 + (colorInfo.balance / 100) * 2.0; // Up to 3x multiplier for pure white!
    const pts = Math.round(basePts * whitenessMult);
    this.score += pts;

    // Audio chime: Celestial harmony if pure white, else regular harmonic scale
    if (colorInfo.isWhite) {
      this.sound.playWhiteEquilibriumChime();
    } else {
      this.sound.playMerge(nextTier, this.combo);
    }

    // Midpoint
    const midX = (b1.x + b2.x) / 2;
    const midY = (b1.y + b2.y) / 2;

    // Remove old bubbles
    this.physics.bubbles = this.physics.bubbles.filter(b => b.id !== b1.id && b.id !== b2.id);

    // 4. Spawn new (n+1) bubble with inherited RGB counts
    const newBubble = this.physics.createBubble(
      nextTier,
      { r: newR, g: newG, b: newB },
      midX,
      midY,
      (b1.vy + b2.vy) * 0.4
    );
    newBubble.wobbleX = 1.35; // Expand spring
    this.physics.bubbles.push(newBubble);

    // 5. THE KEY PUSH-OUT MECHANIC
    this.physics.applyPushOut(newBubble);

    // Visual shockwave in merged color
    this.shockwaves.push({
      x: midX,
      y: midY,
      r: newBubble.size / 2,
      maxR: newBubble.size * 1.8,
      color: colorInfo.isWhite ? '#ffffff' : colorInfo.css,
      life: colorInfo.isWhite ? 0.6 : 0.35,
      maxLife: colorInfo.isWhite ? 0.6 : 0.35
    });

    // Score Popup
    const comboText = this.combo > 1 ? ` COMBO x${this.combo}!` : '';
    let popText = `+${pts}${comboText}`;
    let popColor = '#ffd700';

    if (colorInfo.isWhite) {
      popText = `+${pts} ⚪ PURE WHITE! (100%)`;
      popColor = '#ffffff';
    } else if (colorInfo.balance >= 50) {
      popText = `+${pts} ☀️ EQUILIBRIUM (${colorInfo.balance}%)`;
      popColor = '#00e5ff';
    }

    this.popups.push({
      x: midX,
      y: midY - 20,
      text: popText,
      color: popColor,
      size: colorInfo.isWhite ? 20 : (nextTier >= 10 ? 18 : 15),
      life: colorInfo.isWhite ? 1.4 : 1.0
    });

    // Camera trauma
    this.cameraTrauma = Math.min(1.0, this.cameraTrauma + (colorInfo.isWhite ? 0.5 : 0.25) + (nextTier * 0.04));

    // Particle fountain to Lake Ellem using bubble's authentic color
    const particleCount = colorInfo.isWhite ? 35 + nextTier * 3 : 12 + nextTier * 2;
    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        x: midX + (Math.random() - 0.5) * 20,
        y: midY + (Math.random() - 0.5) * 20,
        vx: (Math.random() - 0.5) * (colorInfo.isWhite ? 240 : 160),
        vy: -100 - Math.random() * (colorInfo.isWhite ? 280 : 200),
        r: colorInfo.isWhite ? 3 + Math.random() * 5 : 2.5 + Math.random() * 3,
        color: colorInfo.isWhite ? (i % 2 === 0 ? '#ffffff' : '#ffd700') : colorInfo.css,
        life: 0.6 + Math.random() * 0.5
      });
    }

    // Check Victory (e.g. Tier 8+ with >= 90% white balance, or Tier 12 Singularity)
    if (nextTier >= 8 && colorInfo.balance >= 90 && !this.isWon && !this.isGameOver) {
      this.triggerWhiteVictory(newBubble, colorInfo);
      return;
    }
  }

  // SIZE 12 SINGULARITY BURST / DISAPPEAR
  onSingularityPop(b) {
    this.sound.playSingularity();
    this.cameraTrauma = 1.0;

    // Massive score bonus
    const pts = 144 * this.combo;
    this.score += pts;

    this.popups.push({
      x: b.x,
      y: b.y,
      text: `+${pts} SINGULARITY BURST!`,
      color: '#ffffff',
      size: 24,
      life: 1.8
    });

    // 50 gold & prismatic fireworks particles
    for (let i = 0; i < 50; i++) {
      const angle = (Math.PI * 2 * i) / 50;
      const spd = 200 + Math.random() * 300;
      this.particles.push({
        x: b.x,
        y: b.y,
        vx: Math.cos(angle) * spd,
        vy: Math.sin(angle) * spd,
        r: 4 + Math.random() * 4,
        color: (i % 2 === 0) ? '#ffd700' : '#ffffff',
        life: 1.2
      });
    }

    // Shockwave
    this.shockwaves.push({
      x: b.x,
      y: b.y,
      r: 20,
      maxR: this.physics.chamber.w * 0.9,
      color: '#ffffff',
      life: 0.6,
      maxLife: 0.6
    });
  }

  triggerWhiteVictory(b, colorInfo) {
    this.isWon = true;
    this.isGameOver = true;
    this.sound.playWhiteEquilibriumChime();
    this.cameraTrauma = 0.85;

    const chamber = this.physics.chamber;
    for (let i = 0; i < 80; i++) {
      const angle = (Math.PI * 2 * i) / 80;
      const spd = 160 + Math.random() * 320;
      this.particles.push({
        x: b.x,
        y: b.y,
        vx: Math.cos(angle) * spd,
        vy: Math.sin(angle) * spd,
        r: 3 + Math.random() * 5,
        color: ['#ffffff', '#00e5ff', '#ffd700', '#ff3838', '#30d158'][i % 5],
        life: 1.8
      });
    }

    const badge = document.getElementById('game-over-badge');
    badge.textContent = `WHITE EQUILIBRIUM ACHIEVED (${colorInfo.balance}%)`;
    badge.style.background = 'rgba(255, 255, 255, 0.25)';
    badge.style.borderColor = '#ffffff';
    badge.style.color = '#ffffff';
    document.getElementById('game-over-title').textContent = 'Pure White Light Synthesized!';
    document.getElementById('game-over-desc').textContent = `Magnificent achievement! You cultivated a giant Tier ${b.tier} bubble with ${colorInfo.balance}% White light equilibrium across ${this.blocksLaunched} launches.`;
    this.showGameOverModal();
  }

  triggerOverflow() {
    this.isGameOver = true;
    this.sound.playOverheat();
    this.cameraTrauma = 0.8;

    const badge = document.getElementById('game-over-badge');
    badge.textContent = 'VENT OVERFLOW';
    badge.style.background = 'rgba(255, 69, 58, 0.2)';
    badge.style.borderColor = '#ff453a';
    badge.style.color = '#ff453a';
    document.getElementById('game-over-title').textContent = 'The Chamber Has Jammed';
    document.getElementById('game-over-desc').textContent = `Bubbles stacked down past the seabed danger line for over 3 seconds. Peak balance achieved: ${this.bestBalance}% on Tier ${this.bestBalanceTier}.`;
    this.showGameOverModal();
  }

  showGameOverModal() {
    document.getElementById('modal-final-score').textContent = this.score;
    document.getElementById('modal-peak-tier').textContent = `Tier ${this.peakTier} (${TIERS[this.peakTier - 1]?.name || ''}) · ⚪ ${this.bestBalance}%`;
    document.getElementById('modal-total-merges').textContent = this.totalMerges;
    document.getElementById('modal-total-pushouts').textContent = `R:${this.cumulativeR} G:${this.cumulativeG} B:${this.cumulativeB}`;
    document.getElementById('game-over-modal').classList.remove('hidden');
  }

  restart() {
    this.isGameOver = false;
    this.isWon = false;
    this.score = 0;
    this.blocksLaunched = 0;
    this.combo = 1;
    this.totalMerges = 0;
    this.peakTier = 1;
    this.dangerTimer = 3.0;
    this.settleTimer = 0.0;
    this.cumulativeR = 0;
    this.cumulativeG = 0;
    this.cumulativeB = 0;
    this.bestBalance = 0;
    this.bestBalanceTier = 1;
    this.whiteBubblesCreated = 0;
    this.physics.bubbles = [];
    this.physics.pushoutCount = 0;
    this.particles = [];
    this.popups = [];
    this.shockwaves = [];
    this.readyBubble = this.rollSpawn();
    this.nextBubble = this.rollSpawn();

    // Prevent any browser scrolling or element offset
    window.scrollTo(0, 0);
    if (document.body) document.body.scrollTop = 0;
    if (document.documentElement) document.documentElement.scrollTop = 0;
    const app = document.getElementById('app-container');
    if (app) app.scrollTop = 0;
    const gv = document.getElementById('game-view');
    if (gv) gv.scrollTop = 0;

    // Recalculate dimensions cleanly on fresh start
    this.resize();
    this.updateLauncherPos();
    this.renderNextPreview();

    document.getElementById('game-over-modal').classList.add('hidden');
    document.getElementById('info-modal').classList.add('hidden');
    this.uiDangerBanner.classList.add('hidden');
  }

  update(dt) {
    if (this.isPaused) return;

    this.gameTime += dt;
    if (this.launchCooldown > 0) {
      this.launchCooldown -= dt;
    }

    // Step physics with merge and singularity callbacks
    if (!this.isGameOver) {
      this.physics.step(
        dt,
        (b1, b2) => this.onMerge(b1, b2),
        (b) => this.onSingularityPop(b)
      );

      // Danger Overflow logic (Rule 22)
      const isOverflowing = this.physics.getDangerOverflowing();
      if (isOverflowing) {
        this.dangerTimer -= dt;
        this.uiDangerBanner.classList.remove('hidden');
        this.uiDangerTimer.textContent = `${Math.max(0, this.dangerTimer).toFixed(1)}s`;
        if (this.dangerTimer <= 0) {
          this.triggerOverflow();
        }
      } else {
        // Relief drain 2x fast
        this.dangerTimer = Math.min(3.0, this.dangerTimer + dt * 2.0);
        if (this.dangerTimer >= 2.95) {
          this.uiDangerBanner.classList.add('hidden');
        } else {
          this.uiDangerTimer.textContent = `${this.dangerTimer.toFixed(1)}s`;
        }
      }
    }

    // Combo timer
    if (this.gameTime - this.lastMergeTime > this.comboWindow) {
      this.combo = 1;
    }

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= dt;
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }

    // Update shockwaves
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const sw = this.shockwaves[i];
      sw.life -= dt;
      const progress = 1 - (sw.life / sw.maxLife);
      sw.r = sw.r + (sw.maxR - sw.r) * progress;
      if (sw.life <= 0) {
        this.shockwaves.splice(i, 1);
      }
    }

    // Update popups
    for (let i = this.popups.length - 1; i >= 0; i--) {
      const pop = this.popups[i];
      pop.life -= dt;
      pop.y -= 30 * dt;
      if (pop.life <= 0) {
        this.popups.splice(i, 1);
      }
    }

    // Camera trauma decay
    this.cameraTrauma = Math.max(0, this.cameraTrauma - dt * 1.5);

    // Update HUD
    this.uiScore.textContent = this.score;
    this.uiCombo.textContent = this.combo > 1 ? `COMBO x${this.combo}` : 'COMBO x1';
    this.uiPushCounter.textContent = this.physics.pushoutCount;

    // Update White Equilibrium HUD
    if (this.uiPressure) {
      this.uiPressure.textContent = `⚪ ${this.bestBalance}%`;
      if (this.bestBalance >= 90) {
        this.uiPressure.style.color = '#ffffff';
        this.uiPressure.style.textShadow = '0 0 10px rgba(255, 255, 255, 0.9)';
      } else if (this.bestBalance >= 50) {
        this.uiPressure.style.color = '#00e5ff';
        this.uiPressure.style.textShadow = 'none';
      } else {
        this.uiPressure.style.color = '#ffd60a';
        this.uiPressure.style.textShadow = 'none';
      }

      if (this.uiPressureStatus) {
        this.uiPressureStatus.textContent = `PEAK: TIER ${this.bestBalanceTier}`;
      }
    }

    // Update RGB Harvest HUD
    if (this.uiBlocks) {
      this.uiBlocks.textContent = `R:${this.cumulativeR} G:${this.cumulativeG} B:${this.cumulativeB}`;
      this.uiBlocks.style.color = '#ffffff';
      const blocksSub = document.getElementById('val-blocks-sub');
      if (blocksSub) {
        const totalUnits = this.cumulativeR + this.cumulativeG + this.cumulativeB;
        blocksSub.textContent = `${totalUnits} UNITS TOTAL`;
      }
    }
  }

  render() {
    const ctx = this.ctx;
    ctx.save();

    // Camera shake
    if (this.cameraTrauma > 0) {
      const shakeAmt = Math.pow(this.cameraTrauma, 2) * 12;
      const shakeX = (Math.random() - 0.5) * shakeAmt;
      const shakeY = (Math.random() - 0.5) * shakeAmt;
      ctx.translate(shakeX, shakeY);
    }

    // Clear background
    ctx.fillStyle = '#060d1b';
    ctx.fillRect(0, 0, this.viewWidth, this.viewHeight);

    const chamber = this.physics.chamber;

    // 1. Draw Rectangular Chamber Background & Grid (Clean, no warning text on grid)
    this.renderChamber(ctx, chamber);

    // 2. Draw Vertical RGB Spectrum Gauge to the Side of the Grid
    this.renderRGBGauge(ctx, this.physics.gauge);

    // 3. Draw Bubbles
    for (const b of this.physics.bubbles) {
      this.renderBubble(ctx, b);
    }

    // 4. Draw Shockwaves
    for (const sw of this.shockwaves) {
      ctx.save();
      ctx.strokeStyle = sw.color;
      ctx.lineWidth = 3 * (sw.life / sw.maxLife);
      ctx.globalAlpha = sw.life / sw.maxLife;
      ctx.beginPath();
      ctx.arc(sw.x, sw.y, sw.r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    // 5. Draw Particles
    for (const p of this.particles) {
      ctx.save();
      ctx.fillStyle = p.color;
      ctx.globalAlpha = Math.max(0, p.life);
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // 6. Draw Launcher Vent & Ready Bubble Preview
    this.renderLauncher(ctx, chamber);

    // 7. Draw Popups
    for (const pop of this.popups) {
      ctx.save();
      ctx.fillStyle = pop.color;
      ctx.globalAlpha = Math.max(0, pop.life);
      ctx.font = `bold ${pop.size}px -apple-system, sans-serif`;
      ctx.textAlign = 'center';
      ctx.shadowColor = 'rgba(0,0,0,0.8)';
      ctx.shadowBlur = 4;
      ctx.fillText(pop.text, pop.x, pop.y);
      ctx.restore();
    }

    ctx.restore();
  }

  renderChamber(ctx, chamber) {
    // Chamber fill
    ctx.save();
    const grad = ctx.createLinearGradient(0, chamber.y, 0, chamber.y + chamber.h);
    grad.addColorStop(0, '#0a1a33');
    grad.addColorStop(1, '#050c18');
    ctx.fillStyle = grad;
    ctx.fillRect(chamber.x, chamber.y, chamber.w, chamber.h);

    // Grid lines (Discrete rectangular grid)
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.08)';
    ctx.lineWidth = 1;

    // Vertical column grid lines
    for (let c = 0; c <= this.physics.cols; c++) {
      const gx = chamber.x + c * this.physics.cellSize;
      ctx.beginPath();
      ctx.moveTo(gx, chamber.y);
      ctx.lineTo(gx, chamber.y + chamber.h);
      ctx.stroke();
    }

    // Horizontal row grid lines
    for (let r = 0; r <= this.physics.rows; r++) {
      const gy = chamber.y + r * this.physics.cellSize;
      ctx.beginPath();
      ctx.moveTo(chamber.x, gy);
      ctx.lineTo(chamber.x + chamber.w, gy);
      ctx.stroke();
    }

    // Top ceiling: Water surface wavy shimmer
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(chamber.x, chamber.y);
    for (let x = chamber.x; x <= chamber.x + chamber.w; x += 10) {
      const wave = Math.sin((x * 0.08) + this.gameTime * 4) * 2;
      ctx.lineTo(x, chamber.y + wave);
    }
    ctx.stroke();

    // Chamber borders
    ctx.strokeStyle = 'rgba(64, 128, 200, 0.4)';
    ctx.lineWidth = 2;
    ctx.strokeRect(chamber.x, chamber.y, chamber.w, chamber.h);

    // Danger line (Rule 22: subtle dashed red line with NO text on the grid)
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 59, 48, 0.65)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(chamber.x, this.physics.dangerY);
    ctx.lineTo(chamber.x + chamber.w, this.physics.dangerY);
    ctx.stroke();
    ctx.restore();

    ctx.restore();
  }

  // Vertical RGB Spectrum Gauge to the side of the grid
  renderRGBGauge(ctx, gauge) {
    if (!gauge) return;
    const gx = gauge.x;
    const gy = gauge.y;
    const gw = gauge.w;
    const gh = gauge.h;

    ctx.save();

    // 1. Gauge Frame
    ctx.fillStyle = '#081324';
    ctx.strokeStyle = 'rgba(64, 128, 200, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(gx, gy, gw, gh, 6);
    ctx.fill();
    ctx.stroke();

    // Top Header
    ctx.fillStyle = '#8b9bb4';
    ctx.font = 'bold 8px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('RGB MIX', gx + gw / 2, gy + 11);

    // 2. Prism Lamp (Global Cumulative Mixed Color Orb)
    const lampX = gx + gw / 2;
    const lampY = gy + 27;
    const lampR = Math.min(12, (gw - 12) / 2);

    const maxGlobal = Math.max(this.cumulativeR, this.cumulativeG, this.cumulativeB, 1);
    const globalR = Math.round((this.cumulativeR / maxGlobal) * 255);
    const globalG = Math.round((this.cumulativeG / maxGlobal) * 255);
    const globalB = Math.round((this.cumulativeB / maxGlobal) * 255);
    const globalMixColor = (this.cumulativeR === 0 && this.cumulativeG === 0 && this.cumulativeB === 0)
      ? '#22334d'
      : `rgb(${globalR}, ${globalG}, ${globalB})`;

    ctx.save();
    ctx.shadowColor = globalMixColor;
    ctx.shadowBlur = 12;
    ctx.fillStyle = globalMixColor;
    ctx.beginPath();
    ctx.arc(lampX, lampY, lampR, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Specular highlight on glass lens
    ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
    ctx.beginPath();
    ctx.arc(lampX - lampR * 0.35, lampY - lampR * 0.35, lampR * 0.35, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 3. Three Vertical Fluid Channels (Red, Green, Blue)
    const channelsTop = gy + 46;
    const channelsH = gh - 96;
    const colW = Math.max(6, Math.floor((gw - 18) / 3));
    const pad = 3;
    const totalColsW = colW * 3 + pad * 2;
    const startX = gx + (gw - totalColsW) / 2;

    const channels = [
      { key: 'R', count: this.cumulativeR, color: '#ff3b30', bg: 'rgba(255, 59, 48, 0.12)' },
      { key: 'G', count: this.cumulativeG, color: '#30d158', bg: 'rgba(48, 209, 88, 0.12)' },
      { key: 'B', count: this.cumulativeB, color: '#00e5ff', bg: 'rgba(0, 229, 255, 0.12)' }
    ];

    const maxCapacity = Math.max(25, maxGlobal);

    channels.forEach((ch, i) => {
      const cx = startX + i * (colW + pad);
      const cy = channelsTop;

      // Channel background slot
      ctx.fillStyle = ch.bg;
      ctx.beginPath();
      ctx.roundRect(cx, cy, colW, channelsH, 3);
      ctx.fill();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Fluid fill level
      const fillRatio = Math.min(1.0, ch.count / maxCapacity);
      const fillH = channelsH * fillRatio;
      const fillY = cy + channelsH - fillH;

      if (fillH > 0) {
        ctx.save();
        ctx.fillStyle = ch.color;
        ctx.shadowColor = ch.color;
        ctx.shadowBlur = 6;
        ctx.beginPath();
        ctx.roundRect(cx, fillY, colW, fillH, [0, 0, 3, 3]);
        ctx.fill();
        ctx.restore();
      }

      // Channel Letter Label (R, G, B) below column
      ctx.fillStyle = ch.color;
      ctx.font = 'bold 8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(ch.key, cx + colW / 2, cy + channelsH + 11);

      // Channel count number
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 7px monospace';
      ctx.fillText(`${ch.count}`, cx + colW / 2, cy + channelsH + 20);
    });

    // 4. Peak Bubble Whiteness Readout at bottom
    ctx.save();
    const balanceColor = this.bestBalance >= 90 ? '#ffffff' : (this.bestBalance >= 50 ? '#00e5ff' : '#8b9bb4');
    ctx.fillStyle = balanceColor;
    if (this.bestBalance >= 90) {
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 8;
    }
    ctx.font = 'bold 8px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`⚪ ${this.bestBalance}%`, gx + gw / 2, gy + gh - 14);

    ctx.font = 'bold 7px sans-serif';
    ctx.fillStyle = '#8b9bb4';
    ctx.fillText(`PEAK T${this.bestBalanceTier}`, gx + gw / 2, gy + gh - 4);
    ctx.restore();

    ctx.restore();
  }

  renderBubble(ctx, b) {
    const tierInfo = TIERS[b.tier - 1] || TIERS[0];
    const colorInfo = this.getBubbleColor(b);
    const isGrid = (this.physics.mode === 'grid');

    ctx.save();
    ctx.translate(b.x, b.y);
    ctx.scale(b.wobbleX, b.wobbleY);

    if (isGrid) {
      // 🟦 RENDER n×n SUBDIVIDED CHROMATIC GRID BOX
      const hw = b.hw;
      const hh = b.hh;
      const r = Math.min(6, b.hw * 0.2);

      // Chromatic glow or radiant white halo
      if (colorInfo.isWhite) {
        ctx.shadowColor = '#ffffff';
        ctx.shadowBlur = 22;
      } else {
        ctx.shadowColor = colorInfo.glow;
        ctx.shadowBlur = colorInfo.balance >= 50 ? 16 : 10;
      }

      // Box body with authentic optical mix
      ctx.fillStyle = colorInfo.css;
      ctx.beginPath();
      ctx.roundRect(-hw, -hh, b.size, b.size, r);
      ctx.fill();

      // Border: Glowing white or saturated edge
      ctx.strokeStyle = colorInfo.border;
      ctx.lineWidth = colorInfo.isWhite ? 3.0 : 1.8;
      ctx.stroke();

      // Inner n×n Sub-grid Lines
      ctx.strokeStyle = colorInfo.text === '#ffffff' ? 'rgba(255, 255, 255, 0.18)' : 'rgba(0, 0, 0, 0.18)';
      ctx.lineWidth = 1;
      const subStep = b.size / b.tier;

      for (let i = 1; i < b.tier; i++) {
        // Vertical inner lines
        ctx.beginPath();
        ctx.moveTo(-hw + i * subStep, -hh);
        ctx.lineTo(-hw + i * subStep, hh);
        ctx.stroke();

        // Horizontal inner lines
        ctx.beginPath();
        ctx.moveTo(-hw, -hh + i * subStep);
        ctx.lineTo(hw, -hh + i * subStep);
        ctx.stroke();
      }

      // Center Tier Number Badge
      ctx.fillStyle = colorInfo.text;
      ctx.font = `bold ${Math.max(10, Math.min(22, b.size * 0.42))}px -apple-system, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${b.tier}`, 0, (b.size >= 34 ? -5 : 0));

      // Chromatic balance % or name below number
      if (b.size >= 34) {
        ctx.font = `bold ${Math.max(7, Math.min(10, b.size * 0.17))}px monospace`;
        if (colorInfo.isWhite) {
          ctx.fillText('⚪ 100%', 0, b.size * 0.24);
        } else if (colorInfo.balance > 0) {
          ctx.fillText(`${colorInfo.balance}%`, 0, b.size * 0.24);
        } else {
          ctx.fillText(colorInfo.colorName, 0, b.size * 0.24);
        }
      }
    } else {
      // ⚪ RENDER CLASSIC CIRCLE
      if (colorInfo.isWhite) {
        ctx.shadowColor = '#ffffff';
        ctx.shadowBlur = 22;
      } else {
        ctx.shadowColor = colorInfo.glow;
        ctx.shadowBlur = 12;
      }

      ctx.fillStyle = colorInfo.css;
      ctx.beginPath();
      ctx.arc(0, 0, b.radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = colorInfo.border;
      ctx.lineWidth = colorInfo.isWhite ? 3.0 : 2.0;
      ctx.stroke();

      ctx.fillStyle = colorInfo.text;
      ctx.font = `bold ${Math.max(10, Math.min(20, b.radius * 0.72))}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${b.tier}`, 0, (b.radius >= 22 ? -4 : 0));

      if (b.radius >= 22) {
        ctx.font = `bold ${Math.max(7, Math.min(9, b.radius * 0.3))}px monospace`;
        ctx.fillText(colorInfo.isWhite ? '⚪ 100%' : `${colorInfo.balance}%`, 0, b.radius * 0.38);
      }
    }

    ctx.restore();
  }

  renderLauncher(ctx, chamber) {
    const lx = this.launcherX;
    const ly = chamber.y + chamber.h;
    const ventLength = 28; // Doubled length (from 14px to 28px)

    ctx.save();

    // 1. Base mount flange at seabed floor (ly)
    ctx.fillStyle = '#0f1a28';
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(lx - 28, ly - 4, 56, 6, 2);
    ctx.fill();
    ctx.stroke();

    // 2. Elongated vent column / barrel (height: 28px, doubled from 14px)
    const ventGrad = ctx.createLinearGradient(lx - 20, ly, lx + 20, ly);
    ventGrad.addColorStop(0, '#101d2d');
    ventGrad.addColorStop(0.5, '#22364c');
    ventGrad.addColorStop(1, '#101d2d');
    ctx.fillStyle = ventGrad;
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(lx - 24, ly - 2);
    ctx.lineTo(lx - 13, ly - ventLength);
    ctx.lineTo(lx + 13, ly - ventLength);
    ctx.lineTo(lx + 24, ly - 2);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // 3. Middle reinforcement collar ring (at 14px, the previous nozzle height)
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.65)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(lx - 18, ly - 13);
    ctx.lineTo(lx + 18, ly - 13);
    ctx.stroke();

    // 4. Glowing nozzle mouth opening at ly - 28
    ctx.fillStyle = '#040912';
    ctx.beginPath();
    ctx.ellipse(lx, ly - ventLength, 13, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Soft nozzle mouth glow
    ctx.save();
    ctx.shadowColor = '#00e5ff';
    ctx.shadowBlur = 8;
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.8)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(lx, ly - ventLength, 9, 2.5, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    ctx.restore();

    // Two parallel aim guide lines showing the exact width of the box
    const currentTier = this.readyBubble ? this.readyBubble.tier : 1;
    const boxWidth = currentTier * this.physics.cellSize;
    const halfWidth = boxWidth / 2;
    const previewSize = currentTier * this.physics.cellSize;
    const bob = Math.sin(this.gameTime * 4) * 2;
    const py = ly - ventLength - 4 - (previewSize / 2) + bob;
    const startY = py - (previewSize / 2);
    const targetY = chamber.y + 4;

    ctx.save();
    // 1. Subtle glowing trajectory corridor between the two lines
    ctx.fillStyle = 'rgba(0, 229, 255, 0.04)';
    ctx.fillRect(lx - halfWidth, targetY, boxWidth, Math.max(0, startY - targetY));

    // 2. Two guide lines marking the left and right edges of the box
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);

    // Left guide line
    ctx.beginPath();
    ctx.moveTo(lx - halfWidth, startY);
    ctx.lineTo(lx - halfWidth, targetY);
    ctx.stroke();

    // Right guide line
    ctx.beginPath();
    ctx.moveTo(lx + halfWidth, startY);
    ctx.lineTo(lx + halfWidth, targetY);
    ctx.stroke();

    // Subtle ceiling landing bracket
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.6)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(lx - halfWidth, targetY);
    ctx.lineTo(lx + halfWidth, targetY);
    ctx.stroke();
    ctx.restore();

    // Ready bubble preview floating right over the elongated vent nozzle
    if (this.readyBubble) {
      const colorInfo = this.getBubbleColor(this.readyBubble);

      ctx.save();
      ctx.translate(lx, py);
      ctx.globalAlpha = 0.95;

      ctx.shadowColor = colorInfo.glow;
      ctx.shadowBlur = 14;

      if (this.physics.mode === 'grid') {
        const hw = previewSize / 2;
        ctx.fillStyle = colorInfo.css;
        ctx.beginPath();
        ctx.roundRect(-hw, -hw, previewSize, previewSize, 4);
        ctx.fill();

        ctx.strokeStyle = colorInfo.border;
        ctx.lineWidth = 2.0;
        ctx.stroke();

        ctx.fillStyle = colorInfo.text;
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${this.readyBubble.tier}`, 0, 0);
      } else {
        ctx.fillStyle = colorInfo.css;
        ctx.beginPath();
        ctx.arc(0, 0, previewSize / 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = colorInfo.border;
        ctx.lineWidth = 2.0;
        ctx.stroke();

        ctx.fillStyle = colorInfo.text;
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${this.readyBubble.tier}`, 0, 0);
      }
      ctx.restore();
    }
  }

  renderNextPreview() {
    const ctx = this.nextCtx;
    ctx.clearRect(0, 0, 60, 60);
    if (!this.nextBubble) return;

    const colorInfo = this.getBubbleColor(this.nextBubble);
    const previewSize = Math.min(36, 12 + this.nextBubble.tier * 5);
    const hw = previewSize / 2;

    ctx.save();
    ctx.translate(30, 30);

    ctx.shadowColor = colorInfo.glow;
    ctx.shadowBlur = 10;
    ctx.fillStyle = colorInfo.css;

    if (this.physics.mode === 'grid') {
      ctx.beginPath();
      ctx.roundRect(-hw, -hw, previewSize, previewSize, 3);
      ctx.fill();
      ctx.strokeStyle = colorInfo.border;
      ctx.lineWidth = 2.0;
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(0, 0, hw, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = colorInfo.border;
      ctx.lineWidth = 2.0;
      ctx.stroke();
    }

    ctx.fillStyle = colorInfo.text;
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${this.nextBubble.tier}`, 0, 0);
    ctx.restore();
  }

  renderEvolutionStrip() {
    const container = document.getElementById('evo-scroll-container');
    if (!container) return;
    container.innerHTML = '';
    const evoExamples = [
      { tier: 1, name: "🔴/🟢/🔵 Primary", color: "#ff3b30", text: "#ffffff" },
      { tier: 2, name: "🟡/🟣/🔷 Dual Mix", color: "#ffd60a", text: "#060d1b" },
      { tier: 3, name: "🌈 Tri-Chroma", color: "#c56cf0", text: "#ffffff" },
      { tier: 4, name: "☀️ Harmonic", color: "#ff9f1a", text: "#060d1b" },
      { tier: 5, name: "💎 Prism Lumen", color: "#00e5ff", text: "#060d1b" },
      { tier: 6, name: "🔮 Near-White", color: "#f1f2f6", text: "#060d1b" },
      { tier: 8, name: "⚪ Solar White", color: "#ffffff", text: "#060d1b" },
      { tier: 12, name: "☀️ Singularity", color: "#ffffff", text: "#060d1b" }
    ];
    evoExamples.forEach(t => {
      const item = document.createElement('div');
      item.className = 'evo-item';
      item.innerHTML = `
        <div class="evo-badge" style="background:${t.color}; color:${t.text}; box-shadow: 0 0 8px ${t.color};">${t.tier}</div>
        <div class="evo-name">${t.name}</div>
      `;
      container.appendChild(item);
    });
  }

  generateQRCode() {
    const url = `http://192.168.1.225:8086`;
    const label = document.getElementById('qr-url-text');
    if (label) label.textContent = url;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.airBubbleGame = new AirBubbleGame();
});

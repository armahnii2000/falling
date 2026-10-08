// A.I.r Bubbles — n×n Grid Edition Game Controller
// Implements full inverted buoyancy, 11-tier power-of-2 blocks (1 to 1024),
// Lake Ellem score reservoir, and tactile push-out dynamics.

const TIERS = [
  { tier: 1,  val: 1,    name: "Photon",            sub: "Primary Spark (1)" },
  { tier: 2,  val: 2,    name: "Chroma",            sub: "Dual Spectrum (2)" },
  { tier: 3,  val: 4,    name: "Prism",             sub: "Tri-Color Mix (4)" },
  { tier: 4,  val: 8,    name: "Spectra",           sub: "Harmonic Wave (8)" },
  { tier: 5,  val: 16,   name: "Lumen",             sub: "Amplified Light (16)" },
  { tier: 6,  val: 32,   name: "Candela",           sub: "Focused Beam (32)" },
  { tier: 7,  val: 64,   name: "Aurora",            sub: "Atmospheric Glow (64)" },
  { tier: 8,  val: 128,  name: "Corona",            sub: "Stellar Halo (128)" },
  { tier: 9,  val: 256,  name: "Helios",            sub: "Solar Core (256)" },
  { tier: 10, val: 512,  name: "Supernova",         sub: "Radiant Burst (512)" },
  { tier: 11, val: 1024, name: "White Singularity", sub: "1024 Apex Equilibrium" }
];

function getTierValue(tier) {
  if (tier >= 1 && tier <= TIERS.length) return TIERS[tier - 1].val;
  return Math.pow(2, Math.max(0, tier - 1));
}

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
    this.uiMergesCount = document.getElementById('val-merges-count');
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
        text: '#000000',
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

    // Box numbers strictly black text as requested
    const text = '#000000';

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
    const val = getTierValue(tier);
    const color = this.rollSpawnColor();
    return {
      tier: tier,
      val: val,
      colorName: color,
      r: color === 'red' ? val : 0,
      g: color === 'green' ? val : 0,
      b: color === 'blue' ? val : 0
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

    // 3. Score calculation: resulting block value * combo + Whiteness Purity Bonus
    const nextVal = getTierValue(nextTier);
    const basePts = nextVal * this.combo * 5;
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

    // Check Victory (e.g. Block 128+ with >= 90% white balance, or Block 1024 Singularity)
    if (nextTier >= 8 && colorInfo.balance >= 90 && !this.isWon && !this.isGameOver) {
      this.triggerWhiteVictory(newBubble, colorInfo);
      return;
    }
  }

  // SIZE 11 (1024) SINGULARITY BURST / DISAPPEAR
  onSingularityPop(b) {
    this.sound.playSingularity();
    this.cameraTrauma = 1.0;

    // Massive score bonus for 1024 Singularity
    const pts = 2048 * this.combo;
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
    document.getElementById('game-over-desc').textContent = `Magnificent achievement! You cultivated a giant Block ${getTierValue(b.tier)} with ${colorInfo.balance}% White light equilibrium across ${this.blocksLaunched} launches.`;
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
    document.getElementById('game-over-desc').textContent = `Blocks stacked down past the seabed danger line for over 3 seconds. Peak balance achieved: ${this.bestBalance}% on Block ${getTierValue(this.bestBalanceTier)}.`;
    this.showGameOverModal();
  }

  showGameOverModal() {
    document.getElementById('modal-final-score').textContent = this.score;
    document.getElementById('modal-peak-tier').textContent = `Block ${getTierValue(this.peakTier)} (${TIERS[this.peakTier - 1]?.name || ''}) · ⚪ ${this.bestBalance}%`;
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

    // Live Aim Impact Forecast & Predictive Universe State
    this.aimForecast = this.calculateAimForecast();

    // Update HUD with live vs predictive state
    this.updateHUD(this.aimForecast);

    // Update Huge Cumulative Color Hero Circle on the Right with predictive preview
    this.updateCumulativeHero(this.aimForecast);

    // Update Aim Impact Forecast Card
    this.updateShotForecastCard(this.aimForecast);
  }

  updateHUD(forecast) {
    const isPredictive = Boolean(forecast && forecast.willMerge);
    const cardScore = document.getElementById('card-lake') || document.getElementById('card-score');
    const cardPressure = document.getElementById('card-pressure');
    const cardMerges = document.getElementById('card-blocks') || document.getElementById('card-merges');
    const pushBadge = document.getElementById('live-push-badge');

    // 1. Score
    if (this.uiScore) {
      if (isPredictive && forecast.deltaScore > 0) {
        this.uiScore.innerHTML = `${this.score} <span class="predictive-delta">+${forecast.deltaScore}</span>`;
        if (cardScore) cardScore.classList.add('predictive-pulse');
      } else {
        this.uiScore.textContent = this.score;
        if (cardScore) cardScore.classList.remove('predictive-pulse');
      }
    }

    // 2. Combo
    if (this.uiCombo) {
      if (isPredictive) {
        if (forecast.predictedCombo > 1 || forecast.comboCount > 1) {
          this.uiCombo.textContent = `⚡ COMBO x${forecast.predictedCombo} (PREDICTED)`;
          this.uiCombo.style.color = '#ffd60a';
        } else {
          this.uiCombo.textContent = '🎯 MERGE (PREDICTED)';
          this.uiCombo.style.color = '#00e5ff';
        }
      } else {
        this.uiCombo.textContent = this.combo > 1 ? `COMBO x${this.combo}` : 'COMBO x1';
        this.uiCombo.style.color = '';
      }
    }

    // 3. Push Counter / Dynamics Badge
    if (this.uiPushCounter) {
      this.uiPushCounter.textContent = this.physics.pushoutCount;
    }
    if (pushBadge) {
      if (isPredictive && forecast.comboCount > 1) {
        pushBadge.innerHTML = `⚡ Cascade: x${forecast.comboCount}`;
        pushBadge.classList.add('predictive-badge');
      } else {
        pushBadge.innerHTML = `💥 Pushouts: <span id="push-counter">${this.physics.pushoutCount}</span>`;
        this.uiPushCounter = document.getElementById('push-counter');
        pushBadge.classList.remove('predictive-badge');
      }
    }

    // 4. White Equilibrium
    if (this.uiPressure) {
      if (isPredictive) {
        const isNewPeak = forecast.predictedBestBalance > this.bestBalance;
        if (isNewPeak) {
          this.uiPressure.innerHTML = `⚪ ${this.bestBalance}% <span class="predictive-delta" style="color:#ffffff;">➔ ${forecast.predictedBestBalance}%</span>`;
          if (cardPressure) cardPressure.classList.add('predictive-pulse');
        } else {
          this.uiPressure.innerHTML = `⚪ ${this.bestBalance}% <span class="predictive-delta" style="color:#00e5ff;">(${forecast.colorInfo.balance}%)</span>`;
          if (cardPressure) cardPressure.classList.remove('predictive-pulse');
        }
        if (this.uiPressureStatus) {
          if (isNewPeak) {
            this.uiPressureStatus.textContent = `⚡ NEW PEAK BLOCK ${getTierValue(forecast.predictedPeakTier)}!`;
            this.uiPressureStatus.style.color = '#ffffff';
          } else {
            this.uiPressureStatus.textContent = `YIELDS ${forecast.colorInfo.balance}% BALANCE`;
            this.uiPressureStatus.style.color = '#00e5ff';
          }
        }
      } else {
        this.uiPressure.textContent = `⚪ ${this.bestBalance}%`;
        if (cardPressure) cardPressure.classList.remove('predictive-pulse');
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
          this.uiPressureStatus.style.color = '#30d158';
        }
      }
    }

    // 5. Merges Count / Units Harvest
    if (this.uiMergesCount) {
      if (isPredictive) {
        this.uiMergesCount.innerHTML = `${this.totalMerges} <span class="predictive-delta">+${forecast.chainEvents.length}</span>`;
        const blocksSub = document.getElementById('val-blocks-sub');
        if (blocksSub) {
          blocksSub.textContent = `+${forecast.deltaUnits} HARVEST UNITS`;
          blocksSub.style.color = '#ffd60a';
        }
        if (cardMerges) cardMerges.classList.add('predictive-pulse');
      } else {
        this.uiMergesCount.textContent = this.totalMerges;
        const blocksSub = document.getElementById('val-blocks-sub');
        if (blocksSub) {
          blocksSub.textContent = `${this.totalMerges} MERGES`;
          blocksSub.style.color = '';
        }
        if (cardMerges) cardMerges.classList.remove('predictive-pulse');
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

    // 2. Draw Vertical RGB Spectrum Gauge to the Side of the Grid with predictive preview
    this.renderRGBGauge(ctx, this.physics.gauge, this.aimForecast);

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

  // Vertical RGB Spectrum Gauge to the side of the grid with full predictive preview
  renderRGBGauge(ctx, gauge, forecast) {
    if (!gauge) return;
    const gx = gauge.x;
    const gy = gauge.y;
    const gw = gauge.w;
    const gh = gauge.h;

    const isPredictive = Boolean(forecast && forecast.willMerge && forecast.deltaUnits > 0);

    ctx.save();

    // 1. Gauge Frame
    ctx.fillStyle = '#081324';
    ctx.strokeStyle = isPredictive ? 'rgba(0, 229, 255, 0.85)' : 'rgba(64, 128, 200, 0.45)';
    ctx.lineWidth = isPredictive ? 2 : 1.5;
    ctx.beginPath();
    ctx.roundRect(gx, gy, gw, gh, 6);
    ctx.fill();
    ctx.stroke();

    // Top Header: RGB MIX or RGB PREVIEW
    ctx.fillStyle = isPredictive ? '#ffd60a' : '#8b9bb4';
    ctx.font = isPredictive ? 'bold 7.5px -apple-system, sans-serif' : 'bold 8px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(isPredictive ? 'PREVIEW 🔮' : 'RGB MIX', gx + gw / 2, gy + 11);

    // 2. Prism Lamp (Global Cumulative Mixed Color Orb / Predicted Optical Color)
    const lampX = gx + gw / 2;
    const lampY = gy + 27;
    const lampR = Math.min(12, (gw - 12) / 2);

    let effR = isPredictive ? forecast.predictedR : this.cumulativeR;
    let effG = isPredictive ? forecast.predictedG : this.cumulativeG;
    let effB = isPredictive ? forecast.predictedB : this.cumulativeB;
    const totalUnits = effR + effG + effB;

    if (totalUnits === 0 && this.physics && this.physics.bubbles && this.physics.bubbles.length > 0) {
      for (const b of this.physics.bubbles) {
        effR += (b.r || 0);
        effG += (b.g || 0);
        effB += (b.b || 0);
      }
    }
    const maxGlobal = Math.max(effR, effG, effB, 1);
    const globalR = Math.round((effR / maxGlobal) * 255);
    const globalG = Math.round((effG / maxGlobal) * 255);
    const globalB = Math.round((effB / maxGlobal) * 255);
    const globalMixColor = (effR === 0 && effG === 0 && effB === 0)
      ? '#22334d'
      : `rgb(${globalR}, ${globalG}, ${globalB})`;

    ctx.save();
    ctx.shadowColor = isPredictive ? '#ffd60a' : globalMixColor;
    ctx.shadowBlur = isPredictive ? 16 : 12;
    ctx.fillStyle = globalMixColor;
    ctx.beginPath();
    ctx.arc(lampX, lampY, lampR, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = isPredictive ? '#ffd60a' : '#ffffff';
    ctx.lineWidth = isPredictive ? 2.0 : 1.5;
    ctx.stroke();

    // Specular highlight on glass lens
    ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
    ctx.beginPath();
    ctx.arc(lampX - lampR * 0.35, lampY - lampR * 0.35, lampR * 0.35, 0, Math.PI * 2);
    ctx.fill();

    // Animated dashed aura ring when in predictive mode
    if (isPredictive) {
      ctx.strokeStyle = 'rgba(255, 214, 10, 0.85)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([3, 3]);
      ctx.lineDashOffset = -this.gameTime * 14;
      ctx.beginPath();
      ctx.arc(lampX, lampY, lampR + 3, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();

    // 3. Three Vertical Fluid Channels (Red, Green, Blue)
    const channelsTop = gy + 46;
    const channelsH = gh - 96;
    const colW = Math.max(6, Math.floor((gw - 18) / 3));
    const pad = 3;
    const totalColsW = colW * 3 + pad * 2;
    const startX = gx + (gw - totalColsW) / 2;

    const deltaR = isPredictive ? (forecast.deltaR || 0) : 0;
    const deltaG = isPredictive ? (forecast.deltaG || 0) : 0;
    const deltaB = isPredictive ? (forecast.deltaB || 0) : 0;

    const predR = this.cumulativeR + deltaR;
    const predG = this.cumulativeG + deltaG;
    const predB = this.cumulativeB + deltaB;

    const channels = [
      { key: 'R', live: this.cumulativeR, delta: deltaR, pred: predR, color: '#ff3b30', bg: 'rgba(255, 59, 48, 0.12)' },
      { key: 'G', live: this.cumulativeG, delta: deltaG, pred: predG, color: '#30d158', bg: 'rgba(48, 209, 88, 0.12)' },
      { key: 'B', live: this.cumulativeB, delta: deltaB, pred: predB, color: '#00e5ff', bg: 'rgba(0, 229, 255, 0.12)' }
    ];

    // Dynamic capacity with guaranteed 35% headroom so highest channel never reaches ceiling!
    const peakChannel = Math.max(predR, predG, predB, 1);
    const maxCapacity = Math.max(25, Math.ceil(peakChannel * 1.55));

    channels.forEach((ch, i) => {
      const cx = startX + i * (colW + pad);
      const cy = channelsTop;

      // Channel background slot
      ctx.fillStyle = ch.bg;
      ctx.beginPath();
      ctx.roundRect(cx, cy, colW, channelsH, 3);
      ctx.fill();
      ctx.strokeStyle = (isPredictive && ch.delta > 0) ? 'rgba(255, 214, 10, 0.4)' : 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Fluid fill levels
      const liveRatio = Math.min(0.88, ch.live / maxCapacity);
      const liveFillH = channelsH * liveRatio;
      const liveFillY = cy + channelsH - liveFillH;

      // Solid Live Fluid
      if (liveFillH > 0) {
        ctx.save();
        ctx.fillStyle = ch.color;
        ctx.shadowColor = ch.color;
        ctx.shadowBlur = 6;
        ctx.beginPath();
        ctx.roundRect(cx, liveFillY, colW, liveFillH, [0, 0, 3, 3]);
        ctx.fill();
        ctx.restore();
      }

      // Ghost Fluid Extension (Predicted Gain)
      if (isPredictive && ch.delta > 0) {
        const predRatio = Math.min(0.88, ch.pred / maxCapacity);
        const predFillH = channelsH * predRatio;
        const predFillY = cy + channelsH - predFillH;
        const ghostH = Math.max(0, liveFillY - predFillY);

        if (ghostH > 0) {
          ctx.save();
          // 1. Ghost Translucent Body with gentle pulse
          const ghostAlpha = 0.42 + Math.sin(this.gameTime * 6) * 0.14;
          ctx.globalAlpha = ghostAlpha;
          ctx.fillStyle = ch.color;
          ctx.fillRect(cx, predFillY, colW, ghostH);

          // 2. Diagonal Stripe Hatch
          ctx.beginPath();
          ctx.rect(cx, predFillY, colW, ghostH);
          ctx.clip();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1;
          ctx.globalAlpha = 0.6;
          for (let y = predFillY - colW; y <= predFillY + ghostH + colW; y += 4) {
            ctx.beginPath();
            ctx.moveTo(cx, y);
            ctx.lineTo(cx + colW, y + colW);
            ctx.stroke();
          }
          ctx.restore();

          // 3. Top Glowing Neon Cap Line at predFillY
          ctx.save();
          ctx.strokeStyle = '#ffd60a';
          ctx.lineWidth = 1.6;
          ctx.shadowColor = '#ffd60a';
          ctx.shadowBlur = 5;
          ctx.beginPath();
          ctx.moveTo(cx, predFillY);
          ctx.lineTo(cx + colW, predFillY);
          ctx.stroke();
          ctx.restore();

          // 4. Floating +Delta text above the tube / ghost level
          ctx.save();
          ctx.fillStyle = '#ffd60a';
          ctx.font = 'bold 7px monospace';
          ctx.textAlign = 'center';
          ctx.shadowColor = '#000000';
          ctx.shadowBlur = 3;
          const textY = Math.max(cy + 7, predFillY - 2);
          ctx.fillText(`+${ch.delta}`, cx + colW / 2, textY);
          ctx.restore();
        }
      }

      // Channel Letter Label (R, G, B) below column
      ctx.fillStyle = ch.color;
      ctx.font = 'bold 8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(ch.key, cx + colW / 2, cy + channelsH + 11);

      // Channel count number (shows predicted count in gold or live count in white)
      ctx.font = 'bold 7px monospace';
      if (isPredictive && ch.delta > 0) {
        ctx.fillStyle = '#ffd60a';
        ctx.fillText(`${ch.pred}`, cx + colW / 2, cy + channelsH + 20);
      } else {
        ctx.fillStyle = '#ffffff';
        ctx.fillText(`${ch.live}`, cx + colW / 2, cy + channelsH + 20);
      }
    });

    // Average 1:1:1 Equilibrium Datum Lines
    const avgUnits = (this.cumulativeR + this.cumulativeG + this.cumulativeB) / 3;
    if (avgUnits > 0) {
      const datumRatio = Math.min(0.88, avgUnits / maxCapacity);
      const datumH = channelsH * datumRatio;
      const datumY = channelsTop + channelsH - datumH;

      ctx.save();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.75)';
      ctx.lineWidth = 1.2;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(startX - 2, datumY);
      ctx.lineTo(startX + totalColsW + 2, datumY);
      ctx.stroke();
      ctx.restore();
    }

    // Predicted Equilibrium Line if in predictive mode
    if (isPredictive && (predR + predG + predB > this.cumulativeR + this.cumulativeG + this.cumulativeB)) {
      const predAvgUnits = (predR + predG + predB) / 3;
      const predDatumRatio = Math.min(0.88, predAvgUnits / maxCapacity);
      const predDatumH = channelsH * predDatumRatio;
      const predDatumY = channelsTop + channelsH - predDatumH;

      ctx.save();
      ctx.strokeStyle = '#ffd60a';
      ctx.lineWidth = 1.4;
      ctx.setLineDash([3, 2]);
      ctx.beginPath();
      ctx.moveTo(startX - 2, predDatumY);
      ctx.lineTo(startX + totalColsW + 2, predDatumY);
      ctx.stroke();

      ctx.fillStyle = '#ffd60a';
      ctx.font = 'bold 6px monospace';
      ctx.textAlign = 'right';
      ctx.fillText('EQ➔', startX - 3, predDatumY + 2);
      ctx.restore();
    }

    // 4. Peak Bubble Whiteness Readout at bottom
    ctx.save();
    if (isPredictive) {
      const predBal = forecast.predictedBestBalance;
      const isNewPeak = predBal > this.bestBalance;
      ctx.fillStyle = isNewPeak ? '#ffffff' : '#ffd60a';
      if (isNewPeak) {
        ctx.shadowColor = '#ffffff';
        ctx.shadowBlur = 10;
      }
      ctx.font = 'bold 8px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`⚪ ➔ ${predBal}%`, gx + gw / 2, gy + gh - 14);

      ctx.font = 'bold 7px sans-serif';
      ctx.fillStyle = isNewPeak ? '#ffd60a' : '#8b9bb4';
      ctx.fillText(isNewPeak ? `NEW ${getTierValue(forecast.predictedPeakTier)}!` : `PEAK ${getTierValue(this.bestBalanceTier)}`, gx + gw / 2, gy + gh - 4);
    } else {
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
      ctx.fillText(`PEAK ${getTierValue(this.bestBalanceTier)}`, gx + gw / 2, gy + gh - 4);
    }
    ctx.restore();

    ctx.restore();
  }

  // Renders a sleek heads-up capsule pill overlay showing exact primary R, G, B counts
  renderRGBPillOverlay(ctx, b, yPos, maxWidth) {
    const r = (b && b.r) || 0;
    const g = (b && b.g) || 0;
    const bVal = (b && b.b) || 0;

    // Collect active channel counts
    const channels = [];
    if (r > 0) channels.push({ key: 'R', count: r, color: '#ff3b30' });
    if (g > 0) channels.push({ key: 'G', count: g, color: '#30d158' });
    if (bVal > 0) channels.push({ key: 'B', count: bVal, color: '#00e5ff' });

    if (channels.length === 0) return;

    ctx.save();

    // Scale slightly for larger blocks
    const refW = maxWidth || 50;
    const scale = Math.min(1.3, Math.max(0.85, refW / 64));
    const dotR = 2.8 * scale;
    const fontSize = Math.max(7.5, Math.min(11, 8.5 * scale));
    const itemGap = 5.5 * scale;
    const sidePad = 5.0 * scale;
    const pillH = Math.max(12, Math.min(18, 14.5 * scale));

    ctx.font = `bold ${fontSize}px monospace`;

    // Measure exact widths
    let contentW = 0;
    const itemData = channels.map(ch => {
      const textW = ctx.measureText(`${ch.count}`).width;
      const itemW = dotR * 2 + 2.5 * scale + textW;
      contentW += itemW;
      return { ch, itemW, textW };
    });
    contentW += itemGap * (channels.length - 1);

    const pillW = Math.min(refW * 0.94, contentW + sidePad * 2);
    const pillX = -pillW / 2;
    const pillY = yPos - pillH / 2;

    // 1. Dark translucent capsule container
    ctx.fillStyle = 'rgba(4, 10, 22, 0.90)';
    ctx.beginPath();
    ctx.roundRect(pillX, pillY, pillW, pillH, pillH / 2);
    ctx.fill();

    // 2. Crisp subtle outer rim
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.lineWidth = 1.0;
    ctx.stroke();

    // 3. Render items with glowing color dots and bold counts
    let curX = pillX + (pillW - contentW) / 2;
    for (const item of itemData) {
      const dotCenterX = curX + dotR;
      const dotCenterY = yPos;

      // Color dot with glow
      ctx.fillStyle = item.ch.color;
      ctx.shadowColor = item.ch.color;
      ctx.shadowBlur = 4 * scale;
      ctx.beginPath();
      ctx.arc(dotCenterX, dotCenterY, dotR, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Number text
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      const textX = dotCenterX + dotR + 2.5 * scale;
      ctx.fillText(`${item.ch.count}`, textX, yPos);

      curX += item.itemW + itemGap;
    }

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

      // Inner n×n Sub-grid Lines (clean subtle contrast)
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.22)';
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

      // Center Block Value Number Badge - SOLID BLACK TEXT WITH CRISP MICRO-RIM
      ctx.save();
      const valStr = `${b.val || getTierValue(b.tier)}`;
      let numSize = Math.max(10, Math.min(26, b.size * 0.44));
      if (valStr.length === 3) numSize = Math.max(9, Math.min(22, b.size * 0.36));
      if (valStr.length >= 4) numSize = Math.max(9, Math.min(20, b.size * 0.28));
      ctx.font = `900 ${numSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const numY = (b.size >= 34 ? -Math.round(b.size * 0.12) : 0);

      // Subtle light stroke guaranteeing legibility on pure blue/red boxes
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.92)';
      ctx.lineWidth = Math.max(2, Math.round(b.size * 0.05));
      ctx.lineJoin = 'round';
      ctx.strokeText(valStr, 0, numY);

      // Solid black text fill
      ctx.fillStyle = '#000000';
      ctx.fillText(valStr, 0, numY);
      ctx.restore();

      // RGB Pill Overlay showing exact constituent R, G, B counts
      if (b.size >= 34) {
        this.renderRGBPillOverlay(ctx, b, b.size * 0.24, b.size);
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

      // Circle Block Value Number Badge - SOLID BLACK TEXT WITH CRISP MICRO-RIM
      ctx.save();
      const circleValStr = `${b.val || getTierValue(b.tier)}`;
      let circleNumSize = Math.max(10, Math.min(24, b.radius * 0.72));
      if (circleValStr.length === 3) circleNumSize = Math.max(9, Math.min(20, b.radius * 0.58));
      if (circleValStr.length >= 4) circleNumSize = Math.max(9, Math.min(18, b.radius * 0.46));
      ctx.font = `900 ${circleNumSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const circleNumY = (b.radius >= 22 ? -Math.round(b.radius * 0.18) : 0);

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.92)';
      ctx.lineWidth = Math.max(2, Math.round(b.radius * 0.08));
      ctx.lineJoin = 'round';
      ctx.strokeText(circleValStr, 0, circleNumY);

      ctx.fillStyle = '#000000';
      ctx.fillText(circleValStr, 0, circleNumY);
      ctx.restore();

      // RGB Pill Overlay for circle mode
      if (b.radius >= 22) {
        this.renderRGBPillOverlay(ctx, b, b.radius * 0.38, b.radius * 2);
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
    const forecast = this.calculateAimForecast();
    const landingY = (forecast && forecast.landingY) ? forecast.landingY : (chamber.y + 4);
    const targetY = landingY;

    ctx.save();
    // 1. Subtle glowing trajectory corridor between the two lines
    const corridorColor = (forecast && forecast.willMerge)
      ? (forecast.comboCount > 1 ? 'rgba(255, 214, 10, 0.08)' : 'rgba(0, 229, 255, 0.08)')
      : 'rgba(0, 229, 255, 0.04)';
    ctx.fillStyle = corridorColor;
    ctx.fillRect(lx - halfWidth, targetY, boxWidth, Math.max(0, startY - targetY));

    // 2. Two guide lines marking the left and right edges of the box
    const guideLineColor = (forecast && forecast.willMerge)
      ? (forecast.comboCount > 1 ? 'rgba(255, 214, 10, 0.75)' : 'rgba(0, 229, 255, 0.75)')
      : 'rgba(0, 229, 255, 0.45)';
    ctx.strokeStyle = guideLineColor;
    ctx.lineWidth = (forecast && forecast.willMerge) ? 2.0 : 1.5;
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

    // Subtle landing bracket
    ctx.setLineDash([]);
    ctx.strokeStyle = (forecast && forecast.willMerge)
      ? (forecast.comboCount > 1 ? '#ffd60a' : '#00e5ff')
      : 'rgba(0, 229, 255, 0.6)';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(lx - halfWidth, targetY);
    ctx.lineTo(lx + halfWidth, targetY);
    ctx.stroke();
    ctx.restore();

    // 3. In-Chamber Target Highlight Reticle and Floating Forecast Badge
    if (forecast && forecast.willMerge && forecast.target) {
      const t = forecast.target;

      ctx.save();
      // Animated pulse reticle on target block
      const pulse = 1.0 + Math.sin(this.gameTime * 7) * 0.05;
      const reticleColor = (forecast.comboCount > 1) ? '#ffd60a' : '#00e5ff';
      ctx.strokeStyle = reticleColor;
      ctx.lineWidth = 2.5;
      ctx.shadowColor = reticleColor;
      ctx.shadowBlur = 10;
      ctx.strokeRect(t.x - t.hw * pulse, t.y - t.hh * pulse, t.size * pulse, t.size * pulse);
      ctx.restore();

      // Floating prediction badge right above target block
      ctx.save();
      const badgeY = Math.max(chamber.y + 24, t.y - t.hh - 14);
      ctx.translate(t.x, badgeY);

      const badgeTitle = (forecast.comboCount > 1)
        ? `⚡ COMBO x${forecast.comboCount} ➔ ${getTierValue(forecast.finalTier)}`
        : `🎯 ${getTierValue(forecast.finalTier)}`;

      // Title label
      ctx.fillStyle = (forecast.comboCount > 1) ? '#ffd60a' : '#00e5ff';
      ctx.font = 'bold 9px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.shadowColor = '#000000';
      ctx.shadowBlur = 5;
      ctx.fillText(badgeTitle, 0, -8);

      // Pill overlay showing expected constituent counts
      const simBubble = {
        tier: forecast.finalTier,
        r: forecast.expectedR,
        g: forecast.expectedG,
        b: forecast.expectedB
      };
      this.renderRGBPillOverlay(ctx, simBubble, 0, 96);
      ctx.restore();
    }

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

        const readyValStr = `${this.readyBubble.val || getTierValue(this.readyBubble.tier)}`;
        ctx.save();
        ctx.font = '900 13px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.lineWidth = 2.0;
        ctx.lineJoin = 'round';
        ctx.strokeText(readyValStr, 0, (this.readyBubble.tier >= 2 ? -5 : 0));
        ctx.fillStyle = '#000000';
        ctx.fillText(readyValStr, 0, (this.readyBubble.tier >= 2 ? -5 : 0));
        ctx.restore();

        if (this.readyBubble.tier >= 2) {
          this.renderRGBPillOverlay(ctx, this.readyBubble, previewSize * 0.24, previewSize);
        }
      } else {
        ctx.fillStyle = colorInfo.css;
        ctx.beginPath();
        ctx.arc(0, 0, previewSize / 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = colorInfo.border;
        ctx.lineWidth = 2.0;
        ctx.stroke();

        const readyValStr = `${this.readyBubble.val || getTierValue(this.readyBubble.tier)}`;
        ctx.save();
        ctx.font = '900 13px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.lineWidth = 2.0;
        ctx.lineJoin = 'round';
        ctx.strokeText(readyValStr, 0, (this.readyBubble.tier >= 2 ? -5 : 0));
        ctx.fillStyle = '#000000';
        ctx.fillText(readyValStr, 0, (this.readyBubble.tier >= 2 ? -5 : 0));
        ctx.restore();

        if (this.readyBubble.tier >= 2) {
          this.renderRGBPillOverlay(ctx, this.readyBubble, previewSize * 0.24, previewSize);
        }
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

    const nextValStr = `${this.nextBubble.val || getTierValue(this.nextBubble.tier)}`;
    ctx.save();
    ctx.font = '900 13px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.lineWidth = 2.0;
    ctx.lineJoin = 'round';
    ctx.strokeText(nextValStr, 0, (this.nextBubble.tier >= 2 ? -5 : 0));
    ctx.fillStyle = '#000000';
    ctx.fillText(nextValStr, 0, (this.nextBubble.tier >= 2 ? -5 : 0));
    ctx.restore();

    if (this.nextBubble.tier >= 2) {
      this.renderRGBPillOverlay(ctx, this.nextBubble, previewSize * 0.24, previewSize);
    }

    ctx.restore();
  }

  renderEvolutionStrip() {
    const container = document.getElementById('evo-scroll-container');
    if (!container) return;
    container.innerHTML = '';
    const evoExamples = [
      { tier: 1,  val: 1,    name: "1 Photon",      color: "#ff3b30", text: "#000000" },
      { tier: 2,  val: 2,    name: "2 Chroma",      color: "#ffd60a", text: "#000000" },
      { tier: 3,  val: 4,    name: "4 Prism",       color: "#c56cf0", text: "#000000" },
      { tier: 4,  val: 8,    name: "8 Spectra",     color: "#ff9f1a", text: "#000000" },
      { tier: 5,  val: 16,   name: "16 Lumen",      color: "#00e5ff", text: "#000000" },
      { tier: 6,  val: 32,   name: "32 Candela",    color: "#f1f2f6", text: "#000000" },
      { tier: 7,  val: 64,   name: "64 Aurora",     color: "#2ed573", text: "#000000" },
      { tier: 8,  val: 128,  name: "128 Corona",    color: "#ffa502", text: "#000000" },
      { tier: 9,  val: 256,  name: "256 Helios",    color: "#ff4757", text: "#000000" },
      { tier: 10, val: 512,  name: "512 Nova",      color: "#eccc68", text: "#000000" },
      { tier: 11, val: 1024, name: "1024 Apex",     color: "#ffffff", text: "#000000" }
    ];
    evoExamples.forEach(t => {
      const item = document.createElement('div');
      item.className = 'evo-item';
      item.innerHTML = `
        <div class="evo-badge" style="background:${t.color}; color:${t.text}; box-shadow: 0 0 8px ${t.color}; font-weight: 900;">${t.val}</div>
        <div class="evo-name">${t.name}</div>
      `;
      container.appendChild(item);
    });
  }

  updateCumulativeHero(forecast) {
    const heroCard = document.getElementById('cumulative-color-hero');
    const heroTag = heroCard ? heroCard.querySelector('.hero-tag') : null;
    const orb = document.getElementById('cumulative-color-orb');
    const orbNum = document.getElementById('cumulative-orb-number');
    const orbLabel = document.getElementById('cumulative-orb-label');
    const orbName = document.getElementById('cumulative-orb-color-name');
    const badge = document.getElementById('hero-balance-badge');
    const pillR = document.getElementById('val-pill-r');
    const pillG = document.getElementById('val-pill-g');
    const pillB = document.getElementById('val-pill-b');
    const pillCardR = document.getElementById('pill-r');
    const pillCardG = document.getElementById('pill-g');
    const pillCardB = document.getElementById('pill-b');
    const barFill = document.getElementById('hero-whiteness-fill');
    const barPct = document.getElementById('hero-whiteness-pct');

    if (!orb || !orbNum) return;

    const isPredictive = Boolean(forecast && forecast.willMerge && forecast.deltaUnits > 0);

    // Toggle active predictive styling on hero card
    if (heroCard) {
      heroCard.classList.toggle('predictive-active', isPredictive);
    }
    if (heroTag) {
      heroTag.textContent = isPredictive ? '🔮 PREDICTED SPECTRUM' : 'CUMULATIVE SPECTRUM';
      heroTag.style.color = isPredictive ? '#ffd60a' : '';
    }

    // Determine target values: live vs predicted
    const liveR = this.cumulativeR;
    const liveG = this.cumulativeG;
    const liveB = this.cumulativeB;
    const liveTotal = liveR + liveG + liveB;

    const effR = isPredictive ? forecast.predictedR : liveR;
    const effG = isPredictive ? forecast.predictedG : liveG;
    const effB = isPredictive ? forecast.predictedB : liveB;
    const totalUnits = isPredictive ? forecast.predictedTotalUnits : liveTotal;

    // Effective RGB for chromatic preview:
    // If no merges have occurred yet, preview the chamber's active bubbles so the hero orb is responsive immediately!
    let chromaticR = effR;
    let chromaticG = effG;
    let chromaticB = effB;
    let isStandby = false;

    if (totalUnits === 0) {
      if (this.physics && this.physics.bubbles && this.physics.bubbles.length > 0) {
        for (const b of this.physics.bubbles) {
          chromaticR += (b.r || 0);
          chromaticG += (b.g || 0);
          chromaticB += (b.b || 0);
        }
      } else {
        isStandby = true;
      }
    }

    const maxVal = Math.max(chromaticR, chromaticG, chromaticB);
    let R = 24, G = 38, B = 60;
    let balance = 0;
    let isWhite = false;
    let colorName = 'Standby';

    if (!isStandby && maxVal > 0) {
      R = Math.round((chromaticR / maxVal) * 255);
      G = Math.round((chromaticG / maxVal) * 255);
      B = Math.round((chromaticB / maxVal) * 255);
      const minVal = Math.min(chromaticR, chromaticG, chromaticB);
      balance = Math.round((minVal / maxVal) * 100);
      isWhite = (balance >= 95 && chromaticR > 0 && chromaticG > 0 && chromaticB > 0);

      if (isWhite) {
        colorName = '⚪ Pure White Light';
      } else if (chromaticR > 0 && chromaticG === 0 && chromaticB === 0) {
        colorName = '🔴 Pure Red';
      } else if (chromaticG > 0 && chromaticR === 0 && chromaticB === 0) {
        colorName = '🟢 Pure Green';
      } else if (chromaticB > 0 && chromaticR === 0 && chromaticG === 0) {
        colorName = '🔵 Pure Blue';
      } else if (chromaticR === chromaticG && chromaticB === 0) {
        colorName = '🟡 Yellow (R+G)';
      } else if (chromaticR === chromaticB && chromaticG === 0) {
        colorName = '🟣 Magenta (R+B)';
      } else if (chromaticG === chromaticB && chromaticR === 0) {
        colorName = '🔷 Cyan (G+B)';
      } else if (balance >= 75) {
        colorName = 'Near-White Light';
      } else if (chromaticR >= chromaticG && chromaticR >= chromaticB) {
        colorName = chromaticG > chromaticB ? 'Warm Amber' : 'Rose Violet';
      } else if (chromaticG >= chromaticR && chromaticG >= chromaticB) {
        colorName = chromaticR > chromaticB ? 'Lime Green' : 'Aquamarine';
      } else {
        colorName = chromaticR > chromaticG ? 'Deep Violet' : 'Electric Cyan';
      }
    }

    // Set huge circle background color and radiant glow
    if (isStandby) {
      orb.style.backgroundColor = '#162438';
      orb.style.boxShadow = '0 0 24px rgba(0, 229, 255, 0.2), inset 0 2px 8px rgba(255, 255, 255, 0.4), inset 0 -6px 14px rgba(0, 0, 0, 0.5)';
      orb.style.borderColor = 'rgba(255, 255, 255, 0.35)';
    } else if (isWhite) {
      orb.style.backgroundColor = '#ffffff';
      orb.style.boxShadow = isPredictive
        ? '0 0 65px rgba(255, 255, 255, 1), 0 0 120px rgba(255, 214, 10, 0.6), inset 0 0 28px #ffffff'
        : '0 0 55px rgba(255, 255, 255, 0.95), 0 0 100px rgba(255, 255, 255, 0.55), inset 0 0 24px #ffffff';
      orb.style.borderColor = '#ffffff';
    } else {
      orb.style.backgroundColor = `rgb(${R}, ${G}, ${B})`;
      orb.style.boxShadow = isPredictive
        ? `0 0 55px rgba(${R}, ${G}, ${B}, 0.95), 0 0 95px rgba(255, 214, 10, 0.5), inset 0 3px 10px rgba(255, 255, 255, 0.85), inset 0 -8px 16px rgba(0, 0, 0, 0.5)`
        : `0 0 45px rgba(${R}, ${G}, ${B}, 0.8), 0 0 85px rgba(${R}, ${G}, ${B}, 0.4), inset 0 3px 10px rgba(255, 255, 255, 0.75), inset 0 -8px 16px rgba(0, 0, 0, 0.5)`;
      orb.style.borderColor = (balance >= 70) ? '#ffffff' : `rgba(${Math.min(255, R + 60)}, ${Math.min(255, G + 60)}, ${Math.min(255, B + 60)}, 0.95)`;
    }

    // Display cumulative number in the circle with dynamic font scaling to prevent clipping
    orbNum.textContent = totalUnits;
    const isMobile = window.innerWidth < 768;
    if (totalUnits >= 1000) {
      orbNum.style.fontSize = isMobile ? '1.45rem' : '1.8rem';
    } else if (totalUnits >= 100) {
      orbNum.style.fontSize = isMobile ? '1.75rem' : '2.15rem';
    } else {
      orbNum.style.fontSize = isMobile ? '2.1rem' : '2.6rem';
    }

    // Luminance-adaptive text contrast inside the orb
    const lum = (0.299 * R + 0.587 * G + 0.114 * B) / 255;
    const isLightBackground = !isStandby && lum > 0.55;
    const orbTextColor = isLightBackground ? '#000000' : '#ffffff';

    orbNum.style.color = orbTextColor;
    if (isLightBackground) {
      orbNum.style.textShadow = '0 1px 2px rgba(255, 255, 255, 0.8)';
    } else {
      orbNum.style.textShadow = '0 2px 8px rgba(0, 0, 0, 0.85)';
    }

    if (orbLabel) {
      if (isPredictive) {
        orbLabel.textContent = `PREDICTED (+${forecast.deltaUnits} GAIN)`;
        orbLabel.style.color = '#ffd60a';
      } else {
        orbLabel.textContent = totalUnits === 0 ? 'READY TO HARVEST' : 'CUMULATIVE UNITS';
        orbLabel.style.color = isLightBackground ? 'rgba(0, 0, 0, 0.75)' : 'rgba(255, 255, 255, 0.85)';
      }
    }

    if (orbName) {
      orbName.textContent = isPredictive ? `⚡ ${colorName}` : colorName;
      orbName.style.color = isPredictive ? '#ffd60a' : orbTextColor;
      orbName.style.textShadow = isLightBackground && !isPredictive ? 'none' : '0 1px 4px rgba(0, 0, 0, 0.8)';
    }

    // Top status badge
    if (badge) {
      if (isPredictive) {
        badge.textContent = isWhite ? '⚪ ➔ 100% WHITE!' : `➔ ${balance}% BALANCED`;
        badge.style.color = '#ffd60a';
        badge.style.borderColor = '#ffd60a';
      } else {
        badge.textContent = isWhite ? '⚪ 100% WHITE!' : (totalUnits > 0 ? `${balance}% BALANCED` : '⚪ READY');
        badge.style.color = isWhite ? '#ffffff' : (balance >= 50 ? '#00e5ff' : '#ffd60a');
        badge.style.borderColor = isWhite ? '#ffffff' : (balance >= 50 ? '#00e5ff' : 'rgba(255, 255, 255, 0.2)');
      }
    }

    // Channel pills
    if (pillR) {
      if (isPredictive && forecast.deltaR > 0) {
        pillR.innerHTML = `${liveR} <span class="pill-delta">+${forecast.deltaR}</span>`;
        if (pillCardR) pillCardR.classList.add('pill-predictive-gain');
      } else {
        pillR.textContent = liveR;
        if (pillCardR) pillCardR.classList.remove('pill-predictive-gain');
      }
    }
    if (pillG) {
      if (isPredictive && forecast.deltaG > 0) {
        pillG.innerHTML = `${liveG} <span class="pill-delta">+${forecast.deltaG}</span>`;
        if (pillCardG) pillCardG.classList.add('pill-predictive-gain');
      } else {
        pillG.textContent = liveG;
        if (pillCardG) pillCardG.classList.remove('pill-predictive-gain');
      }
    }
    if (pillB) {
      if (isPredictive && forecast.deltaB > 0) {
        pillB.innerHTML = `${liveB} <span class="pill-delta">+${forecast.deltaB}</span>`;
        if (pillCardB) pillCardB.classList.add('pill-predictive-gain');
      } else {
        pillB.textContent = liveB;
        if (pillCardB) pillCardB.classList.remove('pill-predictive-gain');
      }
    }

    // Progress bar
    const liveMax = Math.max(liveR, liveG, liveB, 1);
    const liveMin = Math.min(liveR, liveG, liveB);
    const liveBal = liveTotal > 0 ? Math.round((liveMin / liveMax) * 100) : 0;

    if (barFill) {
      barFill.style.width = `${balance}%`;
      barFill.classList.toggle('predictive-fill', isPredictive);
    }
    if (barPct) {
      if (isPredictive && balance !== liveBal) {
        barPct.innerHTML = `${liveBal}% <span class="predictive-delta">➔ ${balance}%</span>`;
      } else {
        barPct.textContent = `${balance}%`;
      }
    }
  }

  calculateAimForecast() {
    const nonMergeState = (reason, target, landingY) => ({
      willMerge: false,
      reason: reason,
      target: target,
      landingY: landingY,
      comboCount: 1,
      finalTier: this.readyBubble ? this.readyBubble.tier : 1,
      expectedR: (this.readyBubble && this.readyBubble.r) || 0,
      expectedG: (this.readyBubble && this.readyBubble.g) || 0,
      expectedB: (this.readyBubble && this.readyBubble.b) || 0,
      totalUnits: ((this.readyBubble && this.readyBubble.r) || 0) + ((this.readyBubble && this.readyBubble.g) || 0) + ((this.readyBubble && this.readyBubble.b) || 0),
      chainEvents: [],
      deltaR: 0,
      deltaG: 0,
      deltaB: 0,
      deltaUnits: 0,
      deltaScore: 0,
      predictedScore: this.score,
      predictedR: this.cumulativeR,
      predictedG: this.cumulativeG,
      predictedB: this.cumulativeB,
      predictedTotalUnits: this.cumulativeR + this.cumulativeG + this.cumulativeB,
      predictedMerges: this.totalMerges,
      predictedPeakTier: this.peakTier,
      predictedCombo: this.combo,
      predictedCumulativeColor: null,
      predictedBestBalance: this.bestBalance
    });

    if (!this.readyBubble || this.isGameOver) {
      return nonMergeState('none', null, 0);
    }

    const chamber = this.physics.chamber;
    const lx = this.launcherX;
    const readyTier = this.readyBubble.tier;
    const readyHw = (readyTier * this.physics.cellSize) / 2;
    const readyHh = readyHw;

    // Find all candidate bubbles in chamber intersecting the vertical corridor
    const inCorridor = [];
    for (const b of this.physics.bubbles) {
      if (b.merging) continue;
      const minDistX = readyHw + b.hw;
      const dx = Math.abs(b.x - lx);
      if (dx < minDistX - 2) {
        inCorridor.push(b);
      }
    }

    // Open lane if no bubbles in path
    if (inCorridor.length === 0) {
      return nonMergeState('open_lane', null, chamber.y + readyHh);
    }

    // Bubble with maximum y is lowest in chamber (first hit)
    inCorridor.sort((a, b) => b.y - a.y);
    const target = inCorridor[0];

    // Check tier match
    if (target.tier !== readyTier) {
      return nonMergeState('mismatch', target, target.y + target.hh + readyHh);
    }

    // Direct match: Simulate FULL CASCADE CHAIN
    let simBubbles = this.physics.bubbles.filter(b => !b.merging).map(b => ({
      id: b.id,
      tier: b.tier,
      r: b.r || 0,
      g: b.g || 0,
      b: b.b || 0,
      x: b.x,
      y: b.y,
      size: b.size,
      hw: b.hw,
      hh: b.hh
    }));

    let curTier = readyTier + 1;
    let curR = (target.r || 0) + (this.readyBubble.r || 0);
    let curG = (target.g || 0) + (this.readyBubble.g || 0);
    let curB = (target.b || 0) + (this.readyBubble.b || 0);
    let curX = (target.x + lx) / 2;
    let curY = target.y;
    let curSize = curTier * this.physics.cellSize;
    let curHw = curSize / 2;
    let curHh = curHw;

    simBubbles = simBubbles.filter(b => b.id !== target.id);

    let comboCount = 1;
    let simCombo = (this.gameTime - this.lastMergeTime <= this.comboWindow) ? (this.combo + 1) : 1;
    let deltaR = curR;
    let deltaG = curG;
    let deltaB = curB;

    const step1Color = this.getBubbleColor({ r: curR, g: curG, b: curB });
    const step1BasePts = getTierValue(curTier) * simCombo * 5;
    const step1Mult = 1.0 + (step1Color.balance / 100) * 2.0;
    let deltaScore = Math.round(step1BasePts * step1Mult);

    const chainEvents = [{
      step: 1,
      tier: curTier,
      r: curR,
      g: curG,
      b: curB,
      desc: `Direct Merge ${getTierValue(readyTier)} + ${getTierValue(target.tier)} ➔ ${getTierValue(curTier)}`
    }];

    // Cascade search (11 blocks max)
    let canCascade = true;
    while (canCascade && curTier < 11) {
      canCascade = false;
      let bestNeighbor = null;
      let bestDist = Infinity;

      for (const cand of simBubbles) {
        if (cand.tier === curTier) {
          const dx = Math.abs(cand.x - curX);
          const dy = Math.abs(cand.y - curY);
          const minDistX = cand.hw + curHw;
          const minDistY = cand.hh + curHh;

          // Overlap or touching contact
          if (minDistX - dx >= -5 && minDistY - dy >= -5) {
            const dist = Math.hypot(cand.x - curX, cand.y - curY);
            if (dist < bestDist) {
              bestDist = dist;
              bestNeighbor = cand;
            }
          }
        }
      }

      if (bestNeighbor) {
        comboCount++;
        canCascade = true;
        simCombo++;

        deltaR += curR + (bestNeighbor.r || 0);
        deltaG += curG + (bestNeighbor.g || 0);
        deltaB += curB + (bestNeighbor.b || 0);

        curTier = curTier + 1;
        curR = curR + (bestNeighbor.r || 0);
        curG = curG + (bestNeighbor.g || 0);
        curB = curB + (bestNeighbor.b || 0);

        const stepNColor = this.getBubbleColor({ r: curR, g: curG, b: curB });
        const stepNBasePts = getTierValue(curTier) * simCombo * 5;
        const stepNMult = 1.0 + (stepNColor.balance / 100) * 2.0;
        deltaScore += Math.round(stepNBasePts * stepNMult);

        curX = (curX + bestNeighbor.x) / 2;
        curY = (curY + bestNeighbor.y) / 2;
        curSize = curTier * this.physics.cellSize;
        curHw = curSize / 2;
        curHh = curHw;

        simBubbles = simBubbles.filter(b => b.id !== bestNeighbor.id);

        chainEvents.push({
          step: comboCount,
          tier: curTier,
          r: curR,
          g: curG,
          b: curB,
          desc: `Combo x${comboCount} with adjacent Block ${getTierValue(bestNeighbor.tier)}`
        });
      }
    }

    const colorInfo = this.getBubbleColor({ r: curR, g: curG, b: curB });
    const deltaUnits = deltaR + deltaG + deltaB;
    const predictedR = this.cumulativeR + deltaR;
    const predictedG = this.cumulativeG + deltaG;
    const predictedB = this.cumulativeB + deltaB;
    const predictedTotalUnits = predictedR + predictedG + predictedB;
    const predictedScore = this.score + deltaScore;
    const predictedMerges = this.totalMerges + chainEvents.length;
    const predictedPeakTier = Math.max(this.peakTier, curTier);
    const predictedCumulativeColor = this.getBubbleColor({ r: predictedR, g: predictedG, b: predictedB });
    const predictedBestBalance = Math.max(this.bestBalance, colorInfo.balance, predictedCumulativeColor.balance);

    return {
      willMerge: true,
      target: target,
      comboCount: comboCount,
      finalTier: curTier,
      expectedR: curR,
      expectedG: curG,
      expectedB: curB,
      totalUnits: curR + curG + curB,
      landingX: curX,
      landingY: curY,
      colorInfo: colorInfo,
      chainEvents: chainEvents,

      deltaR: deltaR,
      deltaG: deltaG,
      deltaB: deltaB,
      deltaUnits: deltaUnits,
      deltaScore: deltaScore,
      predictedScore: predictedScore,
      predictedR: predictedR,
      predictedG: predictedG,
      predictedB: predictedB,
      predictedTotalUnits: predictedTotalUnits,
      predictedMerges: predictedMerges,
      predictedPeakTier: predictedPeakTier,
      predictedCombo: simCombo,
      predictedCumulativeColor: predictedCumulativeColor,
      predictedBestBalance: predictedBestBalance
    };
  }

  updateShotForecastCard(forecast) {
    const card = document.getElementById('shot-forecast-card');
    const badge = document.getElementById('forecast-action-badge');
    const targetDesc = document.getElementById('forecast-target-desc');
    const resultWrap = document.getElementById('forecast-result-wrap');
    const resTier = document.getElementById('forecast-res-tier');
    const badgeR = document.getElementById('f-badge-r');
    const badgeG = document.getElementById('f-badge-g');
    const badgeB = document.getElementById('f-badge-b');
    const outcomeDesc = document.getElementById('forecast-outcome-desc');
    const hint = document.getElementById('forecast-hint');

    if (!card || !badge || !targetDesc) return;

    if (!forecast || !forecast.willMerge) {
      card.classList.remove('has-merge', 'has-combo');
      if (resultWrap) resultWrap.classList.add('hidden');
      if (forecast && forecast.reason === 'mismatch') {
        badge.textContent = 'STACKS / NO MERGE';
        badge.className = 'forecast-badge';
        const t = forecast.target;
        targetDesc.textContent = `Block ${getTierValue(t.tier)} [R:${t.r || 0} G:${t.g || 0} B:${t.b || 0}] (Mismatched Value)`;
        if (hint) hint.textContent = `Loaded Block ${getTierValue(this.readyBubble.tier)} will bounce & stack underneath`;
      } else {
        badge.textContent = 'OPEN LANE';
        badge.className = 'forecast-badge';
        targetDesc.textContent = 'Water Surface Ceiling (No Merge)';
        if (hint) hint.textContent = 'Will settle at the top water surface';
      }
      return;
    }

    // Merge or Combo cascade!
    if (resultWrap) resultWrap.classList.remove('hidden');

    if (forecast.comboCount > 1) {
      card.classList.remove('has-merge');
      card.classList.add('has-combo');
      badge.textContent = `⚡ COMBO x${forecast.comboCount}!`;
      badge.className = 'forecast-badge action-combo';
      targetDesc.textContent = `Hits Block ${getTierValue(forecast.target.tier)} ➔ Triggers ${forecast.comboCount}-Hit Cascade!`;
    } else {
      card.classList.remove('has-combo');
      card.classList.add('has-merge');
      badge.textContent = '🎯 DIRECT MERGE';
      badge.className = 'forecast-badge action-merge';
      targetDesc.textContent = `Hits Block ${getTierValue(forecast.target.tier)} [R:${forecast.target.r || 0} G:${forecast.target.g || 0} B:${forecast.target.b || 0}]`;
    }

    if (resTier) resTier.textContent = `BLOCK ${getTierValue(forecast.finalTier)}`;
    if (badgeR) badgeR.textContent = `🔴 R: ${forecast.expectedR}`;
    if (badgeG) badgeG.textContent = `🟢 G: ${forecast.expectedG}`;
    if (badgeB) badgeB.textContent = `🔵 B: ${forecast.expectedB}`;

    const colorName = forecast.colorInfo ? forecast.colorInfo.colorName : '';
    const balance = forecast.colorInfo ? forecast.colorInfo.balance : 0;
    if (outcomeDesc) {
      outcomeDesc.textContent = `Yields ${colorName} (${balance}% Whiteness) · +${forecast.totalUnits} Units`;
    }

    if (hint) {
      if (forecast.comboCount > 1) {
        hint.textContent = `Cascades ${forecast.comboCount} times into adjacent matching blocks!`;
      } else {
        hint.textContent = `Produces clean Block ${getTierValue(forecast.finalTier)}`;
      }
    }
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

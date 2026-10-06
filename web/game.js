// A.I.r Bubbles — n×n Grid Edition Game Controller
// Implements full inverted buoyancy, 12-tier grid bubbles, temperature rules,
// Lake Ellem score reservoir, and tactile push-out dynamics.

const TIERS = [
  { tier: 1,  name: "Token",       sub: "Unchecked Token",      color: "#00d2d3", text: "#003b3c" },
  { tier: 2,  name: "Context",     sub: "4k Window",            color: "#10ac84", text: "#023e2d" },
  { tier: 3,  name: "Colab",       sub: "Free GPU GPU",         color: "#2ed573", text: "#0c4e25" },
  { tier: 4,  name: "H100",        sub: "Silicon Gold",         color: "#ffa502", text: "#523200" },
  { tier: 5,  name: "Server",      sub: "Liquid Cooled",        color: "#ff7f50", text: "#581b04" },
  { tier: 6,  name: "Diesel",      sub: "Backup Gen",           color: "#ff4757", text: "#55070f" },
  { tier: 7,  name: "Dark Fiber",  sub: "Oceanic Glass",        color: "#ff3838", text: "#540606" },
  { tier: 8,  name: "SMR",         sub: "Nuclear Fission",      color: "#c56cf0", text: "#3d1054" },
  { tier: 9,  name: "Hyperscale",  sub: "Idaho MegaDC",         color: "#7158e2", text: "#1b114d" },
  { tier: 10, name: "Stargate",    sub: "1M Cluster",           color: "#3d3d3d", text: "#ffffff", border: "#67e6dc" },
  { tier: 11, name: "Unicorn",     sub: "Paper Valuation",      color: "#f1c40f", text: "#4d3a00", border: "#ffffff" },
  { tier: 12, name: "Singularity", sub: "Dyson Swarm (Max 12)", color: "#ffffff", text: "#d35400", border: "#ff3838" }
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
    this.startingPressure = 30.0;
    this.pressure = 30.0;
    this.maxPressure = 35.0; // Overpressure blowout
    this.targetPressure = 0.0; // Defusal goal
    this.blocksLaunched = 0; // Unlimited coolants supply
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

  rollSpawnTier() {
    const r = Math.random() * 100;
    if (r < 45) return 1;
    if (r < 75) return 2;
    if (r < 92) return 3;
    if (r < 98) return 4;
    return 5;
  }

  rollTempType() {
    const r = Math.random();
    if (r < 0.60) return 'hot';   // 60% Hot (6 in 10)
    return 'cold';                // 40% Cold (4 in 10, 0% Normal)
  }

  rollSpawn() {
    return {
      tier: this.rollSpawnTier(),
      tempType: this.rollTempType()
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
      this.readyBubble.tempType,
      this.launcherX,
      spawnY,
      -820 // Upward launch speed
    );
    this.physics.bubbles.push(b);

    // Camera punch
    this.cameraTrauma = Math.min(1.0, this.cameraTrauma + 0.15);

    // Spawn launcher bubbles at elongated vent nozzle tip
    const moteColor = this.readyBubble.tempType === 'hot'
      ? 'rgba(255, 69, 58, 0.85)'
      : (this.readyBubble.tempType === 'cold' ? 'rgba(0, 229, 255, 0.85)' : 'rgba(0, 229, 255, 0.6)');

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

    // 2. Score calculation: resulting tier * combo
    const pts = nextTier * this.combo;
    this.score += pts;

    // 3. Pressure rules (GAME_RULES.md 11-17)
    let pressureDelta = 0;
    const t1 = b1.tempType;
    const t2 = b2.tempType;

    if (t1 === 'hot' && t2 === 'hot') {
      pressureDelta = 2 * b1.tier;
      this.sound.playSteam();
    } else if ((t1 === 'hot' && t2 === 'normal') || (t1 === 'normal' && t2 === 'hot')) {
      pressureDelta = 1 * b1.tier;
      this.sound.playSteam();
    } else if (t1 === 'cold' && t2 === 'cold') {
      pressureDelta = -2 * b1.tier;
      this.sound.playFrost();
    } else if ((t1 === 'cold' && t2 === 'normal') || (t1 === 'normal' && t2 === 'cold')) {
      pressureDelta = -1 * b1.tier;
      this.sound.playFrost();
    }
    // hot + cold = 0, normal + normal = 0

    const prevPressure = this.pressure;
    this.pressure = Math.max(0.0, this.pressure + pressureDelta);

    // Warning alert ping only when pressure reaches 20 PSI
    if (this.pressure >= 20.0 && prevPressure < 20.0) {
      this.sound.playWarningPing();
    }

    // Audio chime
    this.sound.playMerge(nextTier, this.combo);

    // Midpoint
    const midX = (b1.x + b2.x) / 2;
    const midY = (b1.y + b2.y) / 2;

    // Remove old bubbles
    this.physics.bubbles = this.physics.bubbles.filter(b => b.id !== b1.id && b.id !== b2.id);

    // 4. Spawn new (n+1) bubble
    const newBubble = this.physics.createBubble(
      nextTier,
      'normal', // children come out normal per rule
      midX,
      midY,
      (b1.vy + b2.vy) * 0.4
    );
    newBubble.wobbleX = 1.35; // Expand spring
    this.physics.bubbles.push(newBubble);

    // 5. THE KEY PUSH-OUT MECHANIC:
    // When a bigger square appears, it pushes all neighbors out of its footprint!
    this.physics.applyPushOut(newBubble);

    // Visual shockwave
    this.shockwaves.push({
      x: midX,
      y: midY,
      r: newBubble.size / 2,
      maxR: newBubble.size * 1.6,
      color: TIERS[nextTier - 1]?.color || '#ffffff',
      life: 0.35,
      maxLife: 0.35
    });

    // Score Popup
    const comboText = this.combo > 1 ? ` COMBO x${this.combo}!` : '';
    this.popups.push({
      x: midX,
      y: midY - 20,
      text: `+${pts}${comboText}`,
      color: '#ffd700',
      size: nextTier === 12 ? 22 : 16,
      life: 1.0
    });

    if (pressureDelta > 0) {
      this.popups.push({
        x: midX + 25,
        y: midY - 5,
        text: `+${pressureDelta} PSI`,
        color: '#ff453a',
        size: 13,
        life: 0.9
      });
    } else if (pressureDelta < 0) {
      this.popups.push({
        x: midX + 25,
        y: midY - 5,
        text: `${pressureDelta} PSI`,
        color: '#30d158',
        size: 13,
        life: 0.9
      });
    }

    // Camera trauma
    this.cameraTrauma = Math.min(1.0, this.cameraTrauma + 0.3 + (nextTier * 0.04));

    // Particle fountain to Lake Ellem
    for (let i = 0; i < 10 + nextTier * 2; i++) {
      this.particles.push({
        x: midX + (Math.random() - 0.5) * 20,
        y: midY + (Math.random() - 0.5) * 20,
        vx: (Math.random() - 0.5) * 160,
        vy: -100 - Math.random() * 200,
        r: 3 + Math.random() * 3,
        color: TIERS[nextTier - 1]?.color || '#ffd700',
        life: 0.6 + Math.random() * 0.4
      });
    }

    // Check Defusal Victory (<= 0.0 PSI reached!)
    if (this.pressure <= 0.0 && !this.isWon && !this.isGameOver) {
      this.pressure = 0.0;
      this.triggerDefusedVictory();
      return;
    }

    // Check Overpressure Blowout (>= 35.0 PSI)
    if (this.pressure >= this.maxPressure && !this.isGameOver && !this.isWon) {
      this.triggerOverpressure();
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

  triggerDefusedVictory() {
    this.isWon = true;
    this.isGameOver = true;
    this.sound.playSingularity();
    this.cameraTrauma = 0.7;

    const chamber = this.physics.chamber;
    for (let i = 0; i < 70; i++) {
      const angle = (Math.PI * 2 * i) / 70;
      const spd = 140 + Math.random() * 260;
      this.particles.push({
        x: chamber.x + chamber.w / 2,
        y: chamber.y + chamber.h / 2,
        vx: Math.cos(angle) * spd,
        vy: Math.sin(angle) * spd,
        r: 3 + Math.random() * 4,
        color: ['#00e5ff', '#30d158', '#ffd700', '#ffffff'][i % 4],
        life: 1.6
      });
    }

    const badge = document.getElementById('game-over-badge');
    badge.textContent = 'CORE DEFUSED! (0.0 PSI)';
    badge.style.background = 'rgba(48, 209, 88, 0.2)';
    badge.style.borderColor = '#30d158';
    badge.style.color = '#30d158';
    document.getElementById('game-over-title').textContent = 'Thermal Core Stabilized!';
    document.getElementById('game-over-desc').textContent = `Mission Accomplished! You successfully cooled the hydrothermal core down from 30.0 PSI to 0.0 PSI using ${this.blocksLaunched} blocks.`;
    this.showGameOverModal();
  }

  triggerOverpressure() {
    this.isGameOver = true;
    this.sound.playOverheat();
    this.cameraTrauma = 1.0;

    const badge = document.getElementById('game-over-badge');
    badge.textContent = 'CRITICAL BLOWOUT (35.0 PSI)';
    badge.style.background = 'rgba(255, 69, 58, 0.2)';
    badge.style.borderColor = '#ff453a';
    badge.style.color = '#ff453a';
    document.getElementById('game-over-title').textContent = 'The System Has Exploded';
    document.getElementById('game-over-desc').textContent = 'Thermal spikes reached 35.0 PSI. The hydrothermal vent cluster suffered catastrophic decompression.';
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
    document.getElementById('game-over-title').textContent = 'The Seabed Has Jammed';
    document.getElementById('game-over-desc').textContent = 'Bubbles stacked down past the hydrothermal vent danger line for over 3 seconds.';
    this.showGameOverModal();
  }

  showGameOverModal() {
    document.getElementById('modal-final-score').textContent = this.score;
    document.getElementById('modal-peak-tier').textContent = `${this.peakTier} (${TIERS[this.peakTier - 1]?.name || ''})`;
    document.getElementById('modal-total-merges').textContent = this.totalMerges;
    document.getElementById('modal-total-pushouts').textContent = this.physics.pushoutCount;
    document.getElementById('game-over-modal').classList.remove('hidden');
  }

  restart() {
    this.isGameOver = false;
    this.isWon = false;
    this.score = 0;
    this.pressure = 30.0;
    this.blocksLaunched = 0;
    this.combo = 1;
    this.totalMerges = 0;
    this.peakTier = 1;
    this.dangerTimer = 3.0;
    this.settleTimer = 0.0;
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

    // Update Pressure HUD (Reversed: starts at 30.0 PSI, goal is 0.0 PSI, max is 35.0 PSI)
    if (this.uiPressure) {
      this.uiPressure.textContent = `${this.pressure.toFixed(1)} / 35 PSI`;
      if (this.pressure <= 0.0) {
        this.uiPressureStatus.textContent = '✅ DEFUSED (0.0)';
        this.uiPressureStatus.className = 'stat-sub';
        this.uiPressure.style.color = '#30d158';
      } else if (this.pressure >= 30.0) {
        this.uiPressureStatus.textContent = '🔥 BURST RISK (MAX: 35)';
        this.uiPressureStatus.className = 'stat-sub warning';
        this.uiPressure.style.color = '#ff3b30';
      } else if (this.pressure >= 20.0) {
        this.uiPressureStatus.textContent = '⚠️ ELEVATED (MAX: 35)';
        this.uiPressureStatus.className = 'stat-sub warning';
        this.uiPressure.style.color = '#ffd60a';
      } else if (this.pressure >= 10.0) {
        this.uiPressureStatus.textContent = '⚡ STABILIZING';
        this.uiPressureStatus.className = 'stat-sub';
        this.uiPressure.style.color = '#00e5ff';
      } else {
        this.uiPressureStatus.textContent = '❄️ COOLING DOWN';
        this.uiPressureStatus.className = 'stat-sub';
        this.uiPressure.style.color = '#30d158';
      }
    }

    // Update Blocks Launched HUD (Unlimited supply)
    if (this.uiBlocks) {
      this.uiBlocks.textContent = `${this.blocksLaunched}`;
      this.uiBlocks.style.color = '#00e5ff';
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

    // 2. Draw Vertical Pressure Gauge to the Side of the Grid
    this.renderPressureGauge(ctx, this.physics.gauge);

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

  // Vertical Pressure Gauge to the side of the grid
  renderPressureGauge(ctx, gauge) {
    if (!gauge) return;
    const gx = gauge.x;
    const gy = gauge.y;
    const gw = gauge.w;
    const gh = gauge.h;

    ctx.save();

    // 1. Manometer Column Frame
    ctx.fillStyle = '#081324';
    ctx.strokeStyle = 'rgba(64, 128, 200, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(gx, gy, gw, gh, 6);
    ctx.fill();
    ctx.stroke();

    // Top Header: PSI
    ctx.fillStyle = '#8b9bb4';
    ctx.font = 'bold 8px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('PSI', gx + gw / 2, gy + 11);

    // 2. Glass Tube
    const tubeX = gx + 6;
    const tubeY = gy + 18;
    const tubeW = Math.max(10, gw - 12);
    const tubeH = gh - 46;
    const tubeBottom = tubeY + tubeH;

    // Tube background
    ctx.fillStyle = '#03070f';
    ctx.beginPath();
    ctx.roundRect(tubeX, tubeY, tubeW, tubeH, 4);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // 3. Fluid column (0 to 35.0 PSI scale)
    const maxGauge = 35.0;
    const clampedPressure = Math.min(maxGauge, Math.max(0.0, this.pressure));
    const fillRatio = clampedPressure / maxGauge;
    const fillH = tubeH * fillRatio;
    const fluidTop = tubeBottom - fillH;

    if (fillH > 0) {
      ctx.save();
      const grad = ctx.createLinearGradient(0, tubeBottom, 0, fluidTop);
      if (this.pressure >= 30.0) {
        // Critical burst zone (30 - 35 PSI)
        grad.addColorStop(0, '#ffd60a');
        grad.addColorStop(1, '#ff3b30');
        ctx.shadowColor = '#ff3b30';
        ctx.shadowBlur = 12;
      } else if (this.pressure >= 20.0) {
        // Warning elevated state
        grad.addColorStop(0, '#00e5ff');
        grad.addColorStop(1, '#ffd60a');
        ctx.shadowColor = '#ffd60a';
        ctx.shadowBlur = 8;
      } else {
        // Nominal cooling state
        grad.addColorStop(0, '#30d158');
        grad.addColorStop(1, '#00e5ff');
      }

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.roundRect(tubeX + 1, fluidTop, tubeW - 2, fillH, [2, 2, 3, 3]);
      ctx.fill();
      ctx.restore();
    }

    // 4. Tick Marks & Numbers (35 at top, 30 start, 20 warning, 10, 0 at bottom)
    const y35 = tubeY;
    const y30 = tubeBottom - (tubeH * (30 / maxGauge));
    const y20 = tubeBottom - (tubeH * (20 / maxGauge));
    const y10 = tubeBottom - (tubeH * (10 / maxGauge));
    const y0 = tubeBottom;

    // Line 35 (Blowout redline limit)
    ctx.strokeStyle = '#ff3b30';
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    ctx.moveTo(tubeX - 2, y35);
    ctx.lineTo(tubeX + tubeW + 2, y35);
    ctx.stroke();

    // Line 30 (Starting pressure level)
    ctx.strokeStyle = '#ff7f50';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(tubeX, y30);
    ctx.lineTo(tubeX + tubeW, y30);
    ctx.stroke();

    // Line 20 (Warning threshold)
    ctx.strokeStyle = '#ffd60a';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(tubeX, y20);
    ctx.lineTo(tubeX + tubeW, y20);
    ctx.stroke();

    // Line 10 (Cooling threshold)
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.5)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(tubeX, y10);
    ctx.lineTo(tubeX + tubeW, y10);
    ctx.stroke();

    // Line 0 (Target Goal line)
    ctx.strokeStyle = '#30d158';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(tubeX - 2, y0);
    ctx.lineTo(tubeX + tubeW + 2, y0);
    ctx.stroke();

    // Tick labels
    ctx.font = 'bold 7px sans-serif';
    ctx.textAlign = 'center';

    // 35 MAX BURST
    ctx.fillStyle = '#ff3b30';
    ctx.fillText('35', gx + gw / 2, y35 + 8);

    // 30 START
    ctx.fillStyle = '#ff7f50';
    ctx.fillText('30', gx + gw / 2, y30 - 2);

    // 20
    ctx.fillStyle = '#ffd60a';
    ctx.fillText('20', gx + gw / 2, y20 - 2);

    // 10
    ctx.fillStyle = '#00e5ff';
    ctx.fillText('10', gx + gw / 2, y10 - 2);

    // 0
    ctx.fillStyle = '#30d158';
    ctx.fillText('0', gx + gw / 2, y0 - 3);

    // 5. Live Digital Readout at bottom of gauge frame
    ctx.save();
    if (this.pressure <= 0.0) {
      ctx.fillStyle = '#30d158';
      ctx.shadowColor = '#30d158';
      ctx.shadowBlur = 6;
      ctx.font = 'bold 8px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('DEFUSED', gx + gw / 2, gy + gh - 8);
    } else {
      ctx.fillStyle = this.pressure >= 30.0 ? '#ff3b30' : (this.pressure >= 20.0 ? '#ffd60a' : '#00e5ff');
      if (this.pressure >= 30.0) {
        ctx.shadowColor = '#ff3b30';
        ctx.shadowBlur = 6;
      }
      ctx.font = 'bold 8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`${this.pressure.toFixed(1)}`, gx + gw / 2, gy + gh - 8);
    }
    ctx.restore();

    ctx.restore();
  }

  renderBubble(ctx, b) {
    const tierInfo = TIERS[b.tier - 1] || TIERS[0];
    const isGrid = (this.physics.mode === 'grid');

    ctx.save();
    ctx.translate(b.x, b.y);
    ctx.scale(b.wobbleX, b.wobbleY);

    if (isGrid) {
      // 🟦 RENDER n×n SUBDIVIDED GRID BOX
      const hw = b.hw;
      const hh = b.hh;
      const r = Math.min(6, b.hw * 0.2);

      // Outer glow for hot (red) / cold (blue) / singularity
      if (b.tempType === 'hot') {
        ctx.shadowColor = '#ff453a'; // Vibrant Red
        ctx.shadowBlur = 14;
      } else if (b.tempType === 'cold') {
        ctx.shadowColor = '#00e5ff'; // Vibrant Icy Blue
        ctx.shadowBlur = 14;
      } else if (b.isSingularity) {
        ctx.shadowColor = '#ffd700';
        ctx.shadowBlur = 20;
      }

      // Box body
      ctx.fillStyle = tierInfo.color;
      ctx.beginPath();
      ctx.roundRect(-hw, -hh, b.size, b.size, r);
      ctx.fill();

      // Border: Hot is Red, Cold is Icy Blue, Normal is default
      ctx.strokeStyle = b.tempType === 'hot' ? '#ff3b30' : (b.tempType === 'cold' ? '#00e5ff' : (tierInfo.border || 'rgba(255,255,255,0.4)'));
      ctx.lineWidth = b.tempType !== 'normal' ? 3.0 : 1.5;
      ctx.stroke();

      // Inner n×n Sub-grid Lines
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.18)';
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

      // Center number badge
      ctx.fillStyle = tierInfo.text;
      ctx.font = `bold ${Math.max(10, Math.min(22, b.size * 0.42))}px -apple-system, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${b.tier}`, 0, (b.size >= 36 ? -4 : 0));

      // Label below number if large enough
      if (b.size >= 48) {
        ctx.font = `bold ${Math.max(8, Math.min(11, b.size * 0.16))}px sans-serif`;
        ctx.fillText(tierInfo.name, 0, b.size * 0.24);
      }
    } else {
      // ⚪ RENDER CLASSIC CIRCLE
      if (b.tempType === 'hot') {
        ctx.shadowColor = '#ff453a';
        ctx.shadowBlur = 14;
      } else if (b.tempType === 'cold') {
        ctx.shadowColor = '#00e5ff';
        ctx.shadowBlur = 14;
      }

      ctx.fillStyle = tierInfo.color;
      ctx.beginPath();
      ctx.arc(0, 0, b.radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = b.tempType === 'hot' ? '#ff3b30' : (b.tempType === 'cold' ? '#00e5ff' : 'rgba(255,255,255,0.5)');
      ctx.lineWidth = b.tempType !== 'normal' ? 3.0 : 2.0;
      ctx.stroke();

      ctx.fillStyle = tierInfo.text;
      ctx.font = `bold ${Math.max(10, Math.min(20, b.radius * 0.75))}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${b.tier}`, 0, 0);
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
      const tierInfo = TIERS[this.readyBubble.tier - 1] || TIERS[0];

      ctx.save();
      ctx.translate(lx, py);
      ctx.globalAlpha = 0.9;

      // Thermal glow on ready bubble if hot (red) or cold (blue)
      if (this.readyBubble.tempType === 'hot') {
        ctx.shadowColor = '#ff453a';
        ctx.shadowBlur = 14;
      } else if (this.readyBubble.tempType === 'cold') {
        ctx.shadowColor = '#00e5ff';
        ctx.shadowBlur = 14;
      }

      if (this.physics.mode === 'grid') {
        const hw = previewSize / 2;
        ctx.fillStyle = tierInfo.color;
        ctx.beginPath();
        ctx.roundRect(-hw, -hw, previewSize, previewSize, 4);
        ctx.fill();

        ctx.strokeStyle = this.readyBubble.tempType === 'hot' ? '#ff3b30' : (this.readyBubble.tempType === 'cold' ? '#00e5ff' : '#ffffff');
        ctx.lineWidth = this.readyBubble.tempType !== 'normal' ? 2.5 : 1.5;
        ctx.stroke();

        ctx.fillStyle = tierInfo.text;
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${this.readyBubble.tier}`, 0, 0);
      } else {
        ctx.fillStyle = tierInfo.color;
        ctx.beginPath();
        ctx.arc(0, 0, previewSize / 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = this.readyBubble.tempType === 'hot' ? '#ff3b30' : (this.readyBubble.tempType === 'cold' ? '#00e5ff' : '#ffffff');
        ctx.lineWidth = this.readyBubble.tempType !== 'normal' ? 2.5 : 1.5;
        ctx.stroke();

        ctx.fillStyle = tierInfo.text;
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

    const tierInfo = TIERS[this.nextBubble.tier - 1] || TIERS[0];
    const previewSize = Math.min(36, 12 + this.nextBubble.tier * 5);
    const hw = previewSize / 2;

    ctx.save();
    ctx.translate(30, 30);

    // Thermal glow for hot (red) or cold (blue)
    if (this.nextBubble.tempType === 'hot') {
      ctx.shadowColor = '#ff453a';
      ctx.shadowBlur = 10;
    } else if (this.nextBubble.tempType === 'cold') {
      ctx.shadowColor = '#00e5ff';
      ctx.shadowBlur = 10;
    }

    ctx.fillStyle = tierInfo.color;

    if (this.physics.mode === 'grid') {
      ctx.beginPath();
      ctx.roundRect(-hw, -hw, previewSize, previewSize, 3);
      ctx.fill();
      ctx.strokeStyle = this.nextBubble.tempType === 'hot' ? '#ff3b30' : (this.nextBubble.tempType === 'cold' ? '#00e5ff' : '#ffffff');
      ctx.lineWidth = this.nextBubble.tempType !== 'normal' ? 2.5 : 1.5;
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(0, 0, hw, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = this.nextBubble.tempType === 'hot' ? '#ff3b30' : (this.nextBubble.tempType === 'cold' ? '#00e5ff' : '#ffffff');
      ctx.lineWidth = this.nextBubble.tempType !== 'normal' ? 2.5 : 1.5;
      ctx.stroke();
    }

    ctx.fillStyle = tierInfo.text;
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${this.nextBubble.tier}`, 0, 0);
    ctx.restore();
  }

  renderEvolutionStrip() {
    const container = document.getElementById('evo-scroll-container');
    container.innerHTML = '';
    TIERS.forEach(t => {
      const item = document.createElement('div');
      item.className = 'evo-item';
      item.innerHTML = `
        <div class="evo-badge" style="background:${t.color}; color:${t.text};">${t.tier}</div>
        <div class="evo-name">${t.tier}×${t.tier} ${t.name}</div>
      `;
      container.appendChild(item);
    });
  }

  generateQRCode() {
    const url = `http://192.168.1.225:8085`;
    const label = document.getElementById('qr-url-text');
    if (label) label.textContent = url;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.airBubbleGame = new AirBubbleGame();
});

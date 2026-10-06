// Procedural Audio Engine using Web Audio API (Zero Cloud Spend, Zero External Assets)
class SoundEngine {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this.unlocked = false;
    // Scale for Tiers 1 through 12: C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5
    this.frequencies = [
      261.63, 293.66, 329.63, 349.23, 392.00, 440.00,
      493.88, 523.25, 587.33, 659.25, 698.46, 783.99
    ];
  }

  ensureContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    return this.muted;
  }

  // Underwater vent launch pop
  playLaunch() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(320, t);
    osc.frequency.exponentialRampToValueAtTime(80, t + 0.12);

    gain.gain.setValueAtTime(0.25, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(t);
    osc.stop(t + 0.13);
  }

  // Musical chime on merge
  playMerge(tier, combo = 1) {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    const baseFreq = this.frequencies[Math.min(tier - 1, this.frequencies.length - 1)] || 440;

    // Primary bell tone
    const osc1 = this.ctx.createOscillator();
    const gain1 = this.ctx.createGain();
    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(baseFreq, t);

    // Harmonic overtone
    const osc2 = this.ctx.createOscillator();
    const gain2 = this.ctx.createGain();
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(baseFreq * 2, t);

    const dur = 0.28 + Math.min(tier * 0.03, 0.3);
    const vol = 0.22;

    gain1.gain.setValueAtTime(vol, t);
    gain1.gain.exponentialRampToValueAtTime(0.001, t + dur);

    gain2.gain.setValueAtTime(vol * 0.4, t);
    gain2.gain.exponentialRampToValueAtTime(0.001, t + dur * 0.7);

    osc1.connect(gain1);
    osc2.connect(gain2);
    gain1.connect(this.ctx.destination);
    gain2.connect(this.ctx.destination);

    osc1.start(t);
    osc2.start(t);
    osc1.stop(t + dur + 0.05);
    osc2.stop(t + dur + 0.05);

    // If combo > 1, add an arpeggiated sparkle
    if (combo > 1) {
      setTimeout(() => {
        if (!this.ctx) return;
        const t2 = this.ctx.currentTime;
        const oscC = this.ctx.createOscillator();
        const gainC = this.ctx.createGain();
        oscC.type = 'sine';
        oscC.frequency.setValueAtTime(baseFreq * 1.5, t2);
        gainC.gain.setValueAtTime(0.15, t2);
        gainC.gain.exponentialRampToValueAtTime(0.001, t2 + 0.2);
        oscC.connect(gainC);
        gainC.connect(this.ctx.destination);
        oscC.start(t2);
        oscC.stop(t2 + 0.22);
      }, 70);
    }
  }

  // Hot steam hiss
  playSteam() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    const dur = 0.15;
    const bufferSize = this.ctx.sampleRate * dur;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = Math.random() * 2 - 1;
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 2200;
    filter.Q.value = 3.0;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.12, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + dur);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);

    noise.start(t);
  }

  // Cold frost ring
  playFrost() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1100, t);
    osc.frequency.exponentialRampToValueAtTime(1600, t + 0.18);

    gain.gain.setValueAtTime(0.14, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.18);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + 0.2);
  }

  // Size 12 Singularity Supernova Fanfare & Disappearance
  playSingularity() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    // 4 chord progression: C4 -> E4 -> G4 -> C5
    const chord = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99];
    chord.forEach((freq, idx) => {
      const delay = idx * 0.08;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, t + delay);

      const filter = this.ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1200, t + delay);
      filter.frequency.exponentialRampToValueAtTime(300, t + delay + 1.2);

      gain.gain.setValueAtTime(0.18, t + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, t + delay + 1.2);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t + delay);
      osc.stop(t + delay + 1.25);
    });

    // Sub-bass thump
    const sub = this.ctx.createOscillator();
    const subGain = this.ctx.createGain();
    sub.type = 'sine';
    sub.frequency.setValueAtTime(120, t);
    sub.frequency.exponentialRampToValueAtTime(35, t + 0.8);
    subGain.gain.setValueAtTime(0.4, t);
    subGain.gain.exponentialRampToValueAtTime(0.001, t + 0.8);
    sub.connect(subGain);
    subGain.connect(this.ctx.destination);
    sub.start(t);
    sub.stop(t + 0.85);
  }

  // Pressure Warning sonar alarm ping (triggered only when reaching 20 PSI)
  playWarningPing() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, t);
    osc.frequency.setValueAtTime(1174, t + 0.08); // High alert ping

    gain.gain.setValueAtTime(0.22, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.28);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(t);
    osc.stop(t + 0.3);
  }

  // Overheat / Overpressure Burst explosion
  playOverheat() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(220, t);
    osc.frequency.exponentialRampToValueAtTime(40, t + 0.6);
    gain.gain.setValueAtTime(0.35, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.6);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + 0.65);
  }

  // Celestial shimmering arpeggio when Pure White (100% RGB balance) is achieved!
  playWhiteEquilibriumChime() {
    if (this.muted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const t = this.ctx.currentTime;
    // C5, E5, G5, B5, C6 shimmering harmonic ladder
    const notes = [523.25, 659.25, 783.99, 987.77, 1046.50];

    notes.forEach((freq, idx) => {
      const delay = idx * 0.06;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, t + delay);

      gain.gain.setValueAtTime(0.28, t + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, t + delay + 1.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t + delay);
      osc.stop(t + delay + 1.45);
    });
  }
}

window.soundEngine = new SoundEngine();

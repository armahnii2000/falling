// Physics & Simulation Engine for n×n Grid & Inverted Buoyancy Suika
// Designed for high performance, smooth mobile frame rates, and tactile push-out mechanics.

class PhysicsEngine {
  constructor() {
    this.cols = 16;       // 16 grid columns wide
    this.rows = 24;       // 24 grid rows tall
    this.cellSize = 20;   // In pixels, dynamically adapted to viewport
    this.chamber = { x: 0, y: 0, w: 320, h: 480 };
    this.gauge = { x: 0, y: 0, w: 30, h: 480 };
    this.dangerY = 0;

    this.bubbles = [];
    this.mode = 'grid'; // 'grid' (n×n squares) or 'circle'
    this.buoyancy = -880; // px/s² upward
    this.drag = 0.985;
    this.restitution = 0.25;
    this.friction = 0.88;

    this.pushoutCount = 0;
    this.nextId = 1;
  }

  updateDimensions(canvasWidth, canvasHeight) {
    // Allocate space for the vertical pressure gauge to the side
    const gaugeW = 28;
    const gap = 12;
    const padX = 14;
    const topMargin = 24;      // Clear headroom so the water ceiling is never hidden under the top
    const bottomMargin = 20;   // Clean spacing for the doubled 28px vent nozzle floor

    const availableW = Math.max(120, Math.min(canvasWidth - padX * 2 - gaugeW - gap, 460));
    const availableH = Math.max(120, canvasHeight - topMargin - bottomMargin);

    // Fit BOTH width and height so the chamber never clips offscreen on desktop or mobile
    const cellFromW = Math.floor(availableW / this.cols);
    const cellFromH = Math.floor(availableH / this.rows);
    this.cellSize = Math.max(8, Math.min(cellFromW, cellFromH));

    const chamberW = this.cols * this.cellSize;
    const chamberH = this.rows * this.cellSize;

    const totalStageW = chamberW + gap + gaugeW;
    const stageLeft = Math.max(padX, Math.floor((canvasWidth - totalStageW) / 2));
    
    // Always guarantee at least topMargin pixels of headroom at the ceiling
    const remainingH = canvasHeight - chamberH;
    const stageTop = Math.max(topMargin, Math.floor(remainingH / 2));

    this.chamber = {
      x: stageLeft,
      y: stageTop,
      w: chamberW,
      h: chamberH
    };

    this.gauge = {
      x: stageLeft + chamberW + gap,
      y: stageTop,
      w: gaugeW,
      h: chamberH
    };

    // Danger line is 4.5 rows above the bottom vent floor
    this.dangerY = this.chamber.y + (this.rows - 4.5) * this.cellSize;
  }

  createBubble(tier, colorData, x, y, vy = -780) {
    const size = tier * this.cellSize;
    const rCount = (typeof colorData === 'object' && colorData !== null) ? (colorData.r || 0) : (colorData === 'hot' ? tier : 0);
    const gCount = (typeof colorData === 'object' && colorData !== null) ? (colorData.g || 0) : 0;
    const bCount = (typeof colorData === 'object' && colorData !== null) ? (colorData.b || 0) : (colorData === 'cold' ? tier : 0);

    const b = {
      id: this.nextId++,
      tier: tier,
      r: rCount,
      g: gCount,
      b: bCount,
      x: x,
      y: y,
      vx: (Math.random() - 0.5) * 40,
      vy: vy,
      size: size,
      hw: size / 2,
      hh: size / 2,
      radius: size / 2,
      mass: Math.pow(tier, 2),
      age: 0,
      settled: false,
      merging: false,
      wobbleX: 1.0,
      wobbleY: 1.0,
      wobbleVel: 0,
      isSingularity: (tier >= 12),
      singularityTimer: (tier >= 12 ? 0.6 : 0)
    };
    return b;
  }

  step(dt, onMerge, onSingularityPop) {
    const subSteps = 4;
    const subDt = dt / subSteps;

    for (let s = 0; s < subSteps; s++) {
      this._subStep(subDt, onMerge, onSingularityPop);
    }

    // Update cosmetic wobbles, ages, and settled flags
    for (let i = this.bubbles.length - 1; i >= 0; i--) {
      const b = this.bubbles[i];
      b.age += dt;

      // Handle Tier 12 Singularity auto-disappear
      if (b.isSingularity) {
        b.singularityTimer -= dt;
        if (b.singularityTimer <= 0 && !b.merging) {
          b.merging = true;
          this.bubbles.splice(i, 1);
          if (onSingularityPop) onSingularityPop(b);
          continue;
        }
      }

      // Wobble spring decay
      const k = 140;
      const d = 12;
      const forceX = -k * (b.wobbleX - 1.0) - d * b.wobbleVel;
      b.wobbleVel += forceX * dt;
      b.wobbleX += b.wobbleVel * dt;
      b.wobbleY = 1.0 + (1.0 - b.wobbleX) * 0.75; // Volume preservation

      // Settled check: bubble is near ceiling or another bubble and moving slowly
      const speed = Math.hypot(b.vx, b.vy);
      b.settled = (b.age > 0.4 && speed < 45);
    }
  }

  _subStep(dt, onMerge, onSingularityPop) {
    const left = this.chamber.x;
    const right = this.chamber.x + this.chamber.w;
    const top = this.chamber.y;
    const bottom = this.chamber.y + this.chamber.h;

    // 1. Integrate forces and velocities
    for (let i = 0; i < this.bubbles.length; i++) {
      const b = this.bubbles[i];
      if (b.merging) continue;

      // Upward buoyant acceleration
      b.vy += this.buoyancy * dt;

      // Drag
      b.vx *= Math.pow(this.drag, dt * 60);
      b.vy *= Math.pow(this.drag, dt * 60);

      // Position update
      b.x += b.vx * dt;
      b.y += b.vy * dt;

      // Wall and ceiling boundaries
      const hw = (this.mode === 'grid') ? b.hw : b.radius;
      const hh = (this.mode === 'grid') ? b.hh : b.radius;

      // Left wall
      if (b.x - hw < left) {
        b.x = left + hw;
        b.vx = -b.vx * this.restitution;
      }
      // Right wall
      if (b.x + hw > right) {
        b.x = right - hw;
        b.vx = -b.vx * this.restitution;
      }
      // Top ceiling (water surface)
      if (b.y - hh < top) {
        b.y = top + hh;
        b.vy = Math.abs(b.vy) * 0.15; // Soft ceiling bounce
        b.vx *= this.friction;       // Ceiling friction
      }
      // Floor (bottom)
      if (b.y + hh > bottom) {
        b.y = bottom - hh;
        b.vy = -Math.abs(b.vy) * 0.3;
      }
    }

    // 2. Pairwise collisions & merges
    let mergedPair = null;
    for (let i = 0; i < this.bubbles.length; i++) {
      const b1 = this.bubbles[i];
      if (!b1 || b1.merging) continue;

      for (let j = i + 1; j < this.bubbles.length; j++) {
        if (b1.merging) break;
        const b2 = this.bubbles[j];
        if (!b2 || b2.merging) continue;

        const didMerge = (this.mode === 'grid')
          ? this._resolveBoxCollision(b1, b2)
          : this._resolveCircleCollision(b1, b2);

        if (didMerge) {
          mergedPair = [b1, b2];
          break;
        }
      }
      if (mergedPair) break;
    }

    if (mergedPair && onMerge) {
      onMerge(mergedPair[0], mergedPair[1]);
    }
  }

  _resolveBoxCollision(b1, b2) {
    const dx = b2.x - b1.x;
    const dy = b2.y - b1.y;
    const minDistX = b1.hw + b2.hw;
    const minDistY = b1.hh + b2.hh;

    const ox = minDistX - Math.abs(dx);
    const oy = minDistY - Math.abs(dy);

    // Check for identical tier merge (Tiers 1 to 11 can merge into next tier)
    if (b1.tier === b2.tier && b1.tier < 12 && !b1.merging && !b2.merging) {
      // 1. Direct 2D overlap
      const isDirectOverlap = (ox > 0 && oy > 0);

      // 2. Side-by-side face contact (touching within 3.5px tolerance with vertical overlap)
      const isSideBySide = (ox >= -3.5 && oy > Math.min(b1.hh, b2.hh) * 0.35);

      // 3. Top-and-bottom face contact (touching within 3.5px tolerance with horizontal overlap)
      const isTopBottom = (oy >= -3.5 && ox > Math.min(b1.hw, b2.hw) * 0.35);

      if (isDirectOverlap || isSideBySide || isTopBottom) {
        b1.merging = true;
        b2.merging = true;
        return true;
      }
    }

    if (ox > 0 && oy > 0) {
      // Physical contact & separation
      const totalMass = b1.mass + b2.mass;
      const m1Ratio = b2.mass / totalMass;
      const m2Ratio = b1.mass / totalMass;

      if (ox < oy) {
        // Separate along X axis
        const sx = dx > 0 ? 1 : -1;
        b1.x -= sx * ox * m1Ratio;
        b2.x += sx * ox * m2Ratio;

        const relVx = b2.vx - b1.vx;
        const impX = relVx * (1 + this.restitution) * (b1.mass * b2.mass / totalMass);
        b1.vx += impX / b1.mass;
        b2.vx -= impX / b2.mass;

        // Friction along Y
        b1.vy *= this.friction;
        b2.vy *= this.friction;
      } else {
        // Separate along Y axis
        const sy = dy > 0 ? 1 : -1;
        b1.y -= sy * oy * m1Ratio;
        b2.y += sy * oy * m2Ratio;

        const relVy = b2.vy - b1.vy;
        const impY = relVy * (1 + this.restitution) * (b1.mass * b2.mass / totalMass);
        b1.vy += impY / b1.mass;
        b2.vy -= impY / b2.mass;

        // Friction along X
        b1.vx *= this.friction;
        b2.vx *= this.friction;
      }
    }
    return false;
  }

  _resolveCircleCollision(b1, b2) {
    const dx = b2.x - b1.x;
    const dy = b2.y - b1.y;
    const dist = Math.hypot(dx, dy);
    const minDist = b1.radius + b2.radius;

    if (dist < minDist && dist > 0.001) {
      if (b1.tier === b2.tier && b1.tier < 12 && !b1.merging && !b2.merging) {
        b1.merging = true;
        b2.merging = true;
        return true;
      }

      const overlap = minDist - dist;
      const nx = dx / dist;
      const ny = dy / dist;

      const totalMass = b1.mass + b2.mass;
      const m1Ratio = b2.mass / totalMass;
      const m2Ratio = b1.mass / totalMass;

      b1.x -= nx * overlap * m1Ratio;
      b1.y -= ny * overlap * m1Ratio;
      b2.x += nx * overlap * m2Ratio;
      b2.y += ny * overlap * m2Ratio;

      const kx = b1.vx - b2.vx;
      const ky = b1.vy - b2.vy;
      const p = 2 * (nx * kx + ny * ky) / totalMass;

      b1.vx -= p * b2.mass * nx * (1 + this.restitution);
      b1.vy -= p * b2.mass * ny * (1 + this.restitution);
      b2.vx += p * b1.mass * nx * (1 + this.restitution);
      b2.vy += p * b1.mass * ny * (1 + this.restitution);
    }
  }

  // THE KEY PUSH-OUT MECHANIC:
  // When an (n+1)×(n+1) box is created, it expands and forcefully displaces
  // all neighboring boxes out of its footprint!
  applyPushOut(newBox) {
    this.pushoutCount++;
    const pushRadius = newBox.size * 1.35;
    const baseImpulse = 380 + newBox.tier * 35;

    for (let i = 0; i < this.bubbles.length; i++) {
      const other = this.bubbles[i];
      if (other.id === newBox.id || other.merging) continue;

      const dx = other.x - newBox.x;
      const dy = other.y - newBox.y;
      const dist = Math.hypot(dx, dy) || 1;

      // Check for overlap or immediate proximity
      const combinedHalf = newBox.hw + other.hw;
      const isOverlapping = (Math.abs(dx) < combinedHalf && Math.abs(dy) < combinedHalf);

      if (isOverlapping || dist < pushRadius) {
        // Calculate outward direction
        let nx = dx / dist;
        let ny = dy / dist;

        // If boxes were stacked right above/below, add slight horizontal jitter to break deadlocks
        if (Math.abs(nx) < 0.1) {
          nx = (Math.random() > 0.5 ? 0.35 : -0.35);
        }

        // 1. Immediate positional de-penetration push
        if (isOverlapping) {
          const overlapDist = combinedHalf - Math.max(Math.abs(dx), Math.abs(dy));
          const pushStep = Math.max(overlapDist, 6);
          other.x += nx * pushStep;
          other.y += ny * pushStep;
        }

        // 2. Dynamic velocity impulse
        const proximityFactor = Math.max(0.3, 1.0 - (dist / pushRadius));
        const impulse = (baseImpulse / Math.sqrt(other.mass)) * proximityFactor;

        other.vx += nx * impulse;
        other.vy += ny * impulse;

        // 3. Visual impact squash
        other.wobbleX = 0.75;
        other.wobbleVel = 4.0;
      }
    }
  }

  // Get current chamber fill density (0.0 to 1.0)
  getFillRatio() {
    let occupiedArea = 0;
    const totalArea = this.chamber.w * this.chamber.h;
    for (const b of this.bubbles) {
      if (!b.merging) {
        occupiedArea += (b.size * b.size);
      }
    }
    return Math.min(1.0, occupiedArea / totalArea);
  }

  // Check if any settled bubble is past danger line
  getDangerOverflowing() {
    for (const b of this.bubbles) {
      if (!b.merging && b.age > 0.5) {
        // If the bottom edge of the bubble dips past danger line
        if (b.y + b.hh > this.dangerY) {
          return true;
        }
      }
    }
    return false;
  }
}

if (typeof window !== 'undefined') {
  window.PhysicsEngine = PhysicsEngine;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PhysicsEngine;
}

"""
Monte-Carlo Simulation & Game Dynamics Analysis for A.I.r Bubbles: Temperature Ratios
Simulates thousands of full games across multiple ratios (Hot : Cold : Normal)
and evaluates dynamics across player skill archetypes.
"""

import random
import numpy as np

TIER_WEIGHTS = [45, 30, 17, 6, 2] # Tiers 1-5 spawn rates

def roll_tier():
    r = random.random() * 100
    if r < 45: return 1
    if r < 75: return 2
    if r < 92: return 3
    if r < 98: return 4
    return 5

def roll_temp(p_hot, p_cold):
    r = random.random()
    if r < p_hot:
        return 'hot'
    elif r < p_hot + p_cold:
        return 'cold'
    else:
        return 'normal'

class GameSimulator:
    def __init__(self, p_hot, p_cold, player_skill="competent", max_blocks=120):
        self.p_hot = p_hot
        self.p_cold = p_cold
        self.p_norm = round(1.0 - p_hot - p_cold, 2)
        self.player_skill = player_skill # 'novice', 'competent', 'expert'
        self.max_blocks = max_blocks
        
        self.pressure = 30.0
        self.blocks_used = 0
        self.peak_tier = 1
        self.merges = 0
        self.time_in_danger = 0 # steps where pressure >= 20
        self.total_steps = 0
        
        # Grid board model: 7 columns, stack height capacity 9
        self.cols = [[] for _ in range(7)]
        self.max_height = 8
        self.overflow = False
        self.overpressure = False
        self.defused = False

    def simulate(self):
        while not (self.defused or self.overpressure or self.overflow or self.blocks_used >= self.max_blocks):
            self.step()
        
        return {
            "defused": self.defused,
            "overpressure": self.overpressure,
            "overflow": self.overflow,
            "exhausted": not (self.defused or self.overpressure or self.overflow),
            "blocks_used": self.blocks_used,
            "peak_tier": self.peak_tier,
            "merges": self.merges,
            "tension_ratio": (self.time_in_danger / max(1, self.total_steps))
        }

    def step(self):
        tier = roll_tier()
        temp = roll_temp(self.p_hot, self.p_cold)
        self.blocks_used += 1
        self.total_steps += 1
        
        if self.pressure >= 20.0:
            self.time_in_danger += 1
            
        # Decision making on column placement
        target_col = self.choose_column(tier, temp)
        
        # Place block
        block = {"tier": tier, "temp": temp}
        self.cols[target_col].append(block)
        
        # Process merges in that column and adjacent columns
        self.resolve_merges(target_col)
        
        # Check stack heights
        if any(len(c) > self.max_height for c in self.cols):
            self.overflow = True
            return

        # Check pressure states
        if self.pressure <= 0.0:
            self.defused = True
        elif self.pressure >= 35.0:
            self.overpressure = True

    def choose_column(self, tier, temp):
        # Find best column based on player skill
        valid_cols = [i for i, c in enumerate(self.cols) if len(c) < self.max_height]
        if not valid_cols:
            return random.randint(0, 6)

        scored_cols = []
        for c in valid_cols:
            col = self.cols[c]
            score = 0
            if col:
                top = col[-1]
                if top["tier"] == tier:
                    # Potential merge!
                    t1, t2 = top["temp"], temp
                    if t1 == 'hot' and t2 == 'hot':
                        # Hot merge (+2 * tier)
                        if self.player_skill == "novice":
                            score += 10 # Novice just matches numbers
                        else:
                            # Competent/Expert avoids if pressure is dangerous
                            if self.pressure >= 28.0:
                                score -= 30
                            else:
                                score += 5
                    elif (t1 == 'cold' and t2 == 'cold') or ('cold' in (t1, t2) and 'normal' in (t1, t2)):
                        # Cold merge (lowers pressure)
                        score += 35 if self.player_skill != "novice" else 15
                    elif ('hot' in (t1, t2) and 'cold' in (t1, t2)):
                        # Neutralize
                        score += 20
                    else:
                        score += 10
                else:
                    # Non-matching tier: penalize burying lower/higher tiers
                    diff = abs(top["tier"] - tier)
                    score -= diff * 2
            
            # Penalize tall stacks
            score -= len(col) * 3
            scored_cols.append((score, c))
            
        scored_cols.sort(reverse=True)
        
        if self.player_skill == "novice":
            # 30% chance to pick random col
            if random.random() < 0.30:
                return random.choice(valid_cols)
        elif self.player_skill == "competent":
            # 10% sub-optimal pick
            if random.random() < 0.10 and len(scored_cols) > 1:
                return scored_cols[1][1]
                
        return scored_cols[0][1]

    def resolve_merges(self, col_idx):
        changed = True
        while changed:
            changed = False
            # 1. Vertical merge in same column
            col = self.cols[col_idx]
            if len(col) >= 2:
                b1 = col[-2]
                b2 = col[-1]
                if b1["tier"] == b2["tier"] and b1["tier"] < 12:
                    col.pop()
                    col.pop()
                    new_tier = b1["tier"] + 1
                    self.apply_pressure(b1, b2)
                    col.append({"tier": new_tier, "temp": "normal"})
                    self.merges += 1
                    self.peak_tier = max(self.peak_tier, new_tier)
                    changed = True
                    continue
            
            # 2. Side-by-side merge with adjacent columns
            for adj in [col_idx - 1, col_idx + 1]:
                if 0 <= adj < len(self.cols):
                    c1 = self.cols[col_idx]
                    c2 = self.cols[adj]
                    if c1 and c2:
                        top1 = c1[-1]
                        top2 = c2[-1]
                        if top1["tier"] == top2["tier"] and top1["tier"] < 12:
                            c1.pop()
                            c2.pop()
                            new_tier = top1["tier"] + 1
                            self.apply_pressure(top1, top2)
                            # Put resulting block in shorter column
                            dest = c1 if len(c1) <= len(c2) else c2
                            dest.append({"tier": new_tier, "temp": "normal"})
                            self.merges += 1
                            self.peak_tier = max(self.peak_tier, new_tier)
                            changed = True
                            break

    def apply_pressure(self, b1, b2):
        t1, t2 = b1["temp"], b2["temp"]
        tier = b1["tier"]
        delta = 0
        if t1 == 'hot' and t2 == 'hot':
            delta = 2 * tier
        elif (t1 == 'hot' and t2 == 'normal') or (t1 == 'normal' and t2 == 'hot'):
            delta = 1 * tier
        elif t1 == 'cold' and t2 == 'cold':
            delta = -2 * tier
        elif (t1 == 'cold' and t2 == 'normal') or (t1 == 'normal' and t2 == 'cold'):
            delta = -1 * tier
        
        self.pressure = max(0.0, self.pressure + delta)

def run_experiment(ratios, N=600):
    results = {}
    for name, (p_hot, p_cold) in ratios.items():
        results[name] = {}
        for skill in ["novice", "competent", "expert"]:
            wins, blowouts, overflows = 0, 0, 0
            blocks_list, peak_tiers, tension_list = [], [], []
            
            for _ in range(N):
                sim = GameSimulator(p_hot, p_cold, player_skill=skill)
                r = sim.simulate()
                if r["defused"]: wins += 1
                elif r["overpressure"]: blowouts += 1
                elif r["overflow"]: overflows += 1
                blocks_list.append(r["blocks_used"])
                peak_tiers.append(r["peak_tier"])
                tension_list.append(r["tension_ratio"])
                
            results[name][skill] = {
                "win_rate": round(wins / N * 100, 1),
                "blowout_rate": round(blowouts / N * 100, 1),
                "overflow_rate": round(overflows / N * 100, 1),
                "avg_blocks": round(np.mean(blocks_list), 1),
                "avg_peak_tier": round(np.mean(peak_tiers), 1),
                "avg_tension": round(np.mean(tension_list) * 100, 1)
            }
    return results

if __name__ == "__main__":
    test_ratios = {
        "2:4:4 (Current)": (0.20, 0.40),
        "1:5:4 (Gentle)": (0.10, 0.50),
        "1.5:4.5:4 (Chill)": (0.15, 0.45),
        "2:5:3 (Focused)": (0.20, 0.50),
        "2:6:2 (Cool Heavy)": (0.20, 0.60),
        "2:7:1 (Previous)": (0.20, 0.70),
        "2.5:4.5:3 (Brisk)": (0.25, 0.45),
        "3:4:3 (Tense)": (0.30, 0.40),
        "3:5:2 (Dynamic)": (0.30, 0.50),
        "3.5:4.5:2 (Hardcore)": (0.35, 0.45),
        "4:4:2 (Symmetric)": (0.40, 0.40),
        "5:4:1 (Meltdown)": (0.50, 0.40),
    }
    
    print("Running 21,600 simulated games across 12 ratio profiles...")
    data = run_experiment(test_ratios, N=600)
    
    import json
    with open("/Users/georgearmah/air-bubble/scratch/ratio_results.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Experiments completed and saved to scratch/ratio_results.json")

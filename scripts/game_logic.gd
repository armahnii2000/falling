extends RefCounted
## Pure spawn/score/threshold/state math mirroring game.gd constants.
## Scene-free so headless unit tests can call it (rules 1-3, 8-10, 20-24).

const HOT_PROB := 0.20
const COLD_PROB := 0.25
const COOLDOWN_DURATION := 0.18
const COMBO_WINDOW := 0.95
const TEMP_WARN := 20.0
const TEMP_BURST := 30.0
const DANGER_Y := 80.0
const DANGER_AGE := 0.6
const DANGER_VEL := 70.0
const DANGER_LIMIT := 3.0

static func spawn_tier_for(r: float) -> int:
	if r < 0.45: return 1
	if r < 0.75: return 2
	if r < 0.92: return 3
	if r < 0.98: return 4
	return 5

static func temp_type_for(r: float) -> String:
	if r < HOT_PROB: return "hot"
	if r < HOT_PROB + COLD_PROB: return "cold"
	return "normal"

static func combo_count_for(elapsed: float, prev_combo: int = 1) -> int:
	return prev_combo + 1 if elapsed < COMBO_WINDOW else 1

static func temp_state(temp: float) -> String:
	if temp >= TEMP_BURST: return "burst"
	if temp >= TEMP_WARN: return "warning"
	return "stable"

static func should_overheat(temp: float) -> bool:
	return temp >= TEMP_BURST

static func is_breach(y: float, r: float, age: float, speed: float) -> bool:
	return age > DANGER_AGE and speed < DANGER_VEL and y + r > DANGER_Y

static func is_apex(next_tier: int) -> bool:
	return next_tier == 11

static func highest_after(cur_max: int, tier: int) -> int:
	return maxi(cur_max, tier)

static func initial_state() -> Dictionary:
	return {"temperature": 0.0, "overheat": false, "game_over": false, "paused": false, "time": 0.0}

static func tick_time(t: float, delta: float, paused: bool, game_over: bool) -> float:
	return t if (paused or game_over) else t + delta

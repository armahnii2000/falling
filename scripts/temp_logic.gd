extends RefCounted
## Pure temperature / merge math for A.I.r Bubbles (rules 11-19).
## Kept free of scene state so headless unit tests can call it.

# Returns temp gauge delta for a merge of two equal-tier bubbles.
# t1/t2 are "hot", "cold" or "normal". tier is the PARENT tier (e.g. 4 for 4+4).
static func temp_delta(t1: String, t2: String, tier: int) -> int:
	var has_hot := t1 == "hot" or t2 == "hot"
	var has_cold := t1 == "cold" or t2 == "cold"
	if has_hot and has_cold:
		return 0
	if t1 == "hot" and t2 == "hot":
		return tier * 2
	if has_hot:
		return tier
	if t1 == "cold" and t2 == "cold":
		return -tier * 2
	if has_cold:
		return -tier
	return 0


# Children always come out normal (single-use heat/cold, heat vents).
static func child_temp(_t1: String, _t2: String) -> String:
	return "normal"


# Apply delta with floor at 0 (rule 17).
static func apply_temp(current: float, delta: int) -> float:
	return maxf(0.0, current + float(delta))


# Merge eligibility (rules 4-5): equal tiers, both below 11.
static func can_merge(tier_a: int, tier_b: int) -> bool:
	return tier_a > 0 and tier_a < 11 and tier_a == tier_b


# Score for making tier `next_tier` at combo count (rule 8).
static func merge_score(next_tier: int, combo: int) -> int:
	return next_tier * combo

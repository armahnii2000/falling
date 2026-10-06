extends SceneTree
## Merge UTs for A.I.r Bubbles (GAME_RULES.md rules 4-5, 8, 11-19).
## Run: godot --headless --path . -s res://tests/test_merge.gd

const TL := preload("res://scripts/temp_logic.gd")

var _fails := 0
var _passes := 0


func _check(name: String, got, want) -> void:
	if got == want:
		_passes += 1
	else:
		_fails += 1
		printerr("FAIL %s: got %s want %s" % [name, str(got), str(want)])


func _initialize() -> void:
	# Rules 11-14: hot doubles, cold doubles, singles.
	_check("11 H4+H4=+8", TL.temp_delta("hot", "hot", 4), 8)
	_check("11 H1+H1=+2", TL.temp_delta("hot", "hot", 1), 2)
	_check("12 H4+N4=+4", TL.temp_delta("hot", "normal", 4), 4)
	_check("12 N4+H4=+4", TL.temp_delta("normal", "hot", 4), 4)
	_check("13 C4+C4=-8", TL.temp_delta("cold", "cold", 4), -8)
	_check("14 C4+N4=-4", TL.temp_delta("cold", "normal", 4), -4)
	_check("14 N4+C4=-4", TL.temp_delta("normal", "cold", 4), -4)
	# Rule 15: hot+cold neutral (either order).
	_check("15 H1+C1=0", TL.temp_delta("hot", "cold", 1), 0)
	_check("15 C1+H1=0", TL.temp_delta("cold", "hot", 1), 0)
	_check("15 H5+C5=0", TL.temp_delta("hot", "cold", 5), 0)
	# Rule 16: normals neutral.
	_check("16 N3+N3=0", TL.temp_delta("normal", "normal", 3), 0)
	# Rule 17: floor at 0.
	_check("17 floor 2-10=0", TL.apply_temp(2.0, -10), 0.0)
	_check("17 floor 0-8=0", TL.apply_temp(0.0, -8), 0.0)
	_check("17 add 20+8=28", TL.apply_temp(20.0, 8), 28.0)
	# Children always normal (rules 11-16).
	_check("child H+H", TL.child_temp("hot", "hot"), "normal")
	_check("child C+C", TL.child_temp("cold", "cold"), "normal")
	_check("child H+C", TL.child_temp("hot", "cold"), "normal")
	_check("child N+N", TL.child_temp("normal", "normal"), "normal")
	# Rules 4-5: merge eligibility.
	_check("4 4+4 merges", TL.can_merge(4, 4), true)
	_check("4 2+3 no", TL.can_merge(2, 3), false)
	_check("5 11+11 no", TL.can_merge(11, 11), false)
	_check("5 10+10 yes", TL.can_merge(10, 10), true)
	# Rule 8: score = size x combo.
	_check("8 size5 combo1", TL.merge_score(5, 1), 5)
	_check("8 size5 combo2", TL.merge_score(5, 2), 10)
	_check("8 size11 combo1", TL.merge_score(11, 1), 11)
	# Rule 19 reference rows.
	_check("19 H4+H4", TL.temp_delta("hot", "hot", 4), 8)
	_check("19 C4+C4", TL.temp_delta("cold", "cold", 4), -8)
	_check("19 H1+C1", TL.temp_delta("hot", "cold", 1), 0)

	print("test_merge: %d passed, %d failed" % [_passes, _fails])
	quit(1 if _fails > 0 else 0)

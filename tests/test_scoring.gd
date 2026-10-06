extends SceneTree
## Scoring UTs (rules 8-10). Run: godot --headless --path . -s res://tests/test_scoring.gd
const TL := preload("res://scripts/temp_logic.gd")
const GL := preload("res://scripts/game_logic.gd")
var _p := 0
var _f := 0
func _check(n: String, got, want) -> void:
	if got == want: _p += 1
	else: _f += 1; printerr("FAIL %s: got %s want %s" % [n, str(got), str(want)])
func _initialize() -> void:
	_check("8 2x1=2", TL.merge_score(2, 1), 2)
	_check("8 5x2=10", TL.merge_score(5, 2), 10)
	_check("8 11x1=11", TL.merge_score(11, 1), 11)
	_check("8 11x3=33", TL.merge_score(11, 3), 33)
	_check("9 window", GL.COMBO_WINDOW, 0.95)
	_check("9 chain", GL.combo_count_for(0.5, 1), 2)
	_check("9 chain3", GL.combo_count_for(0.94, 2), 3)
	_check("9 edge resets", GL.combo_count_for(0.95, 2), 1)
	_check("9 expired", GL.combo_count_for(1.2, 3), 1)
	_check("9 zero", GL.combo_count_for(0.0, 1), 2)
	_check("10 max up", GL.highest_after(3, 5), 5)
	_check("10 max hold", GL.highest_after(7, 4), 7)
	_check("10 apex trig", GL.is_apex(11), true)
	_check("10 no apex10", GL.is_apex(10), false)
	_check("10 no apex5", GL.is_apex(5), false)
	_check("10 pts apex", TL.merge_score(11, 1), 11)
	print("test_scoring: %d passed, %d failed" % [_p, _f])
	quit(1 if _f > 0 else 0)

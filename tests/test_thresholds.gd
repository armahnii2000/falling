extends SceneTree
## Threshold UTs (rules 20-22). Run: godot --headless --path . -s res://tests/test_thresholds.gd
const GL := preload("res://scripts/game_logic.gd")
var _p := 0
var _f := 0
func _check(n: String, got, want) -> void:
	if got == want: _p += 1
	else: _f += 1; printerr("FAIL %s: got %s want %s" % [n, str(got), str(want)])
func _initialize() -> void:
	_check("20 warn const", GL.TEMP_WARN, 20.0)
	_check("20 burst const", GL.TEMP_BURST, 30.0)
	_check("20 stable", GL.temp_state(0.0), "stable")
	_check("20 stable19", GL.temp_state(19.9), "stable")
	_check("20 warning", GL.temp_state(20.0), "warning")
	_check("20 warn29", GL.temp_state(29.9), "warning")
	_check("20 burst", GL.temp_state(30.0), "burst")
	_check("21 no burst", GL.should_overheat(29.9), false)
	_check("21 burst", GL.should_overheat(30.0), true)
	_check("21 big", GL.should_overheat(45.0), true)
	_check("22 const Y", GL.DANGER_Y, 80.0)
	_check("22 limit", GL.DANGER_LIMIT, 3.0)
	_check("22 breach", GL.is_breach(70.0, 18.0, 1.0, 10.0), true)
	_check("22 young", GL.is_breach(70.0, 18.0, 0.5, 10.0), false)
	_check("22 fast", GL.is_breach(70.0, 18.0, 1.0, 80.0), false)
	_check("22 above", GL.is_breach(0.0, 18.0, 1.0, 10.0), false)
	_check("22 age edge", GL.is_breach(70.0, 18.0, 0.6, 10.0), false)
	print("test_thresholds: %d passed, %d failed" % [_p, _f])
	quit(1 if _f > 0 else 0)

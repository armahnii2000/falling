extends SceneTree
## State UTs (rules 23-24; scene-coupled parts noted). Run: godot --headless --path . -s res://tests/test_state.gd
const GL := preload("res://scripts/game_logic.gd")
var _p := 0
var _f := 0
func _check(n: String, got, want) -> void:
	if got == want: _p += 1
	else: _f += 1; printerr("FAIL %s: got %s want %s" % [n, str(got), str(want)])
func _initialize() -> void:
	var s := GL.initial_state()
	_check("23 temp 0", s["temperature"], 0.0)
	_check("23 overheat false", s["overheat"], false)
	_check("23 game_over false", s["game_over"], false)
	_check("23 paused false", s["paused"], false)
	_check("23 time 0", s["time"], 0.0)
	var r := GL.initial_state() # restart = fresh state (R reloads scene)
	_check("23 restart temp", r["temperature"], 0.0)
	_check("23 restart overheat", r["overheat"], false)
	_check("24 run advances", GL.tick_time(1.0, 0.5, false, false), 1.5)
	_check("24 paused frozen", GL.tick_time(1.0, 0.5, true, false), 1.0)
	_check("24 over frozen", GL.tick_time(1.0, 0.5, false, true), 1.0)
	_check("24 both frozen", GL.tick_time(2.0, 0.1, true, true), 2.0)
	# Manual (scene-coupled, verify by play): P toggles tree.paused + pause_label;
	# merges/danger/time frozen via game_over/paused guards; merges blocked while paused.
	print("test_state: %d passed, %d failed" % [_p, _f])
	quit(1 if _f > 0 else 0)

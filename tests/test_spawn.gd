extends SceneTree
## Spawn UTs (rules 1-3). Run: godot --headless --path . -s res://tests/test_spawn.gd
const GL := preload("res://scripts/game_logic.gd")
var _p := 0
var _f := 0
func _check(n: String, got, want) -> void:
	if got == want: _p += 1
	else: _f += 1; printerr("FAIL %s: got %s want %s" % [n, str(got), str(want)])
func _initialize() -> void:
	_check("t1 lo", GL.spawn_tier_for(0.0), 1)
	_check("t1 hi", GL.spawn_tier_for(0.449), 1)
	_check("t2 lo", GL.spawn_tier_for(0.45), 2)
	_check("t2 hi", GL.spawn_tier_for(0.749), 2)
	_check("t3 lo", GL.spawn_tier_for(0.75), 3)
	_check("t3 hi", GL.spawn_tier_for(0.919), 3)
	_check("t4 lo", GL.spawn_tier_for(0.92), 4)
	_check("t4 hi", GL.spawn_tier_for(0.979), 4)
	_check("t5 lo", GL.spawn_tier_for(0.98), 5)
	_check("t5 hi", GL.spawn_tier_for(0.999), 5)
	_check("never 6+", GL.spawn_tier_for(0.9999) < 6, true)
	_check("hot lo", GL.temp_type_for(0.0), "hot")
	_check("hot hi", GL.temp_type_for(0.199), "hot")
	_check("cold lo", GL.temp_type_for(0.20), "cold")
	_check("cold hi", GL.temp_type_for(0.449), "cold")
	_check("norm lo", GL.temp_type_for(0.45), "normal")
	_check("cooldown", GL.COOLDOWN_DURATION, 0.18)
	_check("hot prob", GL.HOT_PROB, 0.20)
	_check("cold prob", GL.COLD_PROB, 0.25)
	seed(12345)
	var c := [0, 0, 0, 0, 0, 0]
	for i in 10000: c[GL.spawn_tier_for(randf())] += 1
	_check("stat t1 ~45%", absf(float(c[1]) / 10000.0 - 0.45) < 0.03, true)
	_check("stat t2 ~30%", absf(float(c[2]) / 10000.0 - 0.30) < 0.03, true)
	_check("stat t5 ~2%", absf(float(c[5]) / 10000.0 - 0.02) < 0.015, true)
	print("test_spawn: %d passed, %d failed" % [_p, _f])
	quit(1 if _f > 0 else 0)

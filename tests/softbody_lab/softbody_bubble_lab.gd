extends Node2D
## Softbody bubble feel lab — all 11 tiers baked with per-tier density mapping.
## Standalone Godot: godot --path . res://tests/softbody_lab/softbody_bubble_lab.tscn
## Click = poke impulse (nearest bodies). R = rebake all.
## Density map: tiers 1-4 fine (10), tiers 5-8 medium (16), tiers 9-11 coarse (24).
## Zero gravity: bubbles hang mid-water so poke squish reads purely.

const SB := preload("res://addons/softbody2d/softbody2d.gd")

const TIER_RADII := [18.0, 24.0, 31.0, 39.0, 48.0, 58.0, 69.0, 81.0, 94.0, 108.0, 124.0]
const DENSITY_FINE := 10.0
const DENSITY_MEDIUM := 16.0
const DENSITY_COARSE := 24.0
var bubbles: Array = []
var time := 0.0


func density_for_tier(t: int) -> float:
	if t <= 4:
		return DENSITY_FINE
	if t <= 8:
		return DENSITY_MEDIUM
	return DENSITY_COARSE


func _ready() -> void:
	var cam := Camera2D.new()
	cam.position = Vector2.ZERO
	cam.zoom = Vector2(0.5, 0.5)
	add_child(cam)
	cam.make_current()
	_build_chamber()
	_bake_all()


func _build_chamber() -> void:
	var stat := StaticBody2D.new()
	stat.name = "Chamber"
	add_child(stat)
	_add_box(stat, Vector2(0, -560), Vector2(1500, 40))   # ceiling
	_add_box(stat, Vector2(-720, 0), Vector2(40, 1200))   # left wall
	_add_box(stat, Vector2(720, 0), Vector2(40, 1200))    # right wall
	_add_box(stat, Vector2(0, 560), Vector2(1500, 40))    # floor safety


func _add_box(parent: Node, pos: Vector2, size: Vector2) -> void:
	var col := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = size
	col.shape = rect
	col.position = pos
	parent.add_child(col)


func _bubble_texture(r: float) -> Texture2D:
	var px := int(r * 2.0) + 16
	var img := Image.create_empty(px, px, false, Image.FORMAT_RGBA8)
	var c := Vector2(px, px) * 0.5
	for y in px:
		for x in px:
			var d := Vector2(x, y).distance_to(c)
			var a := clampf(1.0 - (d - r) / 8.0, 0.0, 1.0)
			img.set_pixel(x, y, Color(0.35, 0.8, 1.0, a))
	return ImageTexture.create_from_image(img)


func _tier_pos(i: int) -> Vector2:
	var col := i % 4
	var row := i / 4
	return Vector2((col - 1.5) * 320.0, (row - 1.0) * 330.0)


func _bake_all() -> void:
	for b in bubbles:
		if is_instance_valid(b):
			b.queue_free()
	bubbles.clear()
	for i in TIER_RADII.size():
		var t := i + 1
		var sb = SB.new()
		sb.texture = _bubble_texture(TIER_RADII[i])
		sb.vertex_interval = density_for_tier(t)
		sb.gravity_scale = 0.0
		sb.linear_damp = 2.4
		sb.position = _tier_pos(i)
		sb.set_meta("tier", t)
		add_child(sb)
		sb.create_softbody2d(true)
		bubbles.append(sb)


func _process(delta: float) -> void:
	time += delta
	queue_redraw()


func _draw() -> void:
	var font := ThemeDB.fallback_font
	if font == null:
		return
	draw_string(font, Vector2(-1080, -660), "SOFTBODY TIER LAB — click a bubble to poke, R rebakes all", HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color(0.7, 0.9, 1.0))
	draw_string(font, Vector2(-1080, -620), "tiers 1-4 FINE (10)  |  tiers 5-8 MEDIUM (16)  |  tiers 9-11 COARSE (24)", HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(1.0, 0.88, 0.4))
	var y := -580.0
	for i in TIER_RADII.size():
		var t := i + 1
		var n := 0
		if i < bubbles.size() and is_instance_valid(bubbles[i]):
			n = bubbles[i].find_children("*", "RigidBody2D", true, false).size()
		if i % 4 == 0 and i > 0:
			y += 0.0
		draw_string(font, Vector2(-1080 + (i % 4) * 300.0, y + (i / 4) * 34.0), "T%d r=%.0f bodies=%d" % [t, TIER_RADII[i], n], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(0.6, 0.85, 1.0))


func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_poke(get_global_mouse_position())
	elif event is InputEventKey and event.pressed:
		match event.keycode:
			82: _bake_all()   # R


func _poke(p: Vector2) -> void:
	for sb in bubbles:
		if not is_instance_valid(sb):
			continue
		for b in sb.find_children("*", "RigidBody2D", true, false):
			var rb := b as RigidBody2D
			var d: Vector2 = rb.global_position - p
			var dist := d.length()
			if dist < 170.0 and dist > 0.01:
				rb.apply_central_impulse(d.normalized() * (170.0 - dist) * 2.0)

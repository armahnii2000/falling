extends Node2D
##
## Squishiness Lab — Standalone Interactive Bubble Deform & Juice Sandbox
##
## Controls:
##   Mouse Left Click & Drag : Grab and fling any bubble to slam into walls/bubbles
##   Mouse Right Click       : Poke bubble with instant shock impulse
##   1 - 5                   : Spawn bubbles of Tier 1 through 5 at mouse position
##   B                       : Spawn a massive Tier 10 / 11 Apex Titan bubble
##   G                       : Cycle gravity mode (Inverted Buoyancy / Downward / Zero-G)
##   [ / ]                   : Adjust Spring Stiffness (Softer Jell-O <-> Stiffer Rubber)
##   - / =                   : Adjust Spring Damping (Bouncier wobble <-> Quick settle)
##   C                       : Clear all bubbles
##   R                       : Reset to default cluster
##

const TIERS := {
	1: {"radius": 22.0, "color": Color(0.24, 0.78, 1.00), "name": "1"},
	2: {"radius": 30.0, "color": Color(0.28, 0.90, 0.45), "name": "2"},
	3: {"radius": 39.0, "color": Color(1.00, 0.88, 0.18), "name": "3"},
	4: {"radius": 49.0, "color": Color(1.00, 0.54, 0.16), "name": "4"},
	5: {"radius": 60.0, "color": Color(1.00, 0.22, 0.52), "name": "5"},
	6: {"radius": 72.0, "color": Color(0.68, 0.28, 1.00), "name": "6"},
	7: {"radius": 84.0, "color": Color(0.88, 0.20, 0.88), "name": "7"},
	8: {"radius": 96.0, "color": Color(0.96, 0.20, 0.25), "name": "8"},
	9: {"radius": 108.0, "color": Color(1.00, 0.75, 0.10), "name": "9"},
	10: {"radius": 120.0, "color": Color(0.10, 0.84, 0.65), "name": "10"},
	11: {"radius": 136.0, "color": Color(0.98, 0.92, 0.60), "name": "11 (APEX)"}
}

# Chamber boundaries (centered around Vector2.ZERO)
const BOX_W := 860.0
const BOX_H := 620.0

# Tunable Harmonic Spring Parameters
var stiffness := 220.0       # Spring return speed (Hooke's constant)
var damping := 14.0          # How fast oscillations die out
var squish_sensitivity := 0.0022  # How much collision impulse converts to squish

# Gravity Modes: 0 = Inverted (Upward), 1 = Downward, 2 = Zero-G
var gravity_mode := 0
var gravity_names := ["INVERTED BUOYANCY (Float Up)", "STANDARD (Fall Down)", "ZERO-G (Floating)"]
var current_gravity := Vector2(0.0, -420.0)

# Scene nodes & physics
var physics_root: Node2D
var walls_body: StaticBody2D
var bubbles: Array[RigidBody2D] = []

# Interactive Drag / Fling State
var dragged_body: RigidBody2D = null
var drag_offset := Vector2.ZERO
var prev_mouse_pos := Vector2.ZERO
var mouse_velocity := Vector2.ZERO

var time := 0.0


func _ready() -> void:
	randomize()
	_setup_camera()
	_setup_physics_chamber()
	_spawn_default_cluster()


func _setup_camera() -> void:
	var cam := Camera2D.new()
	cam.position = Vector2.ZERO
	cam.zoom = Vector2(0.95, 0.95)
	add_child(cam)
	cam.make_current()


func _setup_physics_chamber() -> void:
	physics_root = Node2D.new()
	physics_root.name = "PhysicsRoot"
	add_child(physics_root)

	walls_body = StaticBody2D.new()
	walls_body.name = "ChamberWalls"
	physics_root.add_child(walls_body)

	var half_w := BOX_W * 0.5
	var half_h := BOX_H * 0.5
	var thick := 50.0

	# Top (Ceiling)
	_add_wall_box(walls_body, Vector2(0.0, -half_h - thick * 0.5), Vector2(BOX_W + thick * 2.0, thick))
	# Bottom (Floor)
	_add_wall_box(walls_body, Vector2(0.0, half_h + thick * 0.5), Vector2(BOX_W + thick * 2.0, thick))
	# Left Wall
	_add_wall_box(walls_body, Vector2(-half_w - thick * 0.5, 0.0), Vector2(thick, BOX_H + thick * 2.0))
	# Right Wall
	_add_wall_box(walls_body, Vector2(half_w + thick * 0.5, 0.0), Vector2(thick, BOX_H + thick * 2.0))


func _add_wall_box(parent: StaticBody2D, pos: Vector2, size: Vector2) -> void:
	var col := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = size
	col.shape = rect
	col.position = pos
	parent.add_child(col)


func _create_bubble(pos: Vector2, tier: int, initial_vel := Vector2.ZERO) -> RigidBody2D:
	var info: Dictionary = TIERS[tier]
	var r: float = info["radius"]
	var col_tint: Color = info["color"]

	var body := RigidBody2D.new()
	body.position = pos
	body.linear_velocity = initial_vel
	body.gravity_scale = 0.0 # We apply custom buoyancy vector in integrate_forces
	body.linear_damp = 1.2
	body.angular_damp = 3.0
	body.contact_monitor = true
	body.max_contacts_reported = 8

	var phys_mat := PhysicsMaterial.new()
	phys_mat.bounce = 0.45
	phys_mat.friction = 0.25
	body.physics_material_override = phys_mat

	var col := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = r
	col.shape = circle
	body.add_child(col)

	# Deformation state metadata
	body.set_meta("tier", tier)
	body.set_meta("radius", r)
	body.set_meta("color", col_tint)
	body.set_meta("squash_axis", Vector2.UP)
	body.set_meta("squash_val", 1.0)
	body.set_meta("squash_vel", 0.0)
	body.set_meta("wobble_phase", randf_range(0.0, TAU))

	body.body_entered.connect(_on_bubble_collision.bind(body))

	physics_root.add_child(body)
	bubbles.append(body)
	return body


func _on_bubble_collision(other: Node, self_body: RigidBody2D) -> void:
	if not is_instance_valid(self_body) or not is_instance_valid(other):
		return

	var v_other := Vector2.ZERO
	var normal := Vector2.UP

	if other is RigidBody2D:
		var other_body := other as RigidBody2D
		v_other = other_body.linear_velocity
		normal = (self_body.global_position - other_body.global_position).normalized()
	elif other is StaticBody2D:
		# Collision against chamber walls: determine normal from wall boundary
		var p := self_body.global_position
		var half_w := BOX_W * 0.5
		var half_h := BOX_H * 0.5
		if p.x > half_w - 60.0:
			normal = Vector2.LEFT
		elif p.x < -half_w + 60.0:
			normal = Vector2.RIGHT
		elif p.y > half_h - 60.0:
			normal = Vector2.UP
		elif p.y < -half_h + 60.0:
			normal = Vector2.DOWN

	if normal.length_squared() < 0.01:
		normal = Vector2.UP

	var rel_vel := self_body.linear_velocity - v_other
	var impact := rel_vel.dot(-normal)

	if impact > 25.0:
		# Calculate dynamic compression based on impact speed
		var kick := clampf(impact * squish_sensitivity, 0.08, 0.65)
		self_body.set_meta("squash_axis", normal)
		# Negative squash_vel drives compression along impact axis
		var curr_vel: float = self_body.get_meta("squash_vel", 0.0)
		self_body.set_meta("squash_vel", curr_vel - kick * 28.0)


func _spawn_default_cluster() -> void:
	_clear_bubbles()
	# Spawn a nice test cluster with various sizes
	_create_bubble(Vector2(-180.0, 100.0), 2, Vector2(60.0, -180.0))
	_create_bubble(Vector2(-60.0, 140.0), 3, Vector2(-40.0, -220.0))
	_create_bubble(Vector2(80.0, 110.0), 4, Vector2(20.0, -150.0))
	_create_bubble(Vector2(200.0, 120.0), 1, Vector2(-80.0, -240.0))
	_create_bubble(Vector2(0.0, -120.0), 6, Vector2(0.0, 30.0))
	_create_bubble(Vector2(-240.0, -140.0), 5, Vector2(50.0, 0.0))


func _clear_bubbles() -> void:
	dragged_body = null
	for b in bubbles:
		if is_instance_valid(b):
			b.queue_free()
	bubbles.clear()


func _physics_process(delta: float) -> void:
	# Compute mouse velocity for flinging
	var mpos := get_global_mouse_position()
	mouse_velocity = (mpos - prev_mouse_pos) / maxf(delta, 0.001)
	prev_mouse_pos = mpos

	# Gravity / buoyancy force
	match gravity_mode:
		0: current_gravity = Vector2(0.0, -420.0) # Inverted
		1: current_gravity = Vector2(0.0, 480.0)  # Downward
		2: current_gravity = Vector2.ZERO         # Zero-G

	# Update physics and harmonic spring oscillators for all bubbles
	for b in bubbles:
		if not is_instance_valid(b):
			continue

		# Apply buoyancy
		b.apply_central_force(current_gravity * b.mass)

		# Drag handling
		if b == dragged_body:
			var target_pos := mpos + drag_offset
			var drag_force := (target_pos - b.global_position) * 35.0
			b.linear_velocity = drag_force
			continue

		# Harmonic Spring Math (Hooke's Law + Viscous Damping)
		var s_val: float = b.get_meta("squash_val", 1.0)
		var s_vel: float = b.get_meta("squash_vel", 0.0)

		var displacement := s_val - 1.0
		var spring_accel := -stiffness * displacement - damping * s_vel

		s_vel += spring_accel * delta
		s_val += s_vel * delta

		# Clamp extreme deformation for stability
		s_val = clampf(s_val, 0.40, 1.75)

		b.set_meta("squash_val", s_val)
		b.set_meta("squash_vel", s_vel)

		# Dynamic buoyant swimming wobble
		var wp: float = b.get_meta("wobble_phase", 0.0) + delta * 4.5
		b.set_meta("wobble_phase", wp)


func _process(delta: float) -> void:
	time += delta
	_handle_input()
	queue_redraw()


func _handle_input() -> void:
	var mpos := get_global_mouse_position()

	# Grab with mouse left click
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		if dragged_body == null:
			var clicked := _find_bubble_at(mpos)
			if clicked != null:
				dragged_body = clicked
				drag_offset = clicked.global_position - mpos
	else:
		if dragged_body != null:
			# Fling release with mouse velocity
			dragged_body.linear_velocity = mouse_velocity.limit_length(950.0)
			# Small squish on fling
			dragged_body.set_meta("squash_axis", mouse_velocity.normalized())
			dragged_body.set_meta("squash_vel", -0.4 * 25.0)
			dragged_body = null

	# Right-click poke
	if Input.is_action_just_pressed("ui_cancel") or Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		var poked := _find_bubble_at(mpos)
		if poked != null:
			poked.set_meta("squash_axis", Vector2.UP)
			poked.set_meta("squash_vel", -0.65 * 30.0)
			poked.apply_central_impulse(Vector2(randf_range(-180.0, 180.0), -260.0))

	# Number keys 1-5: Spawn at mouse
	for key_idx in range(KEY_1, KEY_6):
		if Input.is_physical_key_pressed(key_idx) and not _key_held(key_idx):
			var tier := key_idx - KEY_1 + 1
			_create_bubble(mpos, tier, Vector2(randf_range(-30.0, 30.0), -50.0))

	# 'B' Key: Spawn Apex Titan
	if Input.is_key_pressed(KEY_B) and not _key_held(KEY_B):
		_create_bubble(mpos, 10, Vector2.ZERO)

	# 'G' Key: Cycle Gravity
	if Input.is_key_pressed(KEY_G) and not _key_held(KEY_G):
		gravity_mode = (gravity_mode + 1) % 3

	# '[' / ']' : Stiffness
	if Input.is_key_pressed(KEY_BRACKETLEFT):
		stiffness = maxf(60.0, stiffness - 60.0 * get_process_delta_time())
	if Input.is_key_pressed(KEY_BRACKETRIGHT):
		stiffness = minf(600.0, stiffness + 60.0 * get_process_delta_time())

	# '-' / '=' : Damping
	if Input.is_key_pressed(KEY_MINUS):
		damping = maxf(4.0, damping - 8.0 * get_process_delta_time())
	if Input.is_key_pressed(KEY_EQUAL):
		damping = minf(35.0, damping + 8.0 * get_process_delta_time())

	# 'C' : Clear
	if Input.is_key_pressed(KEY_C) and not _key_held(KEY_C):
		_clear_bubbles()

	# 'R' : Reset
	if Input.is_key_pressed(KEY_R) and not _key_held(KEY_R):
		_spawn_default_cluster()


var _keys_state := {}
func _key_held(k: int) -> bool:
	var pressed := Input.is_physical_key_pressed(k)
	var was := bool(_keys_state.get(k, false))
	_keys_state[k] = pressed
	return was


func _find_bubble_at(pos: Vector2) -> RigidBody2D:
	for b in bubbles:
		if is_instance_valid(b):
			var r: float = b.get_meta("radius", 20.0)
			if b.global_position.distance_to(pos) <= r * 1.1:
				return b
	return null


# --- Rendering: Juicy Deformed 3D Shaded Bubbles ----------------------------

func _draw() -> void:
	_draw_background()
	_draw_chamber()
	_draw_bubbles()
	_draw_hud()


func _draw_background() -> void:
	# Deep underwater gradient backdrop
	var r := Rect2(-BOX_W * 0.7, -BOX_H * 0.7, BOX_W * 1.4, BOX_H * 1.4)
	draw_rect(r, Color(0.04, 0.12, 0.26))


func _draw_chamber() -> void:
	var r := Rect2(-BOX_W * 0.5, -BOX_H * 0.5, BOX_W, BOX_H)
	# Water column tint
	draw_rect(r, Color(0.03, 0.20, 0.45, 0.40))
	# Glowing outer border
	draw_rect(r, Color(0.55, 0.88, 1.0, 0.60), false, 3.0)

	# Surface ripple at ceiling
	var pts := PackedVector2Array()
	var segs := 32
	var top_y := -BOX_H * 0.5
	for i in range(segs + 1):
		var t := float(i) / float(segs)
		var x := -BOX_W * 0.5 + BOX_W * t
		pts.append(Vector2(x, top_y + sin(t * TAU * 3.0 + time * 2.0) * 4.0))
	draw_polyline(pts, Color(0.85, 0.98, 1.0, 0.85), 3.0)


func _draw_bubbles() -> void:
	for b in bubbles:
		if not is_instance_valid(b):
			continue

		var pos := b.global_position
		var tier: int = b.get_meta("tier", 1)
		var r: float = b.get_meta("radius", 20.0)
		var tint: Color = b.get_meta("color", Color.WHITE)

		# Viscoelastic deformation vectors
		var s_axis: Vector2 = b.get_meta("squash_axis", Vector2.UP).normalized()
		var s_val: float = b.get_meta("squash_val", 1.0)
		var wp: float = b.get_meta("wobble_phase", 0.0)

		# Add natural buoyant breathing wave
		var wave := sin(wp) * 0.03
		s_val += wave

		# Volume preservation in 2D: scale along normal = s_val, perpendicular = 1.0 / s_val
		var scale_axis := s_val
		var scale_perp := 1.0 / maxf(0.25, s_val)

		# 1. Transform canvas: rotate to match squash impact direction, then apply ellipse scale
		var rot := s_axis.angle()
		draw_set_transform(pos, rot, Vector2(scale_axis, scale_perp))
		_draw_glassy_sphere(r, tint)

		# 2. Draw number upright (un-rotated) centered on bubble
		draw_set_transform(pos, 0.0, Vector2.ONE)
		_draw_bubble_number(r, tier)

	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_glassy_sphere(radius: float, tint: Color) -> void:
	# 1. Soft atmospheric outer glow
	draw_circle(Vector2.ZERO, radius * 1.45, Color(tint.r, tint.g, tint.b, 0.12))
	# 2. Darkened base sphere for rich 3D sphere shading
	draw_circle(Vector2.ZERO, radius, tint.darkened(0.40))
	# 3. Vibrant main color body
	draw_circle(Vector2.ZERO, radius * 0.92, tint)
	# 4. Soft internal specular crescent
	draw_circle(Vector2(-radius * 0.28, -radius * 0.30), radius * 0.35, tint.lightened(0.55))
	# 5. Bright highlight dot
	draw_circle(Vector2(-radius * 0.28, -radius * 0.30), radius * 0.16, Color(1.0, 1.0, 1.0, 0.92))
	# 6. Glass rim contour arc
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 32, Color(tint.r, tint.g, tint.b, 0.85), 2.2)


func _draw_bubble_number(radius: float, tier_num: int) -> void:
	var font := ThemeDB.fallback_font
	if font == null:
		return
	var txt := str(tier_num)
	var fs := int(clampf(radius * 0.92, 14.0, 56.0))
	var sz := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
	var origin := Vector2(-sz.x * 0.5, float(fs) * 0.36)

	# Drop shadow
	for o in [Vector2(-1.5, 0.0), Vector2(1.5, 0.0), Vector2(0.0, -1.5), Vector2(0.0, 1.5), Vector2(0.0, 2.5)]:
		draw_string(font, origin + o, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.02, 0.08, 0.18, 0.95))
	# White crisp text
	draw_string(font, origin, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 1.0, 1.0, 0.98))


func _draw_hud() -> void:
	var font := ThemeDB.fallback_font
	if font == null:
		return

	# Elegant semi-transparent status panel
	var panel_rect := Rect2(-BOX_W * 0.5 + 16.0, -BOX_H * 0.5 + 16.0, 260.0, 115.0)
	draw_rect(panel_rect, Color(0.02, 0.08, 0.18, 0.75))
	draw_rect(panel_rect, Color(0.55, 0.88, 1.0, 0.45), false, 1.5)

	var p_x := panel_rect.position.x + 14.0
	var p_y := panel_rect.position.y + 22.0

	# Title & Status
	draw_string(font, Vector2(p_x, p_y), "★ SQUISHINESS & JUICE LAB", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color(1.0, 0.90, 0.35))
	p_y += 22.0

	var lines := [
		"GRAVITY: %s" % gravity_names[gravity_mode],
		"STIFFNESS: %.0f  [ / ]" % stiffness,
		"DAMPING:   %.1f  - / =" % damping,
		"BUBBLES:   %d" % bubbles.size()
	]
	for line in lines:
		draw_string(font, Vector2(p_x, p_y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.78, 0.93, 1.0, 0.90))
		p_y += 18.0

	# Interactive Hint at Bottom
	var bot_rect := Rect2(-BOX_W * 0.5 + 16.0, BOX_H * 0.5 - 34.0, BOX_W - 32.0, 24.0)
	draw_rect(bot_rect, Color(0.02, 0.08, 0.18, 0.75))
	var hint := "CLICK & DRAG : Fling  |  RIGHT-CLICK : Poke  |  1-5 : Drop bubble  |  B : Spawn Titan  |  G : Gravity  |  R : Reset  |  C : Clear"
	var hsz := font.get_string_size(hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 11)
	draw_string(font, Vector2(-hsz.x * 0.5, BOX_H * 0.5 - 18.0), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(0.80, 0.92, 1.0, 0.85))


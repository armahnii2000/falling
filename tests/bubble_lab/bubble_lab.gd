extends Node2D
## Bubble Feel Lab — isolated sandbox for rapid squish/float/merge iteration.
## Open this scene directly (tests/bubble_lab/bubble_lab.tscn) to test without main game.

@export var test_gravity: float = -0.55
@export var test_linear_damp: float = 2.4
@export var test_angular_damp: float = 4.0
@export var test_bounce: float = 0.03
@export var test_friction: float = 0.95
@export var test_mass: float = 1.0
@export var test_launch_vel: float = -680.0
@export var test_spawn_radius: float = 35.0
@export var test_squash_threshold: float = 80.0
@export var test_squash_amount: float = 1.2
@export var test_squash_decay: float = 4.0
@export var test_drift_amp: float = 20.0
@export var test_drift_speed: float = 1.0
@export var test_substeps: int = 2

var physics_root: Node2D
var test_bubbles: Array[RigidBody2D] = []
var launcher_x: float = 0.0
var next_tier: int = 1
var cooldown: float = 0.0
const COOLDOWN_DURATION = 0.18

const TIER_RADII = {1: 18.0, 2: 24.0, 3: 31.0, 4: 39.0, 5: 48.0, 6: 58.0, 7: 69.0, 8: 81.0, 9: 94.0, 10: 108.0, 11: 124.0}
const TIER_COLORS = {
	1: Color(0.24, 0.78, 1.00), 2: Color(0.28, 0.90, 0.45), 3: Color(1.00, 0.88, 0.18),
	4: Color(1.00, 0.54, 0.16), 5: Color(1.00, 0.22, 0.52), 6: Color(0.68, 0.28, 1.00),
	7: Color(0.05, 0.85, 0.80), 8: Color(1.00, 0.10, 0.10), 9: Color(0.60, 0.95, 0.15),
	10: Color(0.15, 0.25, 0.55), 11: Color(0.98, 0.92, 0.60)
}

func _ready() -> void:
	physics_root = Node2D.new()
	physics_root.name = "PhysicsRoot"
	add_child(physics_root)
	
	# Chamber walls
	var walls := StaticBody2D.new()
	walls.name = "Walls"
	physics_root.add_child(walls)
	var board_left = -200.0
	var board_top = -400.0
	var board_w = 400.0
	var board_h = 600.0
	_add_wall(walls, Vector2(board_left - 20, board_top + board_h * 0.5), Vector2(40, board_h + 200))
	_add_wall(walls, Vector2(board_left + board_w + 20, board_top + board_h * 0.5), Vector2(40, board_h + 200))
	_add_wall(walls, Vector2(board_left + board_w * 0.5, board_top - 20), Vector2(board_w + 200, 40))
	_add_wall(walls, Vector2(board_left + board_w * 0.5, board_top + board_h + 20), Vector2(board_w + 200, 40))
	
	# Floor vent
	launcher_x = board_left + board_w * 0.5
	spawn_test_bubble()
	
	# Camera
	var cam = Camera2D.new()
	cam.enabled = true
	cam.make_current()
	cam.zoom = Vector2(1.2, 1.2)
	cam.position = Vector2(0, -100)
	add_child(cam)

func _add_wall(body: StaticBody2D, pos: Vector2, size: Vector2) -> void:
	var col := CollisionShape2D.new()
	var box := RectangleShape2D.new()
	box.size = size
	col.shape = box
	col.position = pos
	body.add_child(col)

func spawn_test_bubble(tier: int = -1) -> RigidBody2D:
	if tier == -1:
		tier = next_tier
	var r = TIER_RADII[tier]
	var col = TIER_COLORS[tier]
	var body := RigidBody2D.new()
	body.position = Vector2(launcher_x, 150.0)
	body.linear_velocity = Vector2(0.0, test_launch_vel)
	body.gravity_scale = test_gravity
	body.linear_damp = test_linear_damp
	body.angular_damp = test_angular_damp
	body.mass = test_mass
	
	var mat := PhysicsMaterial.new()
	mat.bounce = test_bounce
	mat.friction = test_friction
	body.physics_material_override = mat
	
	var c := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = r
	c.shape = circle
	body.add_child(c)
	
	body.contact_monitor = true
	body.max_contacts_reported = 8
	body.set_meta("tier", tier)
	body.set_meta("radius", r)
	body.set_meta("color", col)
	body.set_meta("merging", false)
	body.set_meta("spawn_time", 0.0)
	body.set_meta("wobble", 0.0)
	body.set_meta("scale_pop", 1.0)
	body.set_meta("squash_timer", 0.0)
	body.set_meta("squash_amount", 0.0)
	body.set_meta("squash_axis", Vector2.ZERO)
	body.set_meta("drift_phase", randf_range(0.0, TAU))
	body.set_meta("drift_amp", test_drift_amp)
	body.set_meta("drift_speed", test_drift_speed)
	body.set_meta("custom_integrator", true)
	
	body.body_entered.connect(_on_body_entered.bind(body))
	physics_root.add_child(body)
	test_bubbles.append(body)
	
	next_tier = (next_tier % 11) + 1
	return body

func _on_body_entered(other: Node, self_body: RigidBody2D) -> void:
	if not is_instance_valid(self_body) or not is_instance_valid(other):
		return
	if not (other is RigidBody2D):
		return
	var other_body := other as RigidBody2D
	if not test_bubbles.has(self_body) or not test_bubbles.has(other_body):
		return
	if self_body.get_meta("merging", false) or other_body.get_meta("merging", false):
		return
	
	var tier_self: int = self_body.get_meta("tier", 0)
	var tier_other: int = other_body.get_meta("tier", 0)
	
	if tier_self > 0 and tier_self < 11 and tier_self == tier_other:
		self_body.set_meta("merging", true)
		other_body.set_meta("merging", true)
		
		var mid = (self_body.global_position + other_body.global_position) * 0.5
		var next = tier_self + 1
		
		var new_b := spawn_test_bubble(next)
		new_b.global_position = mid
		new_b.linear_velocity = Vector2(randf_range(-15.0, 15.0), -70.0)
		new_b.set_meta("wobble", 0.5)
		new_b.set_meta("scale_pop", 1.45)
		
		test_bubbles.erase(self_body)
		test_bubbles.erase(other_body)
		self_body.queue_free()
		other_body.queue_free()
	else:
		# Impact squash
		var impact = (self_body.linear_velocity - other_body.linear_velocity).length()
		if impact > test_squash_threshold:
			var squish = clampf(impact / 500.0, 0.25, test_squash_amount)
			var dir = (self_body.global_position - other_body.global_position).normalized()
			if dir.length() < 0.01:
				dir = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized()
			self_body.set_meta("squash_axis", dir)
			self_body.set_meta("squash_amount", squish)
			self_body.set_meta("squash_timer", 0.25)
			other_body.set_meta("squash_axis", -dir)
			other_body.set_meta("squash_amount", squish)
			other_body.set_meta("squash_timer", 0.25)
			self_body.set_meta("wobble", maxf(float(self_body.get_meta("wobble", 0.0)), squish * 0.7))
			other_body.set_meta("wobble", maxf(float(other_body.get_meta("wobble", 0.0)), squish * 0.7))

func _physics_process(delta: float) -> void:
	if cooldown > 0.0:
		cooldown -= delta
	
	# Substepping for softer feel
	var h = delta / test_substeps
	for _i in range(test_substeps):
		# Drift sway applied each substep
		for b in test_bubbles:
			if is_instance_valid(b):
				var phase = b.get_meta("drift_phase", 0.0)
				var amp = b.get_meta("drift_amp", 0.0)
				var speed = b.get_meta("drift_speed", 1.0)
				var drift = sin(Time.get_ticks_msec() / 1000.0 * speed + phase) * amp * 0.5
				b.apply_force(Vector2(drift, 0.0))
		# Let physics run
		# Note: Godot runs physics automatically; we just inject forces here
	
	# Input
	var board_left = -200.0
	var board_w = 400.0
	var r = TIER_RADII[next_tier]
	var min_x = board_left + r + 8.0
	var max_x = board_left + board_w - r - 8.0
	
	var mouse_pos = get_global_mouse_position()
	if mouse_pos.x >= board_left - 30.0 and mouse_pos.x <= board_left + board_w + 30.0:
		launcher_x = clampf(mouse_pos.x, min_x, max_x)
	
	if Input.is_action_pressed("move_left"):
		launcher_x = clampf(launcher_x - 650.0 * delta, min_x, max_x)
	elif Input.is_action_pressed("move_right"):
		launcher_x = clampf(launcher_x + 650.0 * delta, min_x, max_x)
	
	var wants_launch = Input.is_action_just_pressed("rotate") or Input.is_action_just_pressed("accelerate") \
		or Input.is_action_just_pressed("ui_accept") \
		or (Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and cooldown <= 0.0)
	
	if wants_launch and cooldown <= 0.0:
		spawn_test_bubble()
		cooldown = COOLDOWN_DURATION

func _process(delta: float) -> void:
	# Decay squash/wobble
	for b in test_bubbles:
		if is_instance_valid(b):
			var w = b.get_meta("wobble", 0.0)
			if w > 0.001:
				b.set_meta("wobble", move_toward(w, 0.0, delta * 2.5))
			var sp = b.get_meta("scale_pop", 1.0)
			if sp > 1.001:
				b.set_meta("scale_pop", move_toward(sp, 1.0, delta * 3.6))
			var sq_t = b.get_meta("squash_timer", 0.0)
			if sq_t > 0.0:
				b.set_meta("squash_timer", maxf(0.0, sq_t - delta))
				var sq_a = b.get_meta("squash_amount", 0.0)
				b.set_meta("squash_amount", move_toward(sq_a, 0.0, delta * test_squash_decay))
	
	queue_redraw()

func _draw() -> void:
	# Chamber bg
	draw_rect(Rect2(-220, -420, 440, 640), Color(0.02, 0.08, 0.18))
	# Walls
	draw_rect(Rect2(-220, -420, 20, 640), Color(0.1, 0.2, 0.35))
	draw_rect(Rect2(200, -420, 20, 640), Color(0.1, 0.2, 0.35))
	draw_rect(Rect2(-220, -420, 440, 20), Color(0.1, 0.2, 0.35))
	draw_rect(Rect2(-220, 200, 440, 20), Color(0.1, 0.2, 0.35))
	
	# Launcher
	draw_circle(Vector2(launcher_x, 150), 24, Color(0.2, 0.16, 0.1, 0.7))
	draw_circle(Vector2(launcher_x, 148), 16, Color(0.08, 0.06, 0.04, 0.9))
	var next_r = TIER_RADII[next_tier]
	var next_col = TIER_COLORS[next_tier]
	_draw_bubble(Vector2(launcher_x, 100), next_r, next_col, next_tier, Vector2.ONE)
	
	# Bubbles
	for b in test_bubbles:
		if is_instance_valid(b):
			var pos = b.global_position
			var tier = b.get_meta("tier", 1)
			var r = b.get_meta("radius", 20.0)
			var col = b.get_meta("color", Color.WHITE)
			var wobble = b.get_meta("wobble", 0.0)
			var scale_pop = b.get_meta("scale_pop", 1.0)
			
			var squash = Vector2(scale_pop, scale_pop)
			var sq_t = b.get_meta("squash_timer", 0.0)
			var sq_amt = b.get_meta("squash_amount", 0.0)
			var sq_axis = b.get_meta("squash_axis", Vector2.ZERO)
			if sq_t > 0.0 and sq_amt > 0.0 and sq_axis.length() > 0.0:
				var perp = Vector2(-sq_axis.y, sq_axis.x)
				squash = sq_axis * (1.0 - sq_amt * 0.6) + perp * (1.0 + sq_amt * 0.4)
				squash *= scale_pop
			elif wobble > 0.001:
				var w_val = sin(Time.get_ticks_msec() / 1000.0 * 26.0) * wobble
				squash = Vector2((1.0 + w_val) * scale_pop, (1.0 - w_val) * scale_pop)
			else:
				squash *= scale_pop
			
			_draw_bubble(pos, r, col, tier, squash)
	
	# UI
	var font = ThemeDB.fallback_font
	if font:
		draw_string(font, Vector2(-200, -450), "BUBBLE FEEL LAB — A/D or mouse to aim, SPACE/Click to launch", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.7, 0.9, 1.0))
		draw_string(font, Vector2(-200, -430), "Gravity: %.2f  Damp: %.2f  Bounce: %.2f  Friction: %.2f  Mass: %.2f  Substeps: %d" % [test_gravity, test_linear_damp, test_bounce, test_friction, test_mass, test_substeps], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.6, 0.85, 1.0))
		draw_string(font, Vector2(-200, -410), "Next: Tier %d (r=%.0f)" % [next_tier, TIER_RADII[next_tier]], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(1.0, 0.88, 0.4))
		draw_string(font, Vector2(-200, -390), "Press 1-9 to tweak params live (see code)", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.6, 0.7, 0.9))

func _draw_bubble(center: Vector2, radius: float, tint: Color, tier_num: int, squash: Vector2) -> void:
	draw_set_transform(center, 0.0, squash)
	draw_circle(Vector2.ZERO, radius * 1.55, Color(tint.r, tint.g, tint.b, 0.08))
	draw_circle(Vector2.ZERO, radius, tint.darkened(0.35))
	draw_circle(Vector2.ZERO, radius * 0.90, tint)
	draw_circle(Vector2(-radius * 0.28, -radius * 0.30), radius * 0.34, tint.lightened(0.55))
	draw_circle(Vector2(-radius * 0.28, -radius * 0.30), radius * 0.16, Color(1.0, 1.0, 1.0, 0.90))
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 28, Color(tint.r, tint.g, tint.b, 0.75), 1.5)
	
	var font = ThemeDB.fallback_font
	if font:
		var txt = str(tier_num)
		var fs = int(clampf(radius * 0.95, 14.0, 52.0))
		var sz = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var origin = Vector2(-sz.x * 0.5, float(fs) * 0.36)
		for o in [Vector2(-1.5, 0.0), Vector2(1.5, 0.0), Vector2(0.0, -1.5), Vector2(0.0, 1.5), Vector2(0.0, 2.5)]:
			draw_string(font, origin + o, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.02, 0.08, 0.18, 0.90))
		draw_string(font, origin, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 1.0, 1.0, 0.98))
	
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		match event.keycode:
			49: test_gravity = -0.45   # KEY_1
			50: test_gravity = -0.55   # KEY_2
			51: test_gravity = -0.72   # KEY_3
			52: test_linear_damp = 1.85  # KEY_4
			53: test_linear_damp = 2.4   # KEY_5
			54: test_linear_damp = 3.0   # KEY_6
			55: test_bounce = 0.03       # KEY_7
			56: test_bounce = 0.08       # KEY_8
			57: test_bounce = 0.15       # KEY_9
			48: test_friction = 0.85     # KEY_0
			45: test_friction = 0.95     # KEY_MINUS
			46: test_friction = 0.5      # KEY_PERIOD
			81: test_mass = 1.0          # KEY_Q
			87: test_mass = 3.0          # KEY_W
			69: test_mass = 10.0         # KEY_E
			82: test_substeps = 1        # KEY_R
			84: test_substeps = 2        # KEY_T
			89: test_substeps = 4        # KEY_Y
			85: test_drift_amp = 12.0    # KEY_U
			73: test_drift_amp = 20.0    # KEY_I
			79: test_drift_amp = 35.0    # KEY_O
			80: test_squash_amount = 0.8 # KEY_P
			91: test_squash_amount = 1.2 # KEY_BRACKETLEFT
			93: test_squash_amount = 1.8 # KEY_BRACKETRIGHT
			65: spawn_test_bubble(1)     # KEY_A
			83: spawn_test_bubble(5)     # KEY_S
			68: spawn_test_bubble(11)    # KEY_D
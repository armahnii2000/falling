extends Node2D
##
## A.I.r bubbles - Suika Game Prototype (Inverted Buoyancy Edition)
##
## Bubbles float UPWARD toward the surface. When two bubbles of the same number
## touch, they pop and merge into the next number tier (1 + 1 = 2, 2 + 2 = 3, etc.).
## Merges generate A.I.r that streams across to grow Lake Ellem.
##
## Controls:
##   A / D or Left / Right / Mouse : Move launcher left and right
##   SPACE / W / Up / Left Click   : Launch bubble upward
##   P                             : Pause
##   R                             : Restart
##

const TempLogic := preload("res://scripts/temp_logic.gd")
const SB := preload("res://addons/softbody2d/softbody2d.gd")
var _disc_tex_cache := {}

# --- Chamber Dimensions -----------------------------------------------------
const BOARD_LEFT := -420.0
const BOARD_TOP := -620.0
const BOARD_W := 400.0
const BOARD_H := 780.0
const SEABED_TOP := 192.0
const DANGER_Y := 80.0 # Bubbles stacking lower than this point trigger danger

# --- Lake Ellem (Basin on the right) ----------------------------------------
const LAKE_X := 40.0
const LAKE_Y := -170.0
const LAKE_W := 400.0
const LAKE_H := 350.0
const AIR_CENTER := Vector2(240.0, -8.0)
const AIR_R := 108.0

# --- Tiers Configuration (1 through 11) -------------------------------------
const TIERS := {
	1: {
		"radius": 18.0,
		"color": Color(0.24, 0.78, 1.00),      # Electric Sky Blue
		"score": 1,
		"name": "1"
	},
	2: {
		"radius": 24.0,
		"color": Color(0.28, 0.90, 0.45),      # Mint Green
		"score": 2,
		"name": "2"
	},
	3: {
		"radius": 31.0,
		"color": Color(1.00, 0.88, 0.18),      # Golden Yellow
		"score": 3,
		"name": "3"
	},
	4: {
		"radius": 39.0,
		"color": Color(1.00, 0.54, 0.16),      # Sunset Orange
		"score": 4,
		"name": "4"
	},
	5: {
		"radius": 48.0,
		"color": Color(1.00, 0.22, 0.52),      # Hot Coral Pink
		"score": 5,
		"name": "5"
	},
	6: {
		"radius": 58.0,
		"color": Color(0.68, 0.28, 1.00),      # Deep Royal Violet
		"score": 6,
		"name": "6"
	},
	7: {
		"radius": 69.0,
		"color": Color(0.05, 0.85, 0.80),      # Bright Teal (was magenta, clashed with 5/8)
		"score": 7,
		"name": "7"
	},
	8: {
		"radius": 81.0,
		"color": Color(1.00, 0.10, 0.10),      # Pure Red (pushed redder from crimson)
		"score": 8,
		"name": "8"
	},
	9: {
		"radius": 94.0,
		"color": Color(0.60, 0.95, 0.15),      # Lime Chartreuse (was amber, clashed with 3/11)
		"score": 9,
		"name": "9"
	},
	10: {
		"radius": 108.0,
		"color": Color(0.15, 0.25, 0.55),      # Deep Navy (was jade, clashed with 2; only dark tier)
		"score": 10,
		"name": "10"
	},
	11: {
		"radius": 124.0,
		"color": Color(0.98, 0.92, 0.60),      # Radiant Solar Gold
		"score": 11,
		"name": "11"
	},
}

# --- Palette ----------------------------------------------------------------
const C_SKY_TOP := Color(0.180, 0.550, 0.780)
const C_SKY_MID := Color(0.070, 0.330, 0.620)
const C_SKY_BOTTOM := Color(0.020, 0.130, 0.320)
const C_SAND := Color(0.780, 0.680, 0.460)
const C_SAND_DARK := Color(0.560, 0.460, 0.300)
const C_ROCK := Color(0.280, 0.340, 0.420)
const C_ROCK_HI := Color(0.440, 0.520, 0.600)
const C_WEED := Color(0.110, 0.460, 0.310)
const C_WEED_HI := Color(0.220, 0.660, 0.420)
const C_COLUMN := Color(0.450, 0.800, 1.000, 0.08)
const C_SURFACE := Color(0.820, 0.960, 1.000)
const C_LAKE := Color(0.080, 0.480, 0.820)
const C_LAKE_RIM := Color(0.550, 0.950, 1.000)
const C_GLASS := Color(0.750, 0.940, 1.000, 0.300)
const C_GOLD := Color(1.000, 0.860, 0.350)

# --- State ------------------------------------------------------------------
var lake_size := 0
var best_score := 0
var highest_tier := 1
var total_merges := 0
var time := 0.0
var game_over := false
var paused := false

# --- Launcher State ---------------------------------------------------------
var launcher_x := BOARD_LEFT + BOARD_W * 0.5
var current_tier := 1
var next_tier := 1
var current_temp := "normal"
var next_temp := "normal"
var launch_cooldown := 0.0
const COOLDOWN_DURATION := 0.18

# --- Combo & Game Feel ------------------------------------------------------
var combo_count := 0
var last_merge_time := -999.0
var camera_trauma := 0.0
var popups: Array = []

# --- Procedural Audio -------------------------------------------------------
var sfx_pool: Array[AudioStreamPlayer] = []
var sfx_index := 0
var launch_stream: AudioStreamWAV
var chime_streams := {}
var supernova_stream: AudioStreamWAV

# --- Danger Line State ------------------------------------------------------
var danger_time := 0.0
const DANGER_LIMIT := 3.0
var is_in_danger := false

# --- Temperature / Pressure State (HOT/COLD/NORMAL test) --------------------
const TEMP_WARN := 20.0
const TEMP_BURST := 30.0
const HOT_PROB := 0.20
const COLD_PROB := 0.25
# NORMAL_PROB is remainder: 1.0 - HOT_PROB - COLD_PROB
var temperature := 0.0
var overheat := false

# --- Physics & Nodes --------------------------------------------------------
var physics_root: Node2D
# SoftBody2D roots (one per bubble; bones carry physics). Was Array[RigidBody2D].
var active_bubbles: Array = []

# --- Visual FX --------------------------------------------------------------
var particles: Array = []
var motes: Array = []
var stream_bubbles: Array = []
var lake_pulse := 0.0

# --- Camera & HUD -----------------------------------------------------------
@onready var camera: Camera2D = $Camera2D
var _view_rect := Rect2(-510.0, -754.0, 980.0, 1156.0)
var _camera_configured := false
var hud_layer: CanvasLayer
var score_label: Label
var next_label: Label
var stats_label: Label
var danger_label: Label
var over_label: Label
var pause_label: Label
var scrim: ColorRect


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	randomize()

	_init_sfx()
	_init_motes()
	_build_physics_world()
	_build_hud()
	_layout_camera()
	get_viewport().size_changed.connect(_layout_camera)

	# Roll initial launcher tiers
	current_tier = _roll_spawn_tier()
	next_tier = _roll_spawn_tier()
	current_temp = _roll_temp_type()
	next_temp = _roll_temp_type()
	_update_hud()


func _roll_spawn_tier() -> int:
	var r := randf()
	if r < 0.45:
		return 1
	elif r < 0.75:
		return 2
	elif r < 0.92:
		return 3
	elif r < 0.98:
		return 4
	else:
		return 5


func _roll_temp_type() -> String:
	var r := randf()
	if r < HOT_PROB:
		return "hot"
	elif r < HOT_PROB + COLD_PROB:
		return "cold"
	else:
		return "normal"


# --- Physics World Construction ---------------------------------------------

func _build_physics_world() -> void:
	physics_root = Node2D.new()
	physics_root.name = "PhysicsRoot"
	add_child(physics_root)

	var walls := StaticBody2D.new()
	walls.name = "ChamberWalls"
	physics_root.add_child(walls)

	# Left Wall
	_add_wall_shape(walls, Vector2(BOARD_LEFT - 20.0, BOARD_TOP + BOARD_H * 0.5), Vector2(40.0, BOARD_H + 200.0))
	# Right Wall
	_add_wall_shape(walls, Vector2(BOARD_LEFT + BOARD_W + 20.0, BOARD_TOP + BOARD_H * 0.5), Vector2(40.0, BOARD_H + 200.0))
	# Top Ceiling (Surface)
	_add_wall_shape(walls, Vector2(BOARD_LEFT + BOARD_W * 0.5, BOARD_TOP - 20.0), Vector2(BOARD_W + 200.0, 40.0))


func _add_wall_shape(body: StaticBody2D, pos: Vector2, size: Vector2) -> void:
	var col := CollisionShape2D.new()
	var box := RectangleShape2D.new()
	box.size = size
	col.shape = box
	col.position = pos
	body.add_child(col)


# --- Bubble Instantiation ---------------------------------------------------

# Softbody bake density by tier: 1-4 fine (10), 5-8 medium (16), 9-11 coarse (24).
func density_for_tier(t: int) -> float:
	if t <= 4:
		return 10.0
	if t <= 8:
		return 16.0
	return 24.0


# Tinted disc texture for the voronoi bake (required: generate() needs a texture).
func _bubble_disc_texture(r: float, tint: Color) -> Texture2D:
	var key := "%d_%s" % [int(r), str(tint.to_html())]
	if _disc_tex_cache.has(key):
		return _disc_tex_cache[key]
	var px := int(r * 2.0) + 16
	var img := Image.create_empty(px, px, false, Image.FORMAT_RGBA8)
	var c := Vector2(px, px) * 0.5
	for y in px:
		for x in px:
			var d := Vector2(x, y).distance_to(c)
			var a := clampf(1.0 - (d - r) / 8.0, 0.0, 1.0)
			img.set_pixel(x, y, Color(tint.r, tint.g, tint.b, a))
	var tex := ImageTexture.create_from_image(img)
	_disc_tex_cache[key] = tex
	return tex


func _create_bubble(pos: Vector2, tier: int, initial_velocity: Vector2 = Vector2.ZERO, temp_type: String = "normal") -> Node2D:
	var info: Dictionary = TIERS[tier]
	var r: float = info["radius"]
	var tint: Color = info["color"]

	# Runtime-baked softbody: one bone-RigidBody2D per voronoi region.
	var sb = SB.new()
	sb.texture = _bubble_disc_texture(r, tint)
	sb.vertex_interval = density_for_tier(tier)
	sb.gravity_scale = -0.55
	sb.linear_damp = 2.4
	sb.position = pos
	sb.set_meta("tier", tier)
	sb.set_meta("radius", r)
	sb.set_meta("color", tint)
	sb.set_meta("merging", false)
	sb.set_meta("spawn_time", time)
	sb.set_meta("scale_pop", 1.0)
	sb.set_meta("temp_type", temp_type)
	# Natural drift params: random phase + amplitude for organic sway.
	sb.set_meta("drift_phase", randf_range(0.0, TAU))
	sb.set_meta("drift_amp", randf_range(12.0, 28.0))
	sb.set_meta("drift_speed", randf_range(0.7, 1.3))
	physics_root.add_child(sb)
	sb.create_softbody2d(true)

	# Tag every bone: physics params, launch velocity, root link, merge signal.
	var bones := sb.find_children("*", "RigidBody2D", true, false)
	var total_mass := (r * r) / (18.0 * 18.0)
	var per_bone := total_mass / maxf(1.0, float(bones.size()))
	var mat := PhysicsMaterial.new()
	mat.bounce = 0.03
	mat.friction = 0.95
	var core: RigidBody2D = null
	var best := 1e20
	for b in bones:
		var rb := b as RigidBody2D
		rb.mass = per_bone
		rb.gravity_scale = -0.55
		rb.linear_damp = 2.4
		rb.angular_damp = 4.0
		rb.physics_material_override = mat
		rb.linear_velocity = initial_velocity
		rb.contact_monitor = true
		rb.max_contacts_reported = 8
		rb.set_meta("bubble_root", sb)
		rb.body_entered.connect(_on_bubble_body_entered.bind(rb))
		var d := rb.global_position.distance_squared_to(sb.global_position)
		if d < best:
			best = d
			core = rb
	sb.set_meta("core", core)
	sb.set_meta("bones", bones)
	active_bubbles.append(sb)

	highest_tier = maxi(highest_tier, tier)
	return sb


# --- Collision & Merge Logic ------------------------------------------------

func _on_bubble_body_entered(other: Node, self_body: RigidBody2D) -> void:
	if not is_instance_valid(self_body) or not is_instance_valid(other):
		return
	if not (other is RigidBody2D):
		return
	var other_body := other as RigidBody2D
	# Softbody bones carry a bubble_root link; bodies without one (walls) are ignored.
	if not self_body.has_meta("bubble_root") or not other_body.has_meta("bubble_root"):
		return
	var root_a = self_body.get_meta("bubble_root")
	var root_b = other_body.get_meta("bubble_root")
	if not is_instance_valid(root_a) or not is_instance_valid(root_b):
		return
	if root_a == root_b:
		return  # self-contact between bones of one bubble
	if not active_bubbles.has(root_a) or not active_bubbles.has(root_b):
		return
	if bool(root_a.get_meta("merging", false)) or bool(root_b.get_meta("merging", false)):
		return

	var tier_self: int = root_a.get_meta("tier", 0)
	var tier_other: int = root_b.get_meta("tier", 0)

	if tier_self > 0 and tier_self < 11 and tier_self == tier_other:
		# Lock both immediately to prevent double-firing
		root_a.set_meta("merging", true)
		root_b.set_meta("merging", true)

		var mid: Vector2 = (self_body.global_position + other_body.global_position) * 0.5
		var next := tier_self + 1

		# Points awarded matches the resulting bubble number!
		# 1+1=2 awards 2 pts, 2+2=3 awards 3 pts, ... 10+10=11 awards 11 pts!
		var base_pts: int = next

		# Fast combo multiplier (merges within 0.95s chain together)
		if time - last_merge_time < 0.95:
			combo_count += 1
		else:
			combo_count = 1
		last_merge_time = time

		var pts: int = base_pts * combo_count
		lake_size += pts
		total_merges += 1

		# Temperature effect via pure TempLogic (rules 11-19, tested in tests/test_merge.gd).
		var t1: String = str(root_a.get_meta("temp_type", "normal"))
		var t2: String = str(root_b.get_meta("temp_type", "normal"))
		var temp_delta: int = TempLogic.temp_delta(t1, t2, tier_self)
		temperature = TempLogic.apply_temp(temperature, temp_delta)
		var child_temp: String = TempLogic.child_temp(t1, t2)

		# Floating point popup at merge location
		var popup_txt := "+%d" % pts
		if combo_count > 1:
			popup_txt = "+%d (COMBO x%d!)" % [pts, combo_count]
		if next == 11:
			popup_txt = "+%d APEX TITAN!" % pts
		popups.append({
			"pos": mid,
			"text": popup_txt,
			"color": Color(1.0, 0.94, 0.35) if combo_count == 1 else Color(1.0, 0.35, 0.70),
			"life": 0.95,
			"max_life": 0.95,
			"scale": 1.4 if next == 11 else (1.0 if combo_count == 1 else 1.3)
		})

		# Camera punch & audio
		camera_trauma = minf(1.0, camera_trauma + 0.12 + float(tier_self) * 0.05)

		# Spawn merge visual fx
		_spawn_merge_fx(mid, tier_self)
		_stream_to_lake(mid, pts, TIERS[tier_self]["color"])

		# Play tier chime pop (or grand fanfare when Tier 11 is achieved)
		if next == 11:
			_spawn_supernova_fx(mid)
			_play_sfx(supernova_stream)
			camera_trauma = 0.90
		elif chime_streams.has(next):
			_play_sfx(chime_streams[next])

		# Spawn new bubble at midpoint with soft upward impulse, scale pop, and birth wobble
		var new_b := _create_bubble(mid, next, Vector2(randf_range(-15.0, 15.0), -70.0), child_temp)
		new_b.set_meta("wobble", 0.50)
		new_b.set_meta("scale_pop", 1.45)

		# Temp popup so heating / cooling reads clearly.
		if temp_delta > 0:
			popups.append({
				"pos": mid + Vector2(0, -28),
				"text": "+%d HEAT!" % temp_delta,
				"color": Color(1.0, 0.35, 0.20),
				"life": 0.95,
				"max_life": 0.95,
				"scale": 1.0
			})
		elif temp_delta < 0:
			popups.append({
				"pos": mid + Vector2(0, -28),
				"text": "%d COOL" % temp_delta,
				"color": Color(0.45, 0.85, 1.0),
				"life": 0.95,
				"max_life": 0.95,
				"scale": 1.0
			})

		active_bubbles.erase(root_a)
		active_bubbles.erase(root_b)
		root_a.queue_free()
		root_b.queue_free()

		_update_hud()

		# Overheat burst check: 20 warns, 30 pops the run.
		if temperature >= TEMP_BURST and not game_over:
			_spawn_supernova_fx(mid)
			_trigger_overheat()
	else:
		# Non-merge contact: strong visual squish + directional stretch from impact.
		var impact := (self_body.linear_velocity - other_body.linear_velocity).length()
		if impact > 80.0:
			var squish := clampf(impact / 500.0, 0.25, 1.2)
			# Directional squash along collision normal, stretch perpendicular
			var dir := (self_body.global_position - other_body.global_position).normalized()
			if dir.length() < 0.01:
				dir = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized()
			# Store squash axis and amount for _draw_styled_bubble to use
			self_body.set_meta("squash_axis", dir)
			self_body.set_meta("squash_amount", squish)
			self_body.set_meta("squash_timer", 0.25)
			other_body.set_meta("squash_axis", -dir)
			other_body.set_meta("squash_amount", squish)
			other_body.set_meta("squash_timer", 0.25)
			# Also boost wobble for extra juice
			self_body.set_meta("wobble", maxf(float(self_body.get_meta("wobble", 0.0)), squish * 0.7))
			other_body.set_meta("wobble", maxf(float(other_body.get_meta("wobble", 0.0)), squish * 0.7))


# --- Effects & Particles ----------------------------------------------------

func _spawn_merge_fx(pos: Vector2, tier: int) -> void:
	var col: Color = TIERS[tier]["color"]
	for i in 14:
		var a := randf_range(0.0, TAU)
		var sp := randf_range(50.0, 180.0)
		particles.append({
			"pos": pos,
			"vel": Vector2(cos(a) * sp, sin(a) * sp),
			"life": 0.45,
			"max_life": 0.45,
			"color": col.lightened(0.3),
			"radius": randf_range(2.0, 5.0)
		})
	# Expanding shockwave ring
	particles.append({
		"ring": true,
		"pos": pos,
		"radius": 10.0,
		"max_radius": TIERS[tier]["radius"] * 1.8,
		"life": 0.35,
		"max_life": 0.35,
		"color": C_GOLD
	})


func _spawn_supernova_fx(pos: Vector2) -> void:
	for i in 36:
		var a := randf_range(0.0, TAU)
		var sp := randf_range(90.0, 320.0)
		particles.append({
			"pos": pos,
			"vel": Vector2(cos(a) * sp, sin(a) * sp),
			"life": 0.80,
			"max_life": 0.80,
			"color": C_GOLD,
			"radius": randf_range(3.5, 8.0)
		})


func _stream_to_lake(start_pos: Vector2, pts: int, col: Color) -> void:
	var count := mini(pts, 6)
	for i in count:
		stream_bubbles.append({
			"pos": start_pos,
			"target": AIR_CENTER + Vector2(randf_range(-AIR_R * 0.4, AIR_R * 0.4), randf_range(-AIR_R * 0.4, AIR_R * 0.4)),
			"t": -randf_range(0.0, 0.12),
			"duration": 0.55,
			"color": col,
			"radius": randf_range(8.0, 14.0),
			"wob": randf_range(-1.0, 1.0)
		})


# --- Procedural Audio Synthesis ---------------------------------------------

func _init_sfx() -> void:
	for i in 8:
		var p := AudioStreamPlayer.new()
		p.volume_db = -4.0
		add_child(p)
		sfx_pool.append(p)

	launch_stream = _create_pop_wav(440.0, 0.08, 0.45, 0.8)

	var freqs := {
		2: 261.63, # C4
		3: 293.66, # D4
		4: 329.63, # E4
		5: 392.00, # G4
		6: 440.00, # A4
		7: 523.25, # C5
		8: 587.33, # D5
		9: 659.25, # E5
		10: 783.99, # G5
		11: 880.00, # A5
	}
	for t in freqs:
		chime_streams[t] = _create_pop_wav(freqs[t], 0.22, 0.60, 0.25)

	supernova_stream = _create_supernova_wav()


func _play_sfx(stream: AudioStreamWAV) -> void:
	if sfx_pool.is_empty() or stream == null:
		return
	var p := sfx_pool[sfx_index]
	sfx_index = (sfx_index + 1) % sfx_pool.size()
	p.stream = stream
	p.play()


func _create_pop_wav(freq: float, duration: float, volume: float, bend: float = 0.3) -> AudioStreamWAV:
	var sample_rate := 22050
	var sample_count := int(duration * float(sample_rate))
	var data := PackedByteArray()
	data.resize(sample_count * 2)
	for i in sample_count:
		var t := float(i) / float(sample_rate)
		var env := exp(-t * 22.0)
		var f := freq * (1.0 + (1.0 - t / duration) * bend)
		var s := sin(t * f * TAU) * env * volume
		s += sin(t * f * 2.0 * TAU) * env * (volume * 0.22)
		var val := int(clampf(s, -1.0, 1.0) * 32767.0)
		data.encode_s16(i * 2, val)
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.stereo = false
	wav.data = data
	return wav


func _create_supernova_wav() -> AudioStreamWAV:
	var sample_rate := 22050
	var duration := 0.65
	var sample_count := int(duration * float(sample_rate))
	var data := PackedByteArray()
	data.resize(sample_count * 2)
	var chords := [523.25, 659.25, 783.99, 1046.5]
	for i in sample_count:
		var t := float(i) / float(sample_rate)
		var s := 0.0
		for k in chords.size():
			var delay: float = float(k) * 0.07
			if t >= delay:
				var dt: float = t - delay
				var env := exp(-dt * 6.5)
				s += sin(dt * chords[k] * TAU) * env * 0.20
		var val := int(clampf(s, -1.0, 1.0) * 32767.0)
		data.encode_s16(i * 2, val)
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = sample_rate
	wav.stereo = false
	wav.data = data
	return wav


func _update_particles(delta: float) -> void:
	var alive := []
	for p in particles:
		p["life"] = float(p["life"]) - delta
		if float(p["life"]) <= 0.0:
			continue
		if p.has("ring"):
			var u: float = 1.0 - float(p["life"]) / float(p["max_life"])
			p["radius"] = lerpf(10.0, float(p["max_radius"]), u)
		else:
			p["pos"] = (p["pos"] as Vector2) + (p["vel"] as Vector2) * delta
			p["vel"] = (p["vel"] as Vector2) * 0.92
		alive.append(p)
	particles = alive

	var alive_streams := []
	for s in stream_bubbles:
		s["t"] = float(s["t"]) + delta
		if float(s["t"]) < 0.0:
			alive_streams.append(s)
			continue
		if float(s["t"]) >= float(s["duration"]):
			lake_pulse = 1.0
			continue
		alive_streams.append(s)
	stream_bubbles = alive_streams
	lake_pulse = maxf(0.0, lake_pulse - delta * 2.2)

	var alive_popups := []
	for pop in popups:
		pop["life"] = float(pop["life"]) - delta
		if float(pop["life"]) <= 0.0:
			continue
		pop["pos"] = (pop["pos"] as Vector2) + Vector2(0.0, -50.0 * delta)
		alive_popups.append(pop)
	popups = alive_popups


# --- Input & Launcher -------------------------------------------------------

func _process_launcher(delta: float) -> void:
	if game_over or paused:
		return

	if launch_cooldown > 0.0:
		launch_cooldown -= delta

	var r_val: float = float(TIERS[current_tier]["radius"])
	var min_x: float = BOARD_LEFT + r_val + 8.0
	var max_x: float = BOARD_LEFT + BOARD_W - r_val - 8.0

	# Mouse steering if cursor is inside game column area
	var mouse_pos := get_global_mouse_position()
	if mouse_pos.x >= BOARD_LEFT - 30.0 and mouse_pos.x <= BOARD_LEFT + BOARD_W + 30.0:
		launcher_x = clampf(mouse_pos.x, min_x, max_x)

	# Snappy keyboard steering (A/D or Left/Right)
	var move_speed := 650.0
	if Input.is_action_pressed("move_left"):
		launcher_x = clampf(launcher_x - move_speed * delta, min_x, max_x)
	elif Input.is_action_pressed("move_right"):
		launcher_x = clampf(launcher_x + move_speed * delta, min_x, max_x)

	# Fire launch
	var wants_launch := false
	if Input.is_action_just_pressed("rotate") or Input.is_action_just_pressed("accelerate"):
		wants_launch = true
	elif Input.is_action_just_pressed("ui_accept"):
		wants_launch = true
	elif Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and launch_cooldown <= 0.0:
		wants_launch = true

	if wants_launch and launch_cooldown <= 0.0:
		_launch_current_bubble()


func _launch_current_bubble() -> void:
	var spawn_y := SEABED_TOP - 40.0
	var initial_upward := Vector2(0.0, -680.0)
	
	_create_bubble(Vector2(launcher_x, spawn_y), current_tier, initial_upward, current_temp)
	_play_sfx(launch_stream)
	camera_trauma = minf(1.0, camera_trauma + 0.05)
	
	# Cycle next tier into launcher
	current_tier = next_tier
	current_temp = next_temp
	next_tier = _roll_spawn_tier()
	next_temp = _roll_temp_type()
	launch_cooldown = COOLDOWN_DURATION
	_update_hud()


# --- Danger Line & Game Over Check ------------------------------------------

func _check_danger(delta: float) -> void:
	if game_over or paused:
		return

	var breach := false
	for b in active_bubbles:
		if not is_instance_valid(b):
			continue
		# Softbody roots are Node2D: read velocity/position from core bone.
		var core: RigidBody2D = b.get_meta("core", null) as RigidBody2D
		var vel := Vector2.ZERO
		var bpos: Vector2 = b.position
		if is_instance_valid(core):
			vel = core.linear_velocity
			bpos = core.global_position - physics_root.global_position
		var age: float = time - float(b.get_meta("spawn_time", 0.0))
		# Only check bubbles that have had time to float up and settle
		if age > 0.6 and vel.length() < 70.0:
			var r: float = b.get_meta("radius", 20.0)
			if bpos.y + r > DANGER_Y:
				breach = true
				break

	is_in_danger = breach
	if breach:
		danger_time += delta
		var to_go := maxf(0.0, DANGER_LIMIT - danger_time)
		danger_label.text = "VENT OVERFLOW IN: %.1fs" % to_go
		danger_label.visible = true
		if danger_time >= DANGER_LIMIT:
			_trigger_game_over()
	else:
		danger_time = maxf(0.0, danger_time - delta * 2.0)
		danger_label.visible = false


func _trigger_game_over() -> void:
	game_over = true
	scrim.visible = true
	over_label.text = "THE BUBBLE OVERFLOWED!\n\nFinal Lake Size: %d A.I.r\nTotal Merges: %d\nHighest Tier: %d\nTemp: %.0f\n\nPress R to Restart" % [lake_size, total_merges, highest_tier, temperature]
	over_label.visible = true


func _trigger_overheat() -> void:
	game_over = true
	overheat = true
	camera_trauma = 1.0
	scrim.visible = true
	over_label.text = "OVERHEAT BURST!\n\nTemp hit %.0f (burst %d)\nFinal Lake Size: %d A.I.r\nTotal Merges: %d\nHighest Tier: %d\n\nPress R to Restart" % [temperature, int(TEMP_BURST), lake_size, total_merges, highest_tier]
	over_label.visible = true


# --- Per-frame loop ---------------------------------------------------------

func _process(delta: float) -> void:
	if Input.is_action_just_pressed("pause"):
		_set_paused(not paused)

	if paused:
		if Input.is_action_just_pressed("restart"):
			_set_paused(false)
			get_tree().call_deferred("reload_current_scene")
			return
		queue_redraw()
		return

	if Input.is_action_just_pressed("restart"):
		get_tree().call_deferred("reload_current_scene")
		return

	time += delta
	if not _camera_configured:
		_layout_camera()

	# Dynamic camera shake
	if camera_trauma > 0.0:
		camera_trauma = maxf(0.0, camera_trauma - delta * 2.8)
		var shake := camera_trauma * camera_trauma * 14.0
		camera.offset = Vector2(randf_range(-shake, shake), randf_range(-shake, shake))
	else:
		camera.offset = Vector2.ZERO

	_update_motes(delta)
	_update_particles(delta)
	_process_launcher(delta)
	_check_danger(delta)

	# Decay bubble wobble, scale_pop, squash + apply natural drift sway
	for b in active_bubbles:
		if is_instance_valid(b):
			var w: float = b.get_meta("wobble", 0.0)
			if w > 0.001:
				b.set_meta("wobble", move_toward(w, 0.0, delta * 2.5))
			var sp: float = b.get_meta("scale_pop", 1.0)
			if sp > 1.001:
				b.set_meta("scale_pop", move_toward(sp, 1.0, delta * 3.6))
			# Decay directional squash from impacts
			var sq_t: float = b.get_meta("squash_timer", 0.0)
			if sq_t > 0.0:
				b.set_meta("squash_timer", maxf(0.0, sq_t - delta))
				var sq_a: float = b.get_meta("squash_amount", 0.0)
				b.set_meta("squash_amount", move_toward(sq_a, 0.0, delta * 4.0))
			# Natural bubble drift: gentle horizontal sway as they rise (to bones).
			var phase: float = b.get_meta("drift_phase", 0.0)
			var amp: float = b.get_meta("drift_amp", 20.0)
			var speed: float = b.get_meta("drift_speed", 1.0)
			var drift_force := sin(time * speed + phase) * amp * 0.5
			var bones: Array = b.get_meta("bones", [])
			for bone in bones:
				if is_instance_valid(bone):
					(bone as RigidBody2D).apply_force(Vector2(drift_force, 0.0))

	queue_redraw()


func _set_paused(state: bool) -> void:
	paused = state
	get_tree().paused = state
	pause_label.visible = state


# --- HUD Construction & Updates ---------------------------------------------

func _build_hud() -> void:
	hud_layer = CanvasLayer.new()
	hud_layer.name = "HUD"
	hud_layer.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(hud_layer)

	score_label = Label.new()
	score_label.add_theme_font_size_override("font_size", 22)
	score_label.add_theme_color_override("font_color", Color(0.68, 0.90, 1.0))
	score_label.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.95))
	score_label.add_theme_constant_override("outline_size", 6)
	score_label.position = Vector2(28, 20)
	hud_layer.add_child(score_label)

	danger_label = Label.new()
	danger_label.add_theme_font_size_override("font_size", 28)
	danger_label.add_theme_color_override("font_color", Color(1.0, 0.35, 0.30))
	danger_label.add_theme_color_override("font_outline_color", Color(0.02, 0.08, 0.18, 0.98))
	danger_label.add_theme_constant_override("outline_size", 8)
	danger_label.position = Vector2(28, 170)
	danger_label.visible = false
	hud_layer.add_child(danger_label)

	var hint := Label.new()
	hint.text = "A / D or MOUSE  aim      SPACE or CLICK  launch bubble      P  pause      R  restart"
	hint.add_theme_font_size_override("font_size", 15)
	hint.add_theme_color_override("font_color", Color(0.65, 0.86, 1.0))
	hint.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.95))
	hint.add_theme_constant_override("outline_size", 5)
	hint.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	hint.position = Vector2(28, -40)
	hud_layer.add_child(hint)

	scrim = ColorRect.new()
	scrim.color = Color(0.02, 0.07, 0.15, 0.78)
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	scrim.visible = false
	hud_layer.add_child(scrim)

	over_label = Label.new()
	over_label.add_theme_font_size_override("font_size", 38)
	over_label.add_theme_color_override("font_color", Color(1.0, 0.88, 0.45))
	over_label.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.98))
	over_label.add_theme_constant_override("outline_size", 8)
	over_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	over_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	over_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	over_label.visible = false
	hud_layer.add_child(over_label)

	pause_label = Label.new()
	pause_label.text = "PAUSED\n\nP  resume      R  restart"
	pause_label.add_theme_font_size_override("font_size", 42)
	pause_label.add_theme_color_override("font_color", Color(0.75, 0.95, 1.0))
	pause_label.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.98))
	pause_label.add_theme_constant_override("outline_size", 8)
	pause_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pause_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	pause_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	pause_label.visible = false
	hud_layer.add_child(pause_label)


func _update_hud() -> void:
	best_score = maxi(best_score, lake_size)
	var temp_state := "STABLE"
	if temperature >= TEMP_BURST:
		temp_state = "BURST!"
	elif temperature >= TEMP_WARN:
		temp_state = "WARNING!"
	score_label.text = "LAKE A.I.r:  %d\nBEST SCORE:  %d\nHighest Tier:  %d / 11\nTotal Merges:  %d\nTEMP:  %.0f / %d  %s" % [lake_size, best_score, highest_tier, total_merges, temperature, int(TEMP_BURST), temp_state]


# --- Camera & View Framing --------------------------------------------------

func _layout_camera() -> void:
	var vp := get_viewport_rect().size
	if vp.x <= 1.0 or vp.y <= 1.0:
		return
	var left := -510.0
	var right := LAKE_X + LAKE_W + 40.0
	var top := BOARD_TOP - 70.0
	var bottom := SEABED_TOP + 210.0
	var bounds := Rect2(left, top, right - left, bottom - top)
	var z := clampf(minf(vp.x / bounds.size.x, vp.y / bounds.size.y), 0.22, 1.8)
	var center := bounds.get_center()
	if camera != null:
		camera.enabled = true
		camera.make_current()
		camera.zoom = Vector2(z, z)
		camera.position = center
	var half := vp * 0.5 / z
	_view_rect = Rect2(center - half, half * 2.0)
	_camera_configured = true
	queue_redraw()


# --- Rendering & Shading ----------------------------------------------------

func _draw() -> void:
	_draw_sky()
	_draw_rays()
	_draw_seabed()
	_draw_motes()
	_draw_column()
	_draw_danger_line()
	_draw_launcher_guideline()
	_draw_bubbles()
	_draw_launcher_preview()
	_draw_lake()
	_draw_temp_gauge()
	_draw_next_box()
	_draw_rules_panel()
	_draw_evolution_guide()
	_draw_particles()


func _draw_sky() -> void:
	var r := _view_rect.grow(8.0)
	var bands := 36
	var band_h := r.size.y / float(bands)
	for i in bands:
		var k := float(i) / float(bands - 1)
		var c: Color = C_SKY_TOP.lerp(C_SKY_MID, k * 2.0) if k < 0.5 else C_SKY_MID.lerp(C_SKY_BOTTOM, (k - 0.5) * 2.0)
		draw_rect(Rect2(r.position.x, r.position.y + band_h * float(i), r.size.x, band_h + 1.0), c)


func _draw_rays() -> void:
	var top := _view_rect.position.y
	var bottom := top + _view_rect.size.y * 1.15
	for i in 4:
		var fi := float(i)
		var base_x := -320.0 + fi * 210.0 + sin(time * 0.25 + fi) * 26.0
		var w_top := 30.0 + fi * 9.0
		var w_bot := 88.0 + fi * 24.0
		var a := 0.028 + 0.014 * sin(time * 0.6 + fi * 2.1)
		if a > 0.0:
			draw_colored_polygon(PackedVector2Array([
				Vector2(base_x - w_top, top),
				Vector2(base_x + w_top, top),
				Vector2(base_x + w_bot, bottom),
				Vector2(base_x - w_bot, bottom),
			]), Color(0.55, 0.80, 1.0, a))


func _init_motes() -> void:
	motes.clear()
	for i in 80:
		motes.append({
			"pos": Vector2(randf_range(-560.0, 560.0), randf_range(-760.0, 410.0)),
			"r": randf_range(1.2, 3.4),
			"sp": randf_range(6.0, 22.0),
			"ph": randf_range(0.0, TAU),
		})


func _update_motes(delta: float) -> void:
	for m in motes:
		var p: Vector2 = m["pos"]
		p.y -= float(m["sp"]) * delta
		p.x += sin(time * 0.7 + float(m["ph"])) * 8.0 * delta
		if p.y < -760.0:
			p.y = 410.0
			p.x = randf_range(-560.0, 560.0)
		m["pos"] = p


func _draw_motes() -> void:
	var bounds := _view_rect.grow(40.0)
	for m in motes:
		var p: Vector2 = m["pos"]
		if bounds.has_point(p):
			var a: float = 0.10 + 0.07 * sin(time * 1.4 + float(m["ph"]))
			if a > 0.0:
				var rr: float = m["r"]
				draw_circle(p, rr * 2.5, Color(0.50, 0.78, 1.0, a * 0.25))
				draw_circle(p, rr, Color(0.78, 0.92, 1.0, a))


func _seabed_y(x: float) -> float:
	return SEABED_TOP + sin(x * 0.006 + 0.7) * 10.0 + sin(x * 0.013 + 2.1) * 6.0


func _draw_seabed() -> void:
	var bottom := _view_rect.end.y + 20.0
	var left := _view_rect.position.x - 20.0
	var span := _view_rect.size.x + 40.0
	var steps := 48
	for i in steps:
		var xa := left + span * float(i) / float(steps)
		var xb := left + span * float(i + 1) / float(steps)
		draw_colored_polygon(PackedVector2Array([
			Vector2(xa, _seabed_y(xa)),
			Vector2(xb, _seabed_y(xb)),
			Vector2(xb, bottom),
			Vector2(xa, bottom),
		]), C_SAND)

	var edge := PackedVector2Array()
	for i in range(steps + 1):
		var x := left + span * float(i) / float(steps)
		edge.append(Vector2(x, _seabed_y(x)))
	draw_polyline(edge, Color(0.96, 0.92, 0.76, 0.45), 6.0)
	draw_polyline(edge, C_SAND_DARK, 2.0)

	_draw_rock(-474.0, 1.00)
	_draw_rock(-62.0, 0.55)
	_draw_rock(468.0, 0.85)
	_draw_weed(-496.0, 0.85, 0.4)
	_draw_weed(-58.0, 0.75, 1.1)
	_draw_weed(462.0, 0.80, 0.9)


func _draw_rock(x: float, s: float) -> void:
	var base := _seabed_y(x) + 6.0
	var r := 26.0 * s
	var pts := PackedVector2Array([
		Vector2(x - r, base + r * 0.5),
		Vector2(x - r * 0.6, base - r * 0.7),
		Vector2(x + r * 0.1, base - r * 0.95),
		Vector2(x + r * 0.8, base - r * 0.35),
		Vector2(x + r, base + r * 0.5),
	])
	draw_colored_polygon(pts, C_ROCK)
	draw_polyline(pts, C_ROCK_HI, 2.0)


func _draw_weed(x: float, s: float, phase: float) -> void:
	var base_y := _seabed_y(x) + 3.0
	var height := 96.0 * s
	var pts := PackedVector2Array()
	var seg := 7
	for i in range(seg + 1):
		var t := float(i) / float(seg)
		var sway := sin(time * 1.4 + phase + t * 2.6) * 14.0 * t * s
		pts.append(Vector2(x + sway, base_y - height * t))
	draw_polyline(pts, C_WEED, 6.0 * s)
	draw_polyline(pts, C_WEED_HI, 2.0 * s)


func _draw_column() -> void:
	var rect := Rect2(BOARD_LEFT, BOARD_TOP, BOARD_W, BOARD_H)
	draw_rect(rect, C_COLUMN)

	# Left and Right glowing walls
	draw_line(Vector2(BOARD_LEFT, BOARD_TOP), Vector2(BOARD_LEFT, BOARD_TOP + BOARD_H), Color(0.60, 0.88, 1.0, 0.45), 2.5)
	draw_line(Vector2(BOARD_LEFT + BOARD_W, BOARD_TOP), Vector2(BOARD_LEFT + BOARD_W, BOARD_TOP + BOARD_H), Color(0.60, 0.88, 1.0, 0.45), 2.5)

	# Water Surface at ceiling where bubbles gather
	var pts := PackedVector2Array()
	for i in range(25):
		var t := float(i) / 24.0
		pts.append(Vector2(BOARD_LEFT + BOARD_W * t, BOARD_TOP + sin(t * TAU * 2.0 + time * 1.8) * 4.0))
	draw_polyline(pts, C_SURFACE, 3.5)

	var font := ThemeDB.fallback_font
	if font != null:
		var stxt := "WATER SURFACE (BUBBLES STACK HERE)"
		var ssz := font.get_string_size(stxt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12)
		draw_string(font, Vector2(BOARD_LEFT + (BOARD_W - ssz.x) * 0.5, BOARD_TOP - 12.0),
			stxt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.82, 0.96, 1.0, 0.85))


func _draw_danger_line() -> void:
	var alpha := 0.30
	var line_col := Color(1.0, 0.40, 0.30, alpha)
	if is_in_danger:
		alpha = 0.60 + 0.40 * sin(time * 12.0)
		line_col = Color(1.0, 0.20, 0.18, alpha)

	# Dashed danger line
	var segments := 20
	var seg_w := BOARD_W / float(segments)
	for i in range(0, segments, 2):
		var x1 := BOARD_LEFT + float(i) * seg_w
		var x2 := BOARD_LEFT + float(i + 1) * seg_w
		draw_line(Vector2(x1, DANGER_Y), Vector2(x2, DANGER_Y), line_col, 2.5)

	var font := ThemeDB.fallback_font
	if font != null:
		var txt := "▲ OVERFLOW DANGER LIMIT (VENT BREACH) ▲" if not is_in_danger else "⚠ WARNING: VENT OVERFLOW CRITICAL! ⚠"
		draw_string(font, Vector2(BOARD_LEFT + 12.0, DANGER_Y - 8.0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, line_col)


func _draw_launcher_guideline() -> void:
	if game_over or paused:
		return
	var start_y := SEABED_TOP - 40.0
	var col := Color(0.70, 0.92, 1.0, 0.22)
	# Dashed guideline pointing up
	var y := start_y - 20.0
	while y > BOARD_TOP + 10.0:
		draw_line(Vector2(launcher_x, y), Vector2(launcher_x, y - 14.0), col, 1.8)
		y -= 26.0


func _draw_launcher_preview() -> void:
	if game_over or paused:
		return
	var spawn_y := SEABED_TOP - 40.0
	var info: Dictionary = TIERS[current_tier]
	var r: float = info["radius"]
	var col: Color = info["color"]

	# Vent base
	draw_circle(Vector2(launcher_x, SEABED_TOP), 24.0, Color(0.20, 0.16, 0.10, 0.70))
	draw_circle(Vector2(launcher_x, SEABED_TOP - 2.0), 16.0, Color(0.08, 0.06, 0.04, 0.90))

	# Ready bubble floating gently over vent
	var float_offset := sin(time * 4.0) * 3.0
	_draw_styled_bubble(Vector2(launcher_x, spawn_y + float_offset), r, col, current_tier, Vector2.ONE, current_temp)


func _draw_bubbles() -> void:
	# SoftBody2D roots render their own deforming polygon; we draw only
	# the temp ring + tier number as an overlay centered on the core bone.
	for b in active_bubbles:
		if not is_instance_valid(b):
			continue
		var core: RigidBody2D = b.get_meta("core", null) as RigidBody2D
		if not is_instance_valid(core):
			continue
		var pos: Vector2 = core.global_position - physics_root.global_position
		var tier: int = b.get_meta("tier", 1)
		var r: float = b.get_meta("radius", 20.0)
		var ttype: String = str(b.get_meta("temp_type", "normal"))
		_draw_bubble_overlay(pos, r, tier, ttype)


func _draw_bubble_overlay(center: Vector2, radius: float, tier_num: int, temp_type: String) -> void:
	draw_set_transform(center, 0.0, Vector2.ONE)
	if temp_type == "hot":
		draw_circle(Vector2.ZERO, radius * 1.30, Color(1.0, 0.30, 0.10, 0.22))
		draw_arc(Vector2.ZERO, radius * 1.08, 0.0, TAU, 28, Color(1.0, 0.35, 0.15, 0.85), 3.0)
	elif temp_type == "cold":
		draw_circle(Vector2.ZERO, radius * 1.30, Color(0.40, 0.80, 1.0, 0.20))
		draw_arc(Vector2.ZERO, radius * 1.08, 0.0, TAU, 28, Color(0.45, 0.85, 1.0, 0.85), 3.0)
	var font := ThemeDB.fallback_font
	if font != null:
		var txt := str(tier_num)
		var fs := int(clampf(radius * 0.95, 14.0, 52.0))
		var sz := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var origin := Vector2(-sz.x * 0.5, float(fs) * 0.36)
		for o in [Vector2(-1.5, 0.0), Vector2(1.5, 0.0), Vector2(0.0, -1.5), Vector2(0.0, 1.5), Vector2(0.0, 2.5)]:
			draw_string(font, origin + o, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.02, 0.08, 0.18, 0.90))
		draw_string(font, origin, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 1.0, 1.0, 0.98))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_styled_bubble(center: Vector2, radius: float, tint: Color, tier_num: int, squash: Vector2, temp_type: String = "normal") -> void:
	draw_set_transform(center, 0.0, squash)

	# Temp tint ring: hot glows red-orange, cold glows icy blue.
	if temp_type == "hot":
		draw_circle(Vector2.ZERO, radius * 1.30, Color(1.0, 0.30, 0.10, 0.22))
		draw_arc(Vector2.ZERO, radius * 1.08, 0.0, TAU, 28, Color(1.0, 0.35, 0.15, 0.85), 3.0)
	elif temp_type == "cold":
		draw_circle(Vector2.ZERO, radius * 1.30, Color(0.40, 0.80, 1.0, 0.20))
		draw_arc(Vector2.ZERO, radius * 1.08, 0.0, TAU, 28, Color(0.45, 0.85, 1.0, 0.85), 3.0)

	# 1. Soft atmospheric outer glow
	draw_circle(Vector2.ZERO, radius * 1.55, Color(tint.r, tint.g, tint.b, 0.08))
	# 2. Darkened base sphere for rich 3D shading
	draw_circle(Vector2.ZERO, radius, tint.darkened(0.35))
	# 3. Vibrant main color body
	draw_circle(Vector2.ZERO, radius * 0.90, tint)
	# 4. Soft internal specular crescent
	draw_circle(Vector2(-radius * 0.28, -radius * 0.30), radius * 0.34, tint.lightened(0.55))
	# 5. Bright highlight dot
	draw_circle(Vector2(-radius * 0.28, -radius * 0.30), radius * 0.16, Color(1.0, 1.0, 1.0, 0.90))
	# 6. Glass rim contour arc
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 28, Color(tint.r, tint.g, tint.b, 0.75), 1.5)

	# 7. BOLD NUMBER in center
	var font := ThemeDB.fallback_font
	if font != null:
		var txt := str(tier_num)
		var fs := int(clampf(radius * 0.95, 14.0, 52.0))
		var sz := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var origin := Vector2(-sz.x * 0.5, float(fs) * 0.36)

		# Drop shadow for clean readability
		for o in [Vector2(-1.5, 0.0), Vector2(1.5, 0.0), Vector2(0.0, -1.5), Vector2(0.0, 1.5), Vector2(0.0, 2.5)]:
			draw_string(font, origin + o, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.02, 0.08, 0.18, 0.90))
		# White crisp text
		draw_string(font, origin, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 1.0, 1.0, 0.98))

	# 8. Temp markers: steam wisps for HOT, frost dots for COLD.
	if temp_type == "hot":
		for k in 3:
			var fx := (float(k) - 1.0) * radius * 0.45
			var sway := sin(time * 6.0 + float(k) * 2.1) * 4.0
			var base_y := -radius * 1.05
			draw_line(Vector2(fx + sway, base_y), Vector2(fx - sway, base_y - 12.0), Color(1.0, 0.55, 0.25, 0.70), 2.0)
			draw_circle(Vector2(fx - sway, base_y - 14.0), 2.2, Color(1.0, 0.70, 0.35, 0.55))
	elif temp_type == "cold":
		for k in 3:
			var ang := -PI * 0.75 + float(k) * PI * 0.25 + sin(time * 3.0 + float(k)) * 0.08
			var p := Vector2(cos(ang), sin(ang)) * radius * 1.22
			draw_circle(p, 2.4, Color(0.75, 0.95, 1.0, 0.90))

	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_lake() -> void:
	var r := Rect2(LAKE_X, LAKE_Y, LAKE_W, LAKE_H)
	var pulse := 1.0 + lake_pulse * 0.07

	# Soft outer rim rings
	for i in range(4, 0, -1):
		var k := float(i)
		draw_colored_polygon(
			_round_pts(Rect2(r.position - Vector2(k * 8.0, k * 8.0), r.size + Vector2(k * 16.0, k * 16.0)), 78.0 + k * 8.0),
			Color(C_LAKE_RIM.r, C_LAKE_RIM.g, C_LAKE_RIM.b, 0.032))

	draw_colored_polygon(_round_pts(r, 78.0), C_LAKE)
	var low := Rect2(r.position + Vector2(0.0, r.size.y * 0.30), Vector2(r.size.x, r.size.y * 0.70))
	draw_colored_polygon(_round_pts(low, 66.0), Color(0.03, 0.25, 0.56, 0.55))
	draw_polyline(_round_pts(r, 78.0), C_LAKE_RIM, 3.0)

	# Water surface ripple line
	var wl_y := r.position.y + r.size.y * 0.11
	var wl := PackedVector2Array()
	for i in range(29):
		var t := float(i) / 28.0
		wl.append(Vector2(
			r.position.x + 10.0 + t * (r.size.x - 20.0),
			wl_y + sin(t * TAU * 2.2 + time * 1.4) * 5.0))
	draw_polyline(wl, Color(0.78, 0.97, 1.0, 0.40), 2.0)

	_draw_air_bubble(pulse)
	_draw_lake_text()


func _draw_air_bubble(pulse: float) -> void:
	var r := AIR_R * pulse
	draw_circle(AIR_CENTER, r * 1.24, Color(0.55, 0.92, 1.0, 0.055))
	draw_circle(AIR_CENTER, r * 1.11, Color(0.62, 0.94, 1.0, 0.070))
	draw_circle(AIR_CENTER, r, C_GLASS)
	draw_circle(AIR_CENTER, r * 0.80, Color(0.90, 0.98, 1.0, 0.100))
	draw_arc(AIR_CENTER, r, 0.0, TAU, 64, Color(0.86, 0.99, 1.0, 0.850), 3.0)
	draw_arc(AIR_CENTER, r * 0.94, 0.0, TAU, 64, Color(0.45, 0.85, 1.0, 0.400), 1.5)
	draw_circle(AIR_CENTER + Vector2(-r * 0.38, -r * 0.42), r * 0.20, Color(1.0, 1.0, 1.0, 0.32))
	draw_circle(AIR_CENTER + Vector2(-r * 0.26, -r * 0.30), r * 0.09, Color(1.0, 1.0, 1.0, 0.28))


func _draw_lake_text() -> void:
	var font := ThemeDB.fallback_font
	if font == null:
		return
	var r := Rect2(LAKE_X, LAKE_Y, LAKE_W, LAKE_H)

	var title := "LAKE ELLEM"
	var tsize := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22)
	draw_string(font, Vector2(AIR_CENTER.x - tsize.x * 0.5, r.position.y - 14.0),
		title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(0.76, 0.95, 1.0, 0.92))

	var txt := str(lake_size)
	var fs := 104
	if txt.length() >= 4:
		fs = 84
	if txt.length() >= 5:
		fs = 66
	var sz := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
	var origin := AIR_CENTER + Vector2(-sz.x * 0.5, float(fs) * 0.35)
	var shadow := Color(0.03, 0.18, 0.36, 0.85)
	for o in [Vector2(-2.0, 0.0), Vector2(2.0, 0.0), Vector2(0.0, -2.0), Vector2(0.0, 2.0), Vector2(0.0, 4.0)]:
		draw_string(font, origin + o, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, shadow)
	draw_string(font, origin, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.97, 1.0, 1.0))

	var tag := "A.I.r"
	var gsize := font.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 20)
	draw_string(font, Vector2(AIR_CENTER.x - gsize.x * 0.5, AIR_CENTER.y + AIR_R * 0.60),
		tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(0.62, 0.90, 1.0, 0.85))


func _draw_temp_gauge() -> void:
	# Vertical thermometer in the gap between chamber (ends x=-20) and lake (starts x=40).
	var gx := -8.0
	var gy := BOARD_TOP
	var gw := 30.0
	var gh := BOARD_H
	var frac := clampf(temperature / TEMP_BURST, 0.0, 1.0)
	var warn_frac := TEMP_WARN / TEMP_BURST
	# Background tube
	draw_rect(Rect2(gx, gy, gw, gh), Color(0.03, 0.12, 0.25, 0.70))
	# Fill from bottom up
	var fill_h := gh * frac
	var fill_col := Color(0.35, 0.80, 1.0)
	if temperature >= TEMP_WARN:
		var pulse := 0.60 + 0.40 * sin(time * 10.0)
		fill_col = Color(1.0, 0.45 + 0.20 * pulse, 0.15)
	elif temperature >= TEMP_WARN * 0.6:
		fill_col = Color(1.0, 0.80, 0.30)
	if fill_h > 0.5:
		draw_rect(Rect2(gx + 4.0, gy + gh - fill_h, gw - 8.0, fill_h), fill_col)
	# Warn + burst marker lines
	var warn_y := gy + gh * (1.0 - warn_frac)
	draw_line(Vector2(gx - 4.0, warn_y), Vector2(gx + gw + 4.0, warn_y), Color(1.0, 0.80, 0.25, 0.95), 2.5)
	draw_line(Vector2(gx - 4.0, gy + 2.0), Vector2(gx + gw + 4.0, gy + 2.0), Color(1.0, 0.25, 0.15, 0.95), 3.0)
	draw_rect(Rect2(gx, gy, gw, gh), Color(0.60, 0.88, 1.0, 0.45), false, 2.0)
	var font := ThemeDB.fallback_font
	if font != null:
		draw_string(font, Vector2(gx - 6.0, gy - 10.0), "TEMP", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(0.80, 0.94, 1.0, 0.95))
		draw_string(font, Vector2(gx - 2.0, warn_y - 5.0), "20", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(1.0, 0.85, 0.35, 0.95))
		var ttxt := "%d" % int(temperature)
		draw_string(font, Vector2(gx - 1.0, gy + gh + 18.0), ttxt, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, fill_col)


func _draw_next_box() -> void:
	var r := Rect2(40.0, -590.0, 160.0, 140.0)
	draw_colored_polygon(_round_pts(r, 16.0), Color(0.04, 0.20, 0.40, 0.65))
	draw_polyline(_round_pts(r, 16.0), Color(0.55, 0.88, 1.0, 0.45), 2.0)

	var font := ThemeDB.fallback_font
	if font != null:
		var title := "NEXT BUBBLE"
		var sz := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 14)
		draw_string(font, Vector2(r.position.x + (r.size.x - sz.x) * 0.5, r.position.y + 24.0),
			title, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.80, 0.94, 1.0, 0.95))

	var info: Dictionary = TIERS[next_tier]
	var next_r: float = float(info["radius"]) * 0.85
	var next_col: Color = info["color"]
	var bob := sin(time * 3.5) * 3.0
	_draw_styled_bubble(Vector2(r.position.x + r.size.x * 0.5, r.position.y + 80.0 + bob), next_r, next_col, next_tier, Vector2.ONE, next_temp)


func _draw_rules_panel() -> void:
	var r := Rect2(215.0, -590.0, 225.0, 168.0)
	draw_colored_polygon(_round_pts(r, 16.0), Color(0.04, 0.20, 0.40, 0.65))
	draw_polyline(_round_pts(r, 16.0), Color(0.55, 0.88, 1.0, 0.45), 2.0)

	var font := ThemeDB.fallback_font
	if font == null:
		return

	var title := "VENT STARTER PACK"
	var tsz := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 17)
	var title_col := Color(1.0, 0.88, 0.40, 0.95)
	if temperature >= TEMP_WARN:
		title_col = Color(1.0, 0.45, 0.25, 0.85 + 0.15 * sin(time * 10.0))
	draw_string(font, Vector2(r.position.x + (r.size.x - tsz.x) * 0.5, r.position.y + 26.0),
		title, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, title_col)

	var rules := [
		"Steer vent, yeet bubbles UP!",
		"Twins merge: 1+1=2 ... 11!",
		"HOT = spicy! Merge vents heat",
		"COLD = AC! Merge chills TEMP",
		"TEMP 20 = sweaty, 30 = KABOOM!",
	]
	var cols := [
		Color(0.78, 0.92, 1.0, 0.92),
		Color(0.78, 0.92, 1.0, 0.92),
		Color(1.0, 0.55, 0.35, 0.95),
		Color(0.50, 0.88, 1.0, 0.95),
		Color(1.0, 0.85, 0.40, 0.95),
	]
	var y := r.position.y + 52.0
	for i in rules.size():
		var bob := sin(time * 2.5 + float(i) * 0.9) * 1.2
		draw_string(font, Vector2(r.position.x + 12.0, y + bob), rules[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, cols[i])
		y += 23.0


func _draw_evolution_guide() -> void:
	var r := Rect2(40.0, -418.0, 400.0, 240.0)
	draw_colored_polygon(_round_pts(r, 18.0), Color(0.03, 0.16, 0.35, 0.70))
	draw_polyline(_round_pts(r, 18.0), Color(0.45, 0.85, 1.0, 0.40), 2.0)

	var font := ThemeDB.fallback_font
	if font == null:
		return

	var title := "BUBBLE EVOLUTION CYCLE (1 ➔ 11)"
	var sz := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 14)
	draw_string(font, Vector2(r.position.x + (r.size.x - sz.x) * 0.5, r.position.y + 20.0),
		title, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.70, 0.94, 1.0, 0.95))

	var sub := "Merge 2 matching bubbles into the next rank:"
	var ssz := font.get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 11)
	draw_string(font, Vector2(r.position.x + (r.size.x - ssz.x) * 0.5, r.position.y + 35.0),
		sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(0.60, 0.85, 1.0, 0.75))

	var col_x := [r.position.x + 50.0, r.position.x + 150.0, r.position.x + 250.0, r.position.x + 350.0]
	var arrow_x := [r.position.x + 100.0, r.position.x + 200.0, r.position.x + 300.0]

	# Row 1: Tiers 1, 2, 3, 4
	var y1 := r.position.y + 66.0
	for i in 4:
		var tier := i + 1
		var info: Dictionary = TIERS[tier]
		var br: float = 10.0 + float(tier) * 1.5
		_draw_styled_bubble(Vector2(col_x[i], y1), br, info["color"], tier, Vector2.ONE)
		var pts_txt := "1 (Vent)" if tier == 1 else "+%d" % tier
		var psz := font.get_string_size(pts_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 10)
		draw_string(font, Vector2(col_x[i] - psz.x * 0.5, y1 + br + 13.0), pts_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(1.0, 0.88, 0.45, 0.90))

	for ax in arrow_x:
		draw_string(font, Vector2(ax - 6.0, y1 + 5.0), "➔", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.65, 0.90, 1.0, 0.65))

	# Row 2: Tiers 5, 6, 7, 8
	var y2 := r.position.y + 126.0
	for i in 4:
		var tier := i + 5
		var info: Dictionary = TIERS[tier]
		var br: float = 16.0 + float(i) * 1.2
		_draw_styled_bubble(Vector2(col_x[i], y2), br, info["color"], tier, Vector2.ONE)
		var pts_txt := "+%d" % tier
		var psz := font.get_string_size(pts_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 10)
		draw_string(font, Vector2(col_x[i] - psz.x * 0.5, y2 + br + 13.0), pts_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color(1.0, 0.88, 0.45, 0.90))

	for ax in arrow_x:
		draw_string(font, Vector2(ax - 6.0, y2 + 5.0), "➔", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.65, 0.90, 1.0, 0.65))

	# Row 3: Tiers 9, 10, 11 (Apex Titan - Solid / Does Not Pop)
	var y3 := r.position.y + 186.0
	var col_x3 := [r.position.x + 65.0, r.position.x + 195.0, r.position.x + 330.0]
	var arrow_x3 := [r.position.x + 130.0, r.position.x + 262.0]

	for i in 3:
		var tier := i + 9
		var info: Dictionary = TIERS[tier]
		var br: float = 20.0 + float(i) * 1.5
		_draw_styled_bubble(Vector2(col_x3[i], y3), br, info["color"], tier, Vector2.ONE)
		var pts_txt := "+%d" % tier if tier < 11 else "11 (APEX TITAN)"
		var psz := font.get_string_size(pts_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 10)
		var col_lbl := Color(1.0, 0.88, 0.45, 0.90) if tier < 11 else Color(1.0, 0.92, 0.35, 1.0)
		draw_string(font, Vector2(col_x3[i] - psz.x * 0.5, y3 + br + 13.0), pts_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, col_lbl)

	for ax in arrow_x3:
		draw_string(font, Vector2(ax - 6.0, y3 + 5.0), "➔", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.65, 0.90, 1.0, 0.65))





func _round_pts(r: Rect2, radius: float, seg := 7) -> PackedVector2Array:
	var rad := minf(radius, minf(r.size.x, r.size.y) * 0.5)
	var corners := [
		Vector2(r.position.x + r.size.x - rad, r.position.y + rad),
		Vector2(r.position.x + r.size.x - rad, r.position.y + r.size.y - rad),
		Vector2(r.position.x + rad, r.position.y + r.size.y - rad),
		Vector2(r.position.x + rad, r.position.y + rad),
	]
	var angles := [-PI * 0.5, 0.0, PI * 0.5, PI]
	var pts := PackedVector2Array()
	for k in 4:
		var c: Vector2 = corners[k]
		for i in range(seg + 1):
			var a: float = float(angles[k]) + (PI * 0.5) * float(i) / float(seg)
			pts.append(c + Vector2(cos(a), sin(a)) * rad)
	pts.append(pts[0])
	return pts


func _draw_particles() -> void:
	for p in particles:
		var col: Color = p["color"]
		var life_ratio: float = float(p["life"]) / float(p["max_life"])
		col.a *= life_ratio
		if p.has("ring"):
			draw_arc(p["pos"], float(p["radius"]), 0.0, TAU, 32, col, 2.5)
		else:
			draw_circle(p["pos"], float(p["radius"]) * life_ratio, col)

	for s in stream_bubbles:
		var t: float = s["t"]
		if t < 0.0:
			continue
		var u := minf(1.0, t / float(s["duration"]))
		var e := u * u * (3.0 - 2.0 * u)
		var base: Vector2 = s["pos"]
		var pos: Vector2 = base.lerp(s["target"], e)
		pos.x += sin(u * PI * 1.3) * 38.0 * float(s["wob"]) * (1.0 - e)
		pos.y += sin(u * PI) * -28.0 * (1.0 - e)
		var fade: float = 1.0 if u < 0.75 else 1.0 - (u - 0.75) / 0.25
		var col: Color = s["color"]
		col.a = fade
		draw_circle(pos, float(s["radius"]) * (1.0 - 0.3 * e), col)

	# Floating Score & Combo Popups
	var font := ThemeDB.fallback_font
	if font != null:
		for pop in popups:
			var u: float = float(pop["life"]) / float(pop["max_life"])
			var alpha := clampf(u * 1.5, 0.0, 1.0)
			var col: Color = pop["color"]
			col.a = alpha
			var base_fs := 22.0 if not pop.has("scale") else 22.0 * float(pop["scale"])
			var fs := int(clampf(base_fs * (0.8 + 0.3 * (1.0 - u)), 14.0, 48.0))
			var txt: String = pop["text"]
			var sz := font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
			var pos: Vector2 = pop["pos"] - Vector2(sz.x * 0.5, float(fs) * 0.4)
			# Crisp drop shadow
			draw_string(font, pos + Vector2(1.5, 2.0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.01, 0.05, 0.12, alpha * 0.85))
			draw_string(font, pos, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

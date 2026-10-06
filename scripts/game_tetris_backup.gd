extends Node2D
##
## A.I.r bubbles - 2D cartoon underwater core loop.
##
## Inverted Tetris under the sea: bubble formations rise from vents in the
## seabed, stack downward from the surface, and any sealed row flashes gold and
## streams across into the great A.I.r bubble inside Lake Ellem, growing the lake.
##
## Grid indexing: row 0 is the BOTTOM row on screen, row ROWS-1 is the ceiling.
## Pieces rise by increasing their row index, so clearing a row makes every row
## below it float up to close the gap.
##

# --- board ------------------------------------------------------------------
const COLS := 10
const ROWS := 26
const CELL := 34.0
# Bubbles sit a hair inside their cell so ten of them read as exactly the width
# of the board, with no dead margin down either side.
const BUBBLE_R := 16.0

const BOARD_LEFT := -430.0
# The column hangs from the surface and keeps its foot on the sand, so extra
# depth grows upward: BOARD_H is ROWS * CELL, and BOARD_TOP is SEABED_TOP less
# that height.
const BOARD_TOP := -692.0
const BOARD_W := 340.0
const BOARD_H := 884.0

# --- seabed -----------------------------------------------------------------
const SEABED_TOP := 192.0

# --- Lake Ellem (a basin of its own, off to the right) ----------------------
const LAKE_X := 30.0
const LAKE_Y := -170.0
const LAKE_W := 400.0
const LAKE_H := 350.0
const AIR_CENTER := Vector2(230.0, -8.0)
const AIR_R := 108.0

# --- rules ------------------------------------------------------------------
const START_LAKE := 0
const LAKE_PER_ROW := 10
const BASE_RISE := 0.75
const ACCEL_RISE := 0.09

# --- pressure (the burn rate) ------------------------------------------------
# Pressure is counted in whole red energy bubbles sent into the lake. Twenty of
# them blows the gauge; the bar keeps a little headroom above that line.
const PRESSURE_MAX := 30.0
const BLOW_LINE := 20.0
const ENERGY_FILL := 1.0
# Pressure counts red bubbles sitting in the lake, so it does not evaporate on
# its own - a bubble that went in stays in. The only thing that takes red back
# out is antimatter cancelling it one for one.
const PRESSURE_BLEED := 0.0
const ANTI_LAKE_LOSS := 5
# The ten reds between the blow line and the top of the gauge are the fuse.
# Each one past the line is a tick; the tenth bursts the lake.
const FUSE_TICKS := 10

# --- feel -------------------------------------------------------------------
const BURST_TIME := 1.15
const FLASH_TIME := 0.26
const TRAVEL_TIME := 0.58
const SETTLE_TIME := 0.14
const PIECE_LERP := 16.0
const REST_TIME := 0.20
const SWAY_AMP := 3.4
const SWAY_FREQ := 1.55
const BOB_AMP := 1.9
const ROT_TIME := 0.16
const TRAIL_RATE := 0.11
const SQUASH_MAX := 0.15

# --- palette ----------------------------------------------------------------
const C_SKY_TOP := Color(0.180, 0.550, 0.780)
const C_SKY_MID := Color(0.070, 0.330, 0.620)
const C_SKY_BOTTOM := Color(0.020, 0.130, 0.320)
const C_SAND := Color(0.780, 0.680, 0.460)
const C_SAND_DARK := Color(0.560, 0.460, 0.300)
const C_ROCK := Color(0.280, 0.340, 0.420)
const C_ROCK_HI := Color(0.440, 0.520, 0.600)
const C_WEED := Color(0.110, 0.460, 0.310)
const C_WEED_HI := Color(0.220, 0.660, 0.420)
const C_COLUMN := Color(0.450, 0.800, 1.000, 0.070)
const C_GRID := Color(0.550, 0.850, 1.000, 0.120)
const C_GRID_STRONG := Color(0.780, 0.960, 1.000, 0.700)
const C_SURFACE := Color(0.820, 0.960, 1.000)
const C_BUBBLE := Color(0.320, 0.700, 1.000)
const C_BUBBLE_HI := Color(0.900, 0.970, 1.000, 0.850)
const C_GOLD := Color(1.000, 0.850, 0.400)
const C_LAKE := Color(0.080, 0.480, 0.820)
const C_LAKE_RIM := Color(0.550, 0.950, 1.000)
const C_GLASS := Color(0.750, 0.940, 1.000, 0.300)

# --- bubble types ------------------------------------------------------------
# Mass is the plain bubble and only carries weight. Energy is burn rate: it
# drives the pressure gauge up. Antimatter cancels stored energy one for one,
# and any surplus eats the lake.
const TYPE_MASS := 0
const TYPE_ENERGY := 1
const TYPE_ANTI := 2

const C_MASS := Color(0.320, 0.700, 1.000)
const C_ENERGY := Color(1.000, 0.380, 0.330)
const C_ANTI := Color(0.480, 0.300, 0.960)

const SPAWN_ENERGY := 0.24
const SPAWN_ANTI := 0.07

# Formations are lists of grid offsets, normalised so min x/y are 0.
const SHAPES := [
	[Vector2i(0, 0), Vector2i(0, 1)],
	[Vector2i(0, 0), Vector2i(0, 1), Vector2i(0, 2)],
	[Vector2i(0, 0), Vector2i(0, 1), Vector2i(1, 0)],
	[Vector2i(0, 0), Vector2i(0, 1), Vector2i(1, 0), Vector2i(1, 1)],
	[Vector2i(0, 0), Vector2i(1, 0), Vector2i(1, 1), Vector2i(2, 1)],
	[Vector2i(0, 0), Vector2i(0, 1), Vector2i(1, 1)],
]

# --- grid state -------------------------------------------------------------
var grid: Array = []
var settle: Dictionary = {}

# --- active formation -------------------------------------------------------
var piece_offsets: Array = []
var piece_types: Dictionary = {}
var piece_origin := Vector2i.ZERO
var piece_from := Vector2.ZERO
var piece_active := false
var rise_progress := 0.0
var rise_timer := 0.0
var h_dir := 0
var h_repeat := 0.0
var piece_phase := 0.0

# --- motion feel ------------------------------------------------------------
var rot_from: Array = []
var rot_t := 1.0
var trail: Array = []
var trail_timer := 0.0

# --- run state --------------------------------------------------------------
var lake_size := START_LAKE
var rows_cleared := 0
var game_over := false
var time := 0.0
var lake_pulse := 0.0
var pressure := 0.0
var stalled := false
var hud_pct := -1
var burst_t := -1.0
var paused := false

# --- fx ---------------------------------------------------------------------
var particles: Array = []
var motes: Array = []
var pending_rows: Array = []
var pending_tally: Dictionary = {}
var pending_landed := 0
var pending_total := 0

# --- view -------------------------------------------------------------------
var _view_rect := Rect2(-510.0, -754.0, 980.0, 1156.0)

@onready var camera: Camera2D = $Camera2D

var rows_label: Label
var over_label: Label
var pause_label: Label
var scrim: ColorRect


func _ready() -> void:
	# Pausing stops the tree, so this node has to keep processing input while
	# paused in order to un-pause it again.
	process_mode = Node.PROCESS_MODE_ALWAYS
	randomize()
	_build_hud()
	_init_motes()
	_init_grid()
	_update_hud()
	_layout_camera()
	get_viewport().size_changed.connect(_layout_camera)
	_spawn_piece()


# --- construction -----------------------------------------------------------

func _build_hud() -> void:
	var layer := CanvasLayer.new()
	layer.name = "HUD"
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(layer)

	rows_label = Label.new()
	rows_label.add_theme_font_size_override("font_size", 20)
	rows_label.add_theme_color_override("font_color", Color(0.62, 0.87, 1.0))
	rows_label.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.9))
	rows_label.add_theme_constant_override("outline_size", 5)
	rows_label.position = Vector2(26, 20)
	layer.add_child(rows_label)

	var hint := Label.new()
	hint.text = "A / D  steer      SPACE  rotate      W  rise faster      P  pause      R  restart"
	hint.add_theme_font_size_override("font_size", 16)
	hint.add_theme_color_override("font_color", Color(0.64, 0.85, 1.0))
	hint.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.9))
	hint.add_theme_constant_override("outline_size", 5)
	hint.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	hint.position = Vector2(26, -44)
	layer.add_child(hint)

	# Dim the whole scene behind the end-of-run message so it reads clearly
	# instead of competing with the lake and the playfield.
	scrim = ColorRect.new()
	scrim.color = Color(0.02, 0.07, 0.15, 0.74)
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	scrim.visible = false
	layer.add_child(scrim)

	over_label = Label.new()
	over_label.add_theme_font_size_override("font_size", 44)
	over_label.add_theme_color_override("font_color", Color(1.0, 0.87, 0.48))
	over_label.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.95))
	over_label.add_theme_constant_override("outline_size", 8)
	over_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	over_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	over_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	over_label.visible = false
	layer.add_child(over_label)

	pause_label = Label.new()
	pause_label.text = "PAUSED\n\nP  resume      R  restart"
	pause_label.add_theme_font_size_override("font_size", 42)
	pause_label.add_theme_color_override("font_color", Color(0.72, 0.94, 1.0))
	pause_label.add_theme_color_override("font_outline_color", Color(0.02, 0.10, 0.22, 0.95))
	pause_label.add_theme_constant_override("outline_size", 8)
	pause_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pause_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	pause_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	pause_label.visible = false
	layer.add_child(pause_label)


func _layout_camera() -> void:
	var vp := get_viewport_rect().size
	if vp.x <= 1.0 or vp.y <= 1.0:
		return
	# Frame the whole scene: the tall rise column on the left, Lake Ellem on the
	# right. The frame is measured from the play column itself, so a deeper
	# column still fits instead of running off the top of the screen.
	var lake := _lake_rect()
	var left := -510.0
	var right := lake.position.x + lake.size.x + 40.0
	var top := BOARD_TOP - CELL * 1.8
	var bottom := SEABED_TOP + 210.0
	var bounds := Rect2(left, top, right - left, bottom - top)
	var z := clampf(minf(vp.x / bounds.size.x, vp.y / bounds.size.y), 0.22, 1.8)
	var center := bounds.get_center()
	if camera != null:
		camera.zoom = Vector2(z, z)
		camera.position = center
	var half := vp * 0.5 / z
	_view_rect = Rect2(center - half, half * 2.0)
	queue_redraw()


func _init_grid() -> void:
	grid.clear()
	for r in range(ROWS):
		var row := []
		row.resize(COLS)
		row.fill(null)
		grid.append(row)


func _init_motes() -> void:
	motes.clear()
	for i in 84:
		motes.append({
			"pos": Vector2(randf_range(-560.0, 560.0), randf_range(-760.0, 410.0)),
			"r": randf_range(1.2, 3.6),
			"sp": randf_range(6.0, 24.0),
			"ph": randf_range(0.0, TAU),
		})


# --- geometry helpers -------------------------------------------------------

func _lake_rect() -> Rect2:
	return Rect2(LAKE_X, LAKE_Y, LAKE_W, LAKE_H)


func _seabed_y(x: float) -> float:
	return SEABED_TOP + sin(x * 0.006 + 0.7) * 10.0 + sin(x * 0.013 + 2.1) * 6.0


func _cell_pos(cell: Vector2i) -> Vector2:
	# Row 0 sits at the bottom of the column, row ROWS-1 at the surface.
	return Vector2(
		BOARD_LEFT + (float(cell.x) + 0.5) * CELL,
		BOARD_TOP + (float(ROWS - cell.y) - 0.5) * CELL
	)


func _piece_positions() -> Array:
	# Target grid positions of the active formation (rise offset excluded).
	var out := []
	for off in piece_offsets:
		out.append(_cell_pos(piece_origin + off))
	return out


func _shape_w() -> int:
	var w := 1
	for o in piece_offsets:
		w = maxi(w, o.x + 1)
	return w


func _normalize(shape: Array) -> Array:
	var mnx := 99
	var mny := 99
	for o in shape:
		mnx = mini(mnx, o.x)
		mny = mini(mny, o.y)
	var out := []
	for o in shape:
		out.append(Vector2i(o.x - mnx, o.y - mny))
	return out


func _roll_type() -> int:
	var r := randf()
	if r < SPAWN_ANTI:
		return TYPE_ANTI
	if r < SPAWN_ANTI + SPAWN_ENERGY:
		return TYPE_ENERGY
	return TYPE_MASS


func _tint(kind: int) -> Color:
	match kind:
		TYPE_ENERGY:
			return C_ENERGY
		TYPE_ANTI:
			return C_ANTI
		_:
			return C_MASS


func _fits(origin: Vector2i, offsets: Array) -> bool:
	for o in offsets:
		var c: int = origin.x + o.x
		var r: int = origin.y + o.y
		if c < 0 or c >= COLS or r < 0 or r >= ROWS:
			return false
		if grid[r][c] != null:
			return false
	return true


# --- formation lifecycle ----------------------------------------------------

func _spawn_piece() -> void:
	var shape: Array = SHAPES[randi() % SHAPES.size()]
	piece_offsets = _normalize(shape)
	piece_origin = Vector2i((COLS - _shape_w()) / 2, 0)
	piece_from = Vector2.ZERO

	# Roll a type per bubble, then guarantee at least one plain mass bubble so
	# every formation still carries useful weight.
	var kinds := []
	for i in piece_offsets.size():
		kinds.append(_roll_type())
	if not kinds.has(TYPE_MASS):
		kinds[randi() % kinds.size()] = TYPE_MASS
	piece_types.clear()
	for i in piece_offsets.size():
		piece_types[piece_offsets[i]] = kinds[i]

	if not _fits(piece_origin, piece_offsets):
		_game_over()
		return

	piece_active = true
	rise_progress = 0.0
	rise_timer = BASE_RISE
	piece_phase = randf_range(0.0, TAU)
	rot_from = []
	rot_t = 1.0
	trail_timer = 0.0
	trail.clear()


func _try_move(dx: int) -> void:
	if not _fits(piece_origin + Vector2i(dx, 0), piece_offsets):
		return
	piece_origin += Vector2i(dx, 0)
	piece_from.x -= float(dx) * CELL


func _try_rotate() -> void:
	# Rotate the shape, carrying each bubble's type with its offset so a
	# formation keeps its mass / energy / antimatter mix through a turn.
	var raw := []
	for o in piece_offsets:
		raw.append(Vector2i(o.y, -o.x))
	var mnx := 99
	var mny := 99
	for o in raw:
		mnx = mini(mnx, o.x)
		mny = mini(mny, o.y)
	var rot := []
	var rot_types := {}
	for i in raw.size():
		var key := Vector2i(raw[i].x - mnx, raw[i].y - mny)
		rot.append(key)
		rot_types[key] = piece_types.get(piece_offsets[i], TYPE_MASS)

	var nudges := [Vector2i.ZERO, Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-2, 0), Vector2i(2, 0)]
	for n in nudges:
		if _fits(piece_origin + n, rot):
			var before := _piece_positions()
			piece_offsets = rot
			piece_types = rot_types
			piece_origin += n
			piece_from.x = 0.0
			# Pair by geometric identity rather than nearest neighbour: rotated
			# offset i belongs to the same bubble as offset i beforehand, and
			# its type travels with it. Nearest-neighbour pairing minimised
			# travel but scrambled which colour landed on which bubble.
			rot_from = before
			rot_t = 0.0
			return


func _step_up() -> void:
	if _fits(piece_origin + Vector2i(0, 1), piece_offsets):
		piece_origin += Vector2i(0, 1)
	else:
		_lock_piece()


func _lock_piece() -> void:
	piece_active = false
	var drop := piece_from.y
	for off in piece_offsets:
		var c: int = piece_origin.x + off.x
		var r: int = piece_origin.y + off.y
		if r >= 0 and r < ROWS and c >= 0 and c < COLS:
			grid[r][c] = piece_types.get(off, TYPE_MASS)
			if drop > 0.5:
				settle[Vector2i(c, r)] = drop
	piece_offsets = []
	piece_types.clear()
	piece_from = Vector2.ZERO
	rot_from = []
	rot_t = 1.0

	var sealed := _clear_rows()
	if int(sealed["rows"]) > 0:
		# Banked, not applied: the lake only grows, and the pressure only moves,
		# once those bubbles have actually landed in it.
		pending_tally = sealed

	_spawn_piece()


func _clear_rows() -> Dictionary:
	if pending_total > 0:
		# A previous seal is still in flight - land it before starting another,
		# otherwise its rows would never collapse.
		_land_pending()

	var full := []
	for r in range(ROWS):
		var complete := true
		for c in range(COLS):
			if grid[r][c] == null:
				complete = false
				break
		if complete:
			full.append(r)

	if full.is_empty():
		return {"rows": 0, "energy": 0, "anti": 0}

	# The sealed bubbles leave the board whole and stream across into Lake Ellem
	# keeping the type and colour they had. This tally is the burn rate: it is
	# banked when they land, not now.
	var energy := 0
	var anti := 0
	for r in full:
		for c in range(COLS):
			var kind = grid[r][c]
			if kind != null:
				if kind == TYPE_ENERGY:
					energy += 1
				elif kind == TYPE_ANTI:
					anti += 1
				_spawn_seal_burst(_cell_pos(Vector2i(c, r)), kind, r)
				grid[r][c] = null

	# One bubble leaves the board per sealed cell. The seal lands - and the rows
	# collapse - once that many bubbles have arrived in the lake.
	pending_landed = 0
	pending_total = full.size() * COLS
	return {"rows": full.size(), "energy": energy, "anti": anti}


func _collapse_rows(rows: Array) -> void:
	# Everything in the sealed rows is already gone: close the gap they left.
	# Rows below a cleared row float up. Rows above stay put - they are held by
	# the surface.
	var new_grid := []
	for r in range(ROWS):
		var row := []
		row.resize(COLS)
		row.fill(null)
		new_grid.append(row)

	for r in range(ROWS):
		if rows.has(r):
			continue
		var shift := 0
		for fr in rows:
			if fr >= r:
				shift += 1
		var nr: int = r + shift
		for c in range(COLS):
			var col = grid[r][c]
			new_grid[nr][c] = col
			if col != null and nr != r:
				settle[Vector2i(c, nr)] = _cell_pos(Vector2i(c, r)).y - _cell_pos(Vector2i(c, nr)).y

	grid = new_grid


func _spawn_seal_burst(center: Vector2, kind: int, row: int) -> void:
	# One travelling bubble per sealed cell, carrying its own type so it arrives
	# in the lake as the same bubble you watched leave the board. Its row comes
	# along too: that row only collapses once every bubble from it has landed.
	particles.append({
		"pos": center,
		"t": -randf_range(0.0, 0.10),
		"target": AIR_CENTER + Vector2(
			randf_range(-AIR_R * 0.55, AIR_R * 0.55),
			randf_range(-AIR_R * 0.45, AIR_R * 0.45)
		),
		"wob": randf_range(-1.0, 1.0),
		"kind": kind,
		"row": row,
	})


func _burst_lake() -> void:
	# Internal pressure went past what the great bubble could hold, so it goes.
	piece_active = false
	game_over = true
	burst_t = 0.0
	over_label.text = "THE LAKE BURST" + String.chr(10) \
		+ "pressure hit %d red bubbles" % int(round(pressure)) + String.chr(10) \
		+ String.chr(10) + "Press R to run it back"
	scrim.visible = true
	over_label.visible = true


func _game_over() -> void:
	piece_active = false
	game_over = true
	over_label.text = "THE LAKE STALLED\nLake Size: %d\n\nPress R to run it back" % lake_size
	scrim.visible = true
	over_label.visible = true


func _update_hud() -> void:
	hud_pct = int(round(pressure / PRESSURE_MAX * 100.0))
	# How many red energy bubbles are sitting in the lake right now.
	var reds := int(round(pressure))
	var txt := "rows reclaimed:  %d\npressure:  %d%%" % [rows_cleared, hud_pct]
	if stalled:
		txt += "\nGROWTH STALLED - the lake is not filling"
	txt += String.chr(10) + "red energy in lake:  %d" % reds
	if stalled:
		# Past the blow line every extra red is one tick of the fuse.
		var to_go := int(ceil(PRESSURE_MAX - pressure))
		txt += String.chr(10) + "CRITICAL - %d more red and it bursts" % to_go
	rows_label.text = txt


# --- per-frame updates ------------------------------------------------------

func _update_motes(delta: float) -> void:
	for m in motes:
		var p: Vector2 = m["pos"]
		p.y -= float(m["sp"]) * delta
		p.x += sin(time * 0.7 + float(m["ph"])) * 8.0 * delta
		if p.y < -760.0:
			p.y = 410.0
			p.x = randf_range(-560.0, 560.0)
		m["pos"] = p


func _update_particles(delta: float) -> void:
	var alive := []
	for p in particles:
		p["t"] = float(p["t"]) + delta
		if float(p["t"]) >= TRAVEL_TIME:
			# The bubble has arrived in Lake Ellem. Only now does its row come
			# off the board, and only now does it count towards the burn rate.
			pending_rows.append(int(p["row"]))
			pending_landed += 1
			if pending_tally.has("energy"):
				if int(p["kind"]) == TYPE_ENERGY:
					pending_tally["energy"] = int(pending_tally["energy"]) + 1
				elif int(p["kind"]) == TYPE_ANTI:
					pending_tally["anti"] = int(pending_tally["anti"]) + 1
			lake_pulse = 1.0
			continue
		alive.append(p)
	particles = alive
	# Every bubble that left the board has arrived in the lake - land the seal.
	# particles is empty at exactly this moment, so it must NOT be part of this
	# guard: requiring a live particle blocked the landing forever, which froze
	# the board (no collapse) and the HUD (nothing banked).
	if pending_total > 0 and pending_landed >= pending_total:
		_land_pending()
	lake_pulse = maxf(0.0, lake_pulse - delta * 1.8)


func _land_pending() -> void:
	# Every bubble of the sealed rows has reached the lake: shift the board up by
	# one for each row that went, and bank the run's takings.
	if pending_rows.is_empty():
		# Nothing has arrived yet - there is nothing to collapse or bank.
		pending_landed = 0
		pending_total = 0
		pending_tally = {}
		return

	var landed: Array = pending_rows.duplicate()
	landed.sort()
	landed.reverse()
	# pending_rows holds one entry per landed bubble, so a cleared row shows up
	# once per column. Collapsing needs each cleared row exactly once - treating
	# the duplicates as separate rows walked the shift off the top of the board.
	var rows := []
	for r in landed:
		if rows.is_empty() or int(rows[rows.size() - 1]) != int(r):
			rows.append(int(r))
	_collapse_rows(rows)

	rows_cleared += int(pending_tally["rows"])
	pending_rows.clear()
	pending_landed = 0
	pending_total = 0
	_apply_yield(pending_tally)
	pending_tally = {}


func _apply_yield(sealed: Dictionary) -> void:
	# A sealed row grows the lake - unless the burn rate has blown past the
	# line, in which case growth stalls hard until pressure bleeds back down.
	if not stalled:
		lake_size += int(sealed["rows"]) * LAKE_PER_ROW

	var net: int = int(sealed["energy"]) - int(sealed["anti"])
	if net > 0:
		pressure = minf(PRESSURE_MAX, pressure + float(net) * ENERGY_FILL)
	elif net < 0:
		# Antimatter cancels stored energy one for one; whatever energy it
		# cannot cancel eats the lake instead.
		var surplus := float(-net)
		var cancelled := minf(pressure, surplus * ENERGY_FILL)
		pressure -= cancelled
		var left := surplus - cancelled / ENERGY_FILL
		if left > 0.001:
			lake_size = maxi(0, lake_size - int(ceil(left)) * ANTI_LAKE_LOSS)

	stalled = pressure >= BLOW_LINE
	_update_hud()


func _update_settle(delta: float) -> void:
	if settle.is_empty():
		return
	var step := CELL * delta / SETTLE_TIME
	for k in settle.keys():
		var v: float = settle[k]
		v = move_toward(v, 0.0, step)
		if absf(v) < 0.6:
			settle.erase(k)
		else:
			settle[k] = v


func _update_pressure(delta: float) -> void:
	if game_over or paused:
		return
	var was := stalled
	pressure = maxf(0.0, pressure - PRESSURE_BLEED * delta)
	# Growth only returns once the red count has come back down under the line,
	# and antimatter is the only thing that takes red out of the lake.
	if stalled and pressure < BLOW_LINE * 0.85:
		stalled = false
	# Fill the gauge to the top and the great bubble can no longer hold its
	# pressure. Antimatter is the only thing that takes red back out in time.
	if pressure >= PRESSURE_MAX:
		_burst_lake()
		return
	if was != stalled or int(round(pressure / PRESSURE_MAX * 100.0)) != hud_pct:
		_update_hud()


func _update_trail(delta: float) -> void:
	# Little bubbles shed by the rising formation, so the climb leaves a wake.
	if not piece_active:
		trail.clear()
		trail_timer = 0.0
		return

	trail_timer -= delta
	if trail_timer <= 0.0:
		trail_timer = TRAIL_RATE
		var pts := _piece_positions()
		if not pts.is_empty():
			var src: Vector2 = pts[randi() % pts.size()] + piece_from
			trail.append({
				"pos": src + Vector2(randf_range(-7.0, 7.0), randf_range(-3.0, 5.0)),
				"t": 0.0,
				"r": randf_range(1.5, 3.2),
				"sp": randf_range(15.0, 32.0),
				"wob": randf_range(-1.0, 1.0),
				"ph": randf_range(0.0, TAU),
			})

	var alive := []
	for b in trail:
		b["t"] = float(b["t"]) + delta
		if float(b["t"]) >= 1.1:
			continue
		alive.append(b)
	trail = alive


func _process_input(delta: float) -> void:
	if Input.is_action_just_pressed("restart"):
		get_tree().call_deferred("reload_current_scene")
		return

	if game_over or not piece_active:
		return

	if Input.is_action_just_pressed("rotate"):
		_try_rotate()

	var dir := 0
	if Input.is_action_pressed("move_left"):
		dir = -1
	elif Input.is_action_pressed("move_right"):
		dir = 1

	if dir != 0:
		if dir != h_dir:
			h_dir = dir
			h_repeat = 0.22
			_try_move(dir)
		else:
			h_repeat -= delta
			if h_repeat <= 0.0:
				h_repeat = 0.07
				_try_move(dir)
	else:
		h_dir = 0
		h_repeat = 0.0

	var interval := ACCEL_RISE if Input.is_action_pressed("accelerate") else BASE_RISE
	interval = maxf(0.06, interval - float(rows_cleared) * 0.012)
	rise_timer = interval

	if _fits(piece_origin + Vector2i(0, 1), piece_offsets):
		# Buoyant climb: one cell per interval, glided continuously rather than
		# jumped a row at a time.
		rise_progress += delta / interval
		while rise_progress >= 1.0 and piece_active:
			if not _fits(piece_origin + Vector2i(0, 1), piece_offsets):
				rise_progress = 1.0
				break
			rise_progress -= 1.0
			_step_up()
	else:
		# Nudged up under the stack: drift the last fraction flush, then seal.
		rise_progress = move_toward(rise_progress, 1.0, delta / REST_TIME)
		if rise_progress >= 0.999:
			_lock_piece()


func _process(delta: float) -> void:
	# The pause toggle is read above the freeze, so it still responds while the
	# rest of the frame is held still.
	if Input.is_action_just_pressed("pause"):
		_set_paused(not paused)
	if paused:
		if Input.is_action_just_pressed("restart"):
			# Restarting from the pause menu has to lift the freeze too, or the
			# fresh scene would come up still paused.
			_set_paused(false)
			get_tree().call_deferred("reload_current_scene")
			return
		# Hold everything still while the menu is up. The frame keeps drawing so
		# the board stays visible behind the overlay.
		queue_redraw()
		return
	time += delta
	if burst_t >= 0.0:
		burst_t += delta
	_update_motes(delta)
	_update_particles(delta)
	_update_settle(delta)
	_update_trail(delta)
	_update_pressure(delta)
	_process_input(delta)
	if piece_active:
		piece_from.x = lerpf(piece_from.x, 0.0, clampf(delta * PIECE_LERP, 0.0, 1.0))
		piece_from.y = (1.0 - rise_progress) * CELL
		rot_t = minf(1.0, rot_t + delta / ROT_TIME)
	queue_redraw()


func _set_paused(state: bool) -> void:
	paused = state
	get_tree().paused = state
	pause_label.visible = state


# --- drawing helpers --------------------------------------------------------

func _ellipse(center: Vector2, rx: float, ry: float, color: Color, segments := 48) -> void:
	var pts := PackedVector2Array()
	for i in segments:
		var a := TAU * float(i) / float(segments)
		pts.append(center + Vector2(cos(a) * rx, sin(a) * ry))
	draw_colored_polygon(pts, color)


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


func _draw_bubble(center: Vector2, radius: float, tint: Color) -> void:
	draw_circle(center, radius * 1.70, Color(tint.r, tint.g, tint.b, 0.09))
	draw_circle(center, radius, tint.darkened(0.32))
	draw_circle(center, radius * 0.90, tint)
	draw_circle(center - Vector2(radius * 0.30, radius * 0.32), radius * 0.32, tint.lightened(0.55))
	draw_circle(center - Vector2(radius * 0.30, radius * 0.32), radius * 0.18, C_BUBBLE_HI)
	draw_arc(center, radius, 0.0, TAU, 26, Color(tint.r, tint.g, tint.b, 0.70), 1.4)


func _draw_bubble_shaped(center: Vector2, radius: float, tint: Color, squash: Vector2) -> void:
	# Bubbles are not rigid circles: a bubble climbing fast is a little taller
	# than it is wide, and relaxes back to round as it slows.
	draw_set_transform(center, 0.0, squash)
	_draw_bubble(Vector2.ZERO, radius, tint)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


# --- scenery ----------------------------------------------------------------

func _draw_sky() -> void:
	var r := _view_rect.grow(8.0)
	var bands := 40
	var band_h := r.size.y / float(bands)
	for i in bands:
		var k := float(i) / float(bands - 1)
		var c: Color
		if k < 0.5:
			c = C_SKY_TOP.lerp(C_SKY_MID, k * 2.0)
		else:
			c = C_SKY_MID.lerp(C_SKY_BOTTOM, (k - 0.5) * 2.0)
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
		if a <= 0.0:
			continue
		draw_colored_polygon(PackedVector2Array([
			Vector2(base_x - w_top, top),
			Vector2(base_x + w_top, top),
			Vector2(base_x + w_bot, bottom),
			Vector2(base_x - w_bot, bottom),
		]), Color(0.55, 0.80, 1.0, a))


func _draw_motes() -> void:
	var bounds := _view_rect.grow(40.0)
	for m in motes:
		var p: Vector2 = m["pos"]
		if not bounds.has_point(p):
			continue
		var a: float = 0.10 + 0.07 * sin(time * 1.4 + float(m["ph"]))
		if a <= 0.0:
			continue
		var rr: float = m["r"]
		draw_circle(p, rr * 2.6, Color(0.50, 0.78, 1.0, a * 0.26))
		draw_circle(p, rr, Color(0.78, 0.92, 1.0, a))


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
	_draw_weed(-466.0, 0.60, 2.2)
	_draw_weed(-58.0, 0.75, 1.1)
	_draw_weed(-26.0, 0.55, 3.4)
	_draw_weed(462.0, 0.80, 0.9)
	_draw_weed(492.0, 0.60, 2.7)

	# Bubble vents: the source. One under each column of the rise zone.
	for c in range(COLS):
		var vx := BOARD_LEFT + (float(c) + 0.5) * CELL
		var vy := _seabed_y(vx)
		draw_circle(Vector2(vx, vy + 1.0), CELL * 0.32, Color(0.30, 0.24, 0.15, 0.50))
		draw_circle(Vector2(vx, vy - 1.0), CELL * 0.19, Color(0.11, 0.09, 0.06, 0.80))


# --- play column ------------------------------------------------------------

func _draw_column() -> void:
	# One border, exactly the width of the ten play columns, and nothing between
	# it and the first bubble - so there is no dead space to misread as a column
	# that is out of play.
	var rect := Rect2(BOARD_LEFT, BOARD_TOP, BOARD_W, BOARD_H)
	draw_rect(rect, C_COLUMN)

	for c in range(COLS + 1):
		var x := BOARD_LEFT + float(c) * CELL
		var edge := c == 0 or c == COLS
		draw_line(Vector2(x, BOARD_TOP), Vector2(x, BOARD_TOP + BOARD_H),
			C_GRID_STRONG if edge else C_GRID, 2.0 if edge else 1.0)
	for r in range(ROWS + 1):
		var y := BOARD_TOP + float(r) * CELL
		var edge := r == 0 or r == ROWS
		draw_line(Vector2(BOARD_LEFT, y), Vector2(BOARD_LEFT + BOARD_W, y),
			C_GRID_STRONG if edge else C_GRID, 2.0 if edge else 1.0)

	# The surface the stack builds down from, sitting on the top edge itself.
	var pts := PackedVector2Array()
	for i in range(25):
		var t := float(i) / 24.0
		pts.append(Vector2(BOARD_LEFT + BOARD_W * t, BOARD_TOP + sin(t * TAU * 2.0 + time * 1.6) * 4.0))
	draw_polyline(pts, C_SURFACE, 3.0)


func _draw_locked() -> void:
	for r in range(ROWS):
		var row: Array = grid[r]
		for c in range(COLS):
			var col = row[c]
			if col == null:
				continue
			var p := _cell_pos(Vector2i(c, r))
			if settle.has(Vector2i(c, r)):
				p.y += settle[Vector2i(c, r)]
			# A whisper of breathing, so a settled stack hangs in the water
			# instead of looking frozen in place.
			var ph := float(c) * 0.90 + float(r) * 0.62
			var st := 1.0 + sin(time * 1.25 + ph) * 0.018
			_draw_bubble_shaped(p, BUBBLE_R, _tint(col), Vector2(1.0 / sqrt(st), sqrt(st)))


func _draw_trail() -> void:
	for b in trail:
		var t: float = float(b["t"])
		var k := t / 1.1
		var pos: Vector2 = b["pos"] + Vector2(0.0, -float(b["sp"]) * t)
		pos.x += sin(t * 5.5 + float(b["ph"])) * 3.5 * float(b["wob"])
		var fade := 1.0 - k
		var rr: float = float(b["r"]) * (0.6 + 0.4 * fade)
		draw_circle(pos, rr * 1.7, Color(C_BUBBLE.r, C_BUBBLE.g, C_BUBBLE.b, 0.10 * fade))
		draw_circle(pos, rr, Color(0.72, 0.93, 1.0, 0.30 * fade))
		draw_arc(pos, rr, 0.0, TAU, 12, Color(0.90, 0.98, 1.0, 0.35 * fade), 1.0)


func _draw_piece() -> void:
	if not piece_active:
		return

	# A bubble stretches along its travel as it climbs, then relaxes.
	var climbing := clampf(1.0 - rise_progress, 0.0, 1.0)
	var st := 1.0 + SQUASH_MAX * (0.30 + 0.70 * climbing)
	st *= 1.0 + sin(time * 4.2 + piece_phase) * 0.035
	var squash := Vector2(1.0 / sqrt(st), sqrt(st))

	# Free-floating sway: the formation drifts as it rises rather than
	# tracking a fixed lane, and each bubble bobs on its own phase.
	var sway := sin(time * SWAY_FREQ + piece_phase) * SWAY_AMP
	var targets := _piece_positions()
	var ease_t := smoothstep(0.0, 1.0, rot_t)

	for i in targets.size():
		var p: Vector2 = targets[i]
		if ease_t < 1.0 and i < rot_from.size():
			p = (rot_from[i] as Vector2).lerp(p, ease_t)
		p += piece_from
		p.x += sway + sin(time * 2.7 + float(i) * 1.9 + piece_phase) * 1.6
		p.y += sin(time * 2.2 + float(i) * 1.3 + piece_phase) * BOB_AMP
		var kind: int = piece_types.get(piece_offsets[i], TYPE_MASS)
		_draw_bubble_shaped(p, BUBBLE_R, _tint(kind), squash)


# --- Lake Ellem -------------------------------------------------------------

func _draw_lake() -> void:
	var r := _lake_rect()
	var pulse := 1.0 + lake_pulse * 0.06

	for i in range(4, 0, -1):
		var k := float(i)
		draw_colored_polygon(
			_round_pts(Rect2(r.position - Vector2(k * 9.0, k * 9.0), r.size + Vector2(k * 18.0, k * 18.0)), 78.0 + k * 9.0),
			Color(C_LAKE_RIM.r, C_LAKE_RIM.g, C_LAKE_RIM.b, 0.035))

	draw_colored_polygon(_round_pts(r, 78.0), C_LAKE)
	var low := Rect2(r.position + Vector2(0.0, r.size.y * 0.30), Vector2(r.size.x, r.size.y * 0.70))
	draw_colored_polygon(_round_pts(low, 66.0), Color(0.03, 0.25, 0.56, 0.55))
	draw_polyline(_round_pts(r, 78.0), C_LAKE_RIM, 3.0)

	# Wavy water line near the surface of the basin.
	var wl_y := r.position.y + r.size.y * 0.11
	var wl := PackedVector2Array()
	for i in range(29):
		var t := float(i) / 28.0
		wl.append(Vector2(
			r.position.x + 10.0 + t * (r.size.x - 20.0),
			wl_y + sin(t * TAU * 2.2 + time * 1.4) * 5.0))
	draw_polyline(wl, Color(0.78, 0.97, 1.0, 0.40), 2.0)

	# Slow ripples across the lake.
	for i in 4:
		var fi := float(i)
		var a := 0.050 + 0.030 * sin(time * 1.3 + fi)
		if a <= 0.0:
			continue
		var hw := r.size.x * (0.34 - fi * 0.045)
		if hw <= 1.0:
			continue
		_ellipse(
			Vector2(r.position.x + r.size.x * 0.5, r.position.y + r.size.y * (0.40 + fi * 0.14)),
			hw, 8.0 + fi * 2.0, Color(0.85, 0.98, 1.0, a), 30)

	_draw_air_bubble(pulse)
	_draw_lake_text()


func _draw_air_bubble(pulse: float) -> void:
	if burst_t >= 0.0:
		# The pop: the great bubble swells, loses hold of itself, and throws a
		# shockwave out across the lake.
		var u := clampf(burst_t / BURST_TIME, 0.0, 1.0)
		var fade := 1.0 - u
		draw_circle(AIR_CENTER, AIR_R * (1.0 + 1.30 * u), Color(0.70, 0.94, 1.0, 0.36 * fade))
		draw_arc(AIR_CENTER, AIR_R * (1.0 + 1.20 * u), 0.0, TAU, 64, Color(0.94, 1.0, 1.0, 0.95 * fade), 4.0)
		for i in 3:
			var ru := clampf(u - float(i) * 0.14, 0.0, 1.0)
			if ru <= 0.0 or ru >= 1.0:
				continue
			draw_arc(AIR_CENTER, AIR_R * (0.9 + 1.6 * ru), 0.0, TAU, 56,
				Color(1.0, 0.86, 0.42, 0.60 * (1.0 - ru)), 3.0)
		return
	var r := AIR_R * pulse
	draw_circle(AIR_CENTER, r * 1.24, Color(0.55, 0.92, 1.0, 0.055))
	draw_circle(AIR_CENTER, r * 1.11, Color(0.62, 0.94, 1.0, 0.070))
	draw_circle(AIR_CENTER, r, C_GLASS)
	draw_circle(AIR_CENTER, r * 0.80, Color(0.90, 0.98, 1.0, 0.100))
	draw_arc(AIR_CENTER, r, 0.0, TAU, 64, Color(0.86, 0.99, 1.0, 0.850), 3.0)
	draw_arc(AIR_CENTER, r * 0.94, 0.0, TAU, 64, Color(0.45, 0.85, 1.0, 0.400), 1.5)
	draw_circle(AIR_CENTER + Vector2(-r * 0.38, -r * 0.42), r * 0.20, Color(1.0, 1.0, 1.0, 0.32))
	draw_circle(AIR_CENTER + Vector2(-r * 0.26, -r * 0.30), r * 0.09, Color(1.0, 1.0, 1.0, 0.28))
	draw_arc(AIR_CENTER, r * 0.78, 0.40, PI - 0.40, 30, Color(0.88, 0.99, 1.0, 0.200), 2.0)


func _draw_lake_text() -> void:
	if burst_t >= 0.0:
		# The number went down with the bubble.
		return
	var font := ThemeDB.fallback_font
	if font == null:
		return
	var r := _lake_rect()

	var title := "LAKE ELLEM"
	var tsize := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22)
	draw_string(font, Vector2(AIR_CENTER.x - tsize.x * 0.5, r.position.y - 14.0),
		title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(0.76, 0.95, 1.0, 0.92))

	# The lake size, big and centred inside the great A.I.r bubble.
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


# --- seal burst -------------------------------------------------------------

func _draw_particles() -> void:
	for p in particles:
		var t: float = p["t"]
		if t < 0.0:
			continue
		# The sealed row crosses to Lake Ellem as the bubbles it actually was -
		# same colour, same shape - and only softens at the very last moment.
		var u := minf(1.0, t / TRAVEL_TIME)
		var e := u * u * (3.0 - 2.0 * u)
		var base: Vector2 = p["pos"]
		var pos: Vector2 = base.lerp(p["target"], e)
		pos.x += sin(u * PI * 1.2) * 34.0 * float(p["wob"]) * (1.0 - e)
		pos.y += sin(u * PI) * -26.0 * (1.0 - e)
		var fade: float = 1.0 if u < 0.80 else 1.0 - (u - 0.80) / 0.20
		var radius := BUBBLE_R * clampf(fade, 0.0, 1.0) * (1.0 - 0.30 * e)
		if radius > 0.5:
			_draw_bubble(pos, radius, _tint(int(p["kind"])))


func _draw_pressure() -> void:
	# The burn rate, standing between the rise column and the lake.
	var x := BOARD_LEFT + BOARD_W + 40.0
	var y := BOARD_TOP
	var w := 24.0
	var h := BOARD_H
	var k := clampf(pressure / PRESSURE_MAX, 0.0, 1.0)
	var blown := pressure >= BLOW_LINE

	draw_rect(Rect2(x - 4.0, y - 4.0, w + 8.0, h + 8.0), Color(0.02, 0.10, 0.22, 0.55))
	draw_rect(Rect2(x, y, w, h), Color(0.05, 0.18, 0.32, 0.78))
	draw_rect(Rect2(x, y, w, h), Color(0.60, 0.90, 1.0, 0.22), false, 1.5)

	for i in range(1, 10):
		var ty := y + h * (float(i) / 10.0)
		draw_line(Vector2(x, ty), Vector2(x + w, ty), Color(0.02, 0.12, 0.26, 0.40), 1.0)

	# Stored energy: cool while it is safe, hot as it nears the line.
	var fh := h * k
	if fh > 0.5:
		var top := y + h - fh
		var col := Color(0.30, 0.78, 1.0).lerp(C_ENERGY, clampf(k * 1.4, 0.0, 1.0))
		if blown:
			col = col.lerp(Color(1.0, 0.93, 0.55), 0.30 + 0.30 * sin(time * 9.0))
		draw_rect(Rect2(x, top, w, fh), col)
		draw_rect(Rect2(x, top, w, minf(fh, 5.0)), Color(1.0, 1.0, 1.0, 0.35))

	# The blow line. Past it the top of the gauge is the fuse: ten ticks, one per
	# red bubble, and the tenth one bursts the lake.
	var by := y + h * (1.0 - BLOW_LINE / PRESSURE_MAX)
	var blink := 0.55 + 0.45 * sin(time * 6.0) if blown else 0.85
	if blown:
		var danger := 0.10 + 0.08 * sin(time * 7.0)
		draw_rect(Rect2(x, y, w, by - y), Color(1.0, 0.28, 0.22, danger))
	for i in range(1, FUSE_TICKS + 1):
		var ty := by - (by - y) * (float(i) / float(FUSE_TICKS))
		draw_line(Vector2(x, ty), Vector2(x + w, ty), Color(1.0, 0.80, 0.40, 0.38), 1.0)
	draw_rect(Rect2(x - 7.0, by - 1.5, w + 14.0, 3.0), Color(1.0, 0.85, 0.35, blink))

	var font := ThemeDB.fallback_font
	if font != null:
		draw_string(font, Vector2(x - 4.0, y - 14.0), "PRESSURE", HORIZONTAL_ALIGNMENT_LEFT, -1, 13,
			Color(0.72, 0.92, 1.0, 0.90))
		var state_txt := "BURST" if blown else "SAFE"
		var state_col := Color(1.0, 0.55, 0.42, 0.95) if blown else Color(0.60, 0.90, 1.0, 0.70)
		draw_string(font, Vector2(x - 4.0, y + h + 20.0), state_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, state_col)


func _draw() -> void:
	_draw_sky()
	_draw_rays()
	_draw_seabed()
	_draw_motes()
	_draw_column()
	_draw_pressure()
	_draw_locked()
	_draw_trail()
	_draw_piece()
	_draw_lake()
	_draw_particles()

#!/usr/bin/env python3
"""
render_translucent_motherboard_grid.py
Renders the computer motherboard game chambers with:
1. High translucency (48% opacity) allowing Leo Vance's 3:32 AM phone screen notifications to shine through clearly.
2. Anti-aliased 24x36 mathematical game grid overlaid on the motherboard playfield.
3. The new Silver Metallic Processor Chip Blocks (with centered numerals) placed on the board.
4. Both Option A (Matte Black Workstation) and Option B (Classic Emerald Server) comparison.

Outputs saved to OUT_DIR and mirrored to BRAIN_DIR.
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = "/Users/georgearmah/into-the-darkness"
OUT_DIR = f"{BASE_DIR}/assets/ui/tech_explorations"
BRAIN_DIR = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"

SCALE = 2
W = 390 * SCALE
H = 844 * SCALE

# Chamber dimensions: 336x560 (at 2x: 672x1120)
CW = 336 * SCALE
CH = 560 * SCALE
CH_X0 = 27 * SCALE
CH_Y0 = 140 * SCALE
CH_X1 = CH_X0 + CW
CH_Y1 = CH_Y0 + CH

# 24x36 Playfield Grid specs (Unit scale = 14px -> 28px at 2x)
GRID_UNIT = 14 * SCALE
GRID_COLS = 24 # 24 * 28 = 672px (= CW)
GRID_ROWS = 36 # 36 * 28 = 1008px (leaves 56px at top for dropper rail/gantry)
PLAY_Y0 = CH_Y0 + (CH - GRID_ROWS * GRID_UNIT) # Start grid below dropper gantry

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, int(size * SCALE))
    except Exception:
        return ImageFont.load_default()

# Load raw source images
black_mb_path = f"{BRAIN_DIR}/motherboard_pcb_topdown_1791988126479.jpg"
emerald_mb_path = f"{BRAIN_DIR}/emerald_server_motherboard_macro_1791988135704.jpg"
black_mb_raw = Image.open(black_mb_path).convert("RGBA")
emerald_mb_raw = Image.open(emerald_mb_path).convert("RGBA")

# Load centered silver chip and titan
chip_silver_path = f"{OUT_DIR}/silver_chip_opt1_nickel_ihs_master.png"
chip_silver = Image.open(chip_silver_path).convert("RGBA")
titan_path = f"{BASE_DIR}/assets/ui/blocks/block_tier_11_154px.png"
titan_img = Image.open(titan_path).convert("RGBA")
b4_path = f"{BASE_DIR}/assets/ui/blocks/block_tier_4_56px.png"
b4_img = Image.open(b4_path).convert("RGBA") if os.path.exists(b4_path) else None

def render_translucent_motherboard_phone(mb_img, theme_title, is_green=False, mb_alpha=128):
    # 1. Base Canvas - 3:32 AM Gloom
    base = Image.new("RGBA", (W, H), (8, 10, 15, 255))
    
    # 2. Leo Vance's Phone Screen (Notifications & Status in sharp, high contrast behind chamber)
    phone_screen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_screen = ImageDraw.Draw(phone_screen)
    
    f_title = get_font(BOLD_FONT, 12)
    f_body = get_font(REG_FONT, 11)
    f_time = get_font(REG_FONT, 10)
    f_sub = get_font(MONO_FONT, 9)
    
    # Notification Card 1: Slack build alert (centered right behind the middle of chamber)
    cx0, cy0, cx1, cy1 = 36 * SCALE, 230 * SCALE, 354 * SCALE, 298 * SCALE
    d_screen.rounded_rectangle([cx0, cy0, cx1, cy1], radius=14*SCALE, fill=(28, 35, 48, 240), outline=(70, 85, 110, 200), width=1*SCALE)
    # App icon / header
    d_screen.rectangle([cx0 + 12*SCALE, cy0 + 12*SCALE, cx0 + 26*SCALE, cy0 + 26*SCALE], fill=(224, 30, 90, 255)) # Slack magenta icon
    d_screen.text((cx0 + 34*SCALE, cy0 + 12*SCALE), "SLACK • build-pipeline", fill=(240, 245, 255, 255), font=f_title)
    d_screen.text((cx1 - 58*SCALE, cy0 + 12*SCALE), "3:28 AM", fill=(160, 175, 195, 220), font=f_time)
    d_screen.text((cx0 + 12*SCALE, cy0 + 34*SCALE), "Build #4028 FAILED: NullPointerException", fill=(255, 120, 120, 255), font=f_title)
    d_screen.text((cx0 + 12*SCALE, cy0 + 50*SCALE), "CorePhysicsEngine.cpp:1442: unhandled null pointer", fill=(190, 200, 215, 240), font=f_body)
    
    # Notification Card 2: Messages from Sarah
    cy0_2, cy1_2 = cy0 + 82 * SCALE, cy1 + 82 * SCALE
    d_screen.rounded_rectangle([cx0, cy0_2, cx1, cy1_2], radius=14*SCALE, fill=(28, 35, 48, 240), outline=(70, 85, 110, 200), width=1*SCALE)
    d_screen.rectangle([cx0 + 12*SCALE, cy0_2 + 12*SCALE, cx0 + 26*SCALE, cy0_2 + 26*SCALE], fill=(52, 199, 89, 255)) # Messages green icon
    d_screen.text((cx0 + 34*SCALE, cy0_2 + 12*SCALE), "MESSAGES • Sarah", fill=(240, 245, 255, 255), font=f_title)
    d_screen.text((cx1 - 58*SCALE, cy0_2 + 12*SCALE), "3:30 AM", fill=(160, 175, 195, 220), font=f_time)
    d_screen.text((cx0 + 12*SCALE, cy0_2 + 34*SCALE), "Are you still awake looking at code? Please sleep...", fill=(225, 235, 248, 255), font=f_body)
    d_screen.text((cx0 + 12*SCALE, cy0_2 + 50*SCALE), "Your alarm goes off in less than 4 hours.", fill=(160, 175, 195, 220), font=f_body)

    # Notification Card 3: Calendar Alert
    cy0_3, cy1_3 = cy0_2 + 82 * SCALE, cy1_2 + 82 * SCALE
    d_screen.rounded_rectangle([cx0, cy0_3, cx1, cy1_3], radius=14*SCALE, fill=(28, 35, 48, 240), outline=(70, 85, 110, 200), width=1*SCALE)
    d_screen.rectangle([cx0 + 12*SCALE, cy0_3 + 12*SCALE, cx0 + 26*SCALE, cy0_3 + 26*SCALE], fill=(255, 59, 48, 255)) # Calendar red icon
    d_screen.text((cx0 + 34*SCALE, cy0_3 + 12*SCALE), "CALENDAR • Sprint Planning", fill=(240, 245, 255, 255), font=f_title)
    d_screen.text((cx1 - 58*SCALE, cy0_3 + 12*SCALE), "9:00 AM", fill=(160, 175, 195, 220), font=f_time)
    d_screen.text((cx0 + 12*SCALE, cy0_3 + 34*SCALE), "In 5h 28m: Architecture Review & Demo with VP", fill=(225, 235, 248, 255), font=f_body)

    # Composite phone screen onto base (crisp contrast so it shows through translucent motherboard)
    base = Image.alpha_composite(base, phone_screen)

    # 3. Translucent Motherboard Layer (Scaled to Chamber 336x560)
    mb_w, mb_h = mb_img.size
    target_crop_w = int(mb_h * (336.0 / 560.0))
    if target_crop_w > mb_w:
        target_crop_w = mb_w
        target_crop_h = int(mb_w * (560.0 / 336.0))
        crop_x = 0
        crop_y = (mb_h - target_crop_h) // 2
    else:
        target_crop_h = mb_h
        crop_x = (mb_w - target_crop_w) // 2
        crop_y = 0

    mb_cropped = mb_img.crop((crop_x, crop_y, crop_x + target_crop_w, crop_y + target_crop_h))
    mb_scaled = mb_cropped.resize((CW, CH), Image.Resampling.LANCZOS)

    # Create translucent mask (48% opacity = 122 alpha)
    ch_mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(ch_mask).rounded_rectangle([0, 0, CW, CH], radius=16*SCALE, fill=mb_alpha)
    mb_scaled.putalpha(ch_mask)

    ch_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ch_layer.paste(mb_scaled, (CH_X0, CH_Y0), mb_scaled)
    
    # Outer motherboard chassis bezel / retaining brackets
    d_ch = ImageDraw.Draw(ch_layer)
    bezel_col = (45, 140, 85, 255) if is_green else (80, 105, 135, 255)
    d_ch.rounded_rectangle([CH_X0, CH_Y0, CH_X1, CH_Y1], radius=16*SCALE, outline=bezel_col, width=2*SCALE)
    
    # Floor bed: Gold contact socket retention bracket
    floor_y0 = CH_Y1 - 20 * SCALE
    floor_y1 = CH_Y1 - 2 * SCALE
    d_ch.rounded_rectangle([CH_X0 + 6*SCALE, floor_y0, CH_X1 - 6*SCALE, floor_y1], radius=4*SCALE, fill=(24, 30, 42, 255), outline=(90, 110, 135, 255), width=1*SCALE)
    for px in range(int(CH_X0 + 14*SCALE), int(CH_X1 - 14*SCALE), int(8*SCALE)):
        d_ch.line([(px, floor_y0 + 3*SCALE), (px, floor_y1 - 3*SCALE)], fill=(255, 215, 0, 240), width=2*SCALE)
        d_ch.ellipse([(px-2*SCALE, floor_y0 + 2*SCALE), (px+2*SCALE, floor_y0 + 6*SCALE)], fill=(255, 240, 180, 255))
        
    base = Image.alpha_composite(base, ch_layer)

    # 4. Anti-Aliased 24x36 Game Grid Overlay Layer
    grid_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_grid = ImageDraw.Draw(grid_layer)
    
    # Grid colors: Subtle semi-transparent cyan / white
    grid_line_col = (0, 240, 255, 55) if not is_green else (0, 255, 140, 55)
    major_line_col = (0, 240, 255, 115) if not is_green else (0, 255, 140, 115)
    axis_text_col = (0, 240, 255, 160) if not is_green else (180, 255, 180, 160)
    f_grid_num = get_font(MONO_FONT, 7)

    # Draw vertical grid lines (24 columns)
    for col in range(GRID_COLS + 1):
        x = CH_X0 + col * GRID_UNIT
        is_major = (col % 6 == 0)
        col_w = 2*SCALE if is_major else 1*SCALE
        c = major_line_col if is_major else grid_line_col
        d_grid.line([(x, PLAY_Y0), (x, floor_y0)], fill=c, width=col_w)
        # Ticks and numbers along bottom
        if is_major and col < GRID_COLS:
            d_grid.text((x + 2*SCALE, floor_y0 - 14*SCALE), str(col), fill=axis_text_col, font=f_grid_num)

    # Draw horizontal grid lines (36 rows)
    for row in range(GRID_ROWS + 1):
        y = PLAY_Y0 + row * GRID_UNIT
        if y > floor_y0:
            break
        is_major = (row % 6 == 0)
        row_w = 2*SCALE if is_major else 1*SCALE
        c = major_line_col if is_major else grid_line_col
        d_grid.line([(CH_X0, y), (CH_X1, y)], fill=c, width=row_w)
        # Ticks and row numbers along left wall
        if is_major:
            d_grid.text((CH_X0 + 4*SCALE, y + 2*SCALE), str(row), fill=axis_text_col, font=f_grid_num)

    # Danger Limit Line at Row 6 (Overflow threshold)
    danger_y = PLAY_Y0 + 6 * GRID_UNIT
    d_grid.line([(CH_X0 + 4*SCALE, danger_y), (CH_X1 - 4*SCALE, danger_y)], fill=(255, 60, 75, 230), width=2*SCALE)
    f_warn = get_font(MONO_FONT, 8)
    d_grid.text((CH_X0 + 52*SCALE, danger_y - 12*SCALE), "⚠ VBUS_OVERFLOW_LIMIT // 24x36 GRID (Y=6)", fill=(255, 90, 90, 240), font=f_warn)

    base = Image.alpha_composite(base, grid_layer)

    # 5. Settled and Dropping Silver Processor Blocks
    blocks_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # Titan Monolith #11 (154x154px = 11 grid units wide, centered at bottom)
    t_w = int(154 * SCALE)
    titan_scaled = titan_img.resize((t_w, t_w), Image.Resampling.LANCZOS)
    tx = CH_X0 + (CW - t_w) // 2
    ty = floor_y0 - t_w
    blocks_layer.paste(titan_scaled, (tx, ty), titan_scaled)

    # Tier 4 Cobalt processor block (56px = 4 grid units) sitting left of Titan
    if b4_img:
        b4_w = int(56 * SCALE)
        b4_scaled = b4_img.resize((b4_w, b4_w), Image.Resampling.LANCZOS)
        blocks_layer.paste(b4_scaled, (CH_X0 + 2*GRID_UNIT, floor_y0 - b4_w), b4_scaled)

    # Dropping Silver Processor Chip #7 (80x80px = ~5.7 grid units, suspended at top)
    chip_w = int(80 * SCALE)
    chip_scaled = chip_silver.resize((chip_w, chip_w), Image.Resampling.LANCZOS)
    drop_x = CH_X0 + (CW - chip_w) // 2
    drop_y = PLAY_Y0 + 4 * GRID_UNIT
    blocks_layer.paste(chip_scaled, (drop_x, drop_y), chip_scaled)

    base = Image.alpha_composite(base, blocks_layer)

    # 6. Dropper Gantry Assembly & Crosshair Laser
    drop_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_d = ImageDraw.Draw(drop_layer)
    rail_y = CH_Y0 + 28 * SCALE
    rail_x0 = CH_X0 + 16 * SCALE
    rail_x1 = CH_X1 - 16 * SCALE
    d_d.rounded_rectangle([rail_x0, rail_y, rail_x1, rail_y + 8*SCALE], radius=4*SCALE, fill=(35, 44, 56, 255), outline=(90, 110, 135, 255), width=1*SCALE)
    d_d.line([(rail_x0+4*SCALE, rail_y+4*SCALE), (rail_x1-4*SCALE, rail_y+4*SCALE)], fill=(225, 235, 248, 255), width=2*SCALE)

    spigot_x = W // 2
    head_w = 44 * SCALE
    head_h = 24 * SCALE
    hx0 = spigot_x - head_w // 2
    hy0 = rail_y - 6 * SCALE
    hx1 = spigot_x + head_w // 2
    hy1 = hy0 + head_h
    d_d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=6*SCALE, fill=(24, 30, 42, 255), outline=(100, 120, 145, 255), width=2*SCALE)
    d_d.rectangle([spigot_x - 6*SCALE, hy1, spigot_x + 6*SCALE, hy1 + 10*SCALE], fill=(190, 200, 215, 255))
    d_d.text((hx0 + 6*SCALE, hy0 + 6*SCALE), "SMT_PnP_A1", fill=(0, 240, 255, 240), font=get_font(MONO_FONT, 7))

    laser_y0 = hy1 + 10 * SCALE
    laser_y1 = drop_y
    d_d.line([(spigot_x, laser_y0), (spigot_x, laser_y1)], fill=(0, 240, 255, 170), width=2*SCALE)
    d_d.ellipse([(spigot_x - 8*SCALE, laser_y1 - 8*SCALE), (spigot_x + 8*SCALE, laser_y1 + 8*SCALE)], outline=(0, 240, 255, 220), width=1*SCALE)
    d_d.line([(spigot_x - 12*SCALE, laser_y1), (spigot_x + 12*SCALE, laser_y1)], fill=(0, 240, 255, 240), width=1*SCALE)
    d_d.line([(spigot_x, laser_y1 - 12*SCALE), (spigot_x, laser_y1 + 12*SCALE)], fill=(0, 240, 255, 240), width=1*SCALE)

    base = Image.alpha_composite(base, drop_layer)

    # 7. Motherboard Telemetry HUD Header & Controls
    hud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_hud = ImageDraw.Draw(hud)
    hud_y0 = 56 * SCALE
    hud_y1 = 124 * SCALE
    d_hud.rounded_rectangle([CH_X0, hud_y0, CH_X1, hud_y1], radius=10*SCALE, fill=(16, 22, 30, 245), outline=(55, 70, 90, 255), width=1*SCALE)
    d_hud.text((CH_X0 + 16*SCALE, hud_y0 + 10*SCALE), theme_title, fill=(245, 248, 255, 255), font=get_font(BOLD_FONT, 12))
    
    d_hud.text((CH_X0 + 16*SCALE, hud_y0 + 34*SCALE), "BUS_CLK", fill=(140, 155, 175, 200), font=get_font(MONO_FONT, 8))
    d_hud.text((CH_X0 + 16*SCALE, hud_y0 + 46*SCALE), "4.80 GHz", fill=(0, 240, 255, 255), font=get_font(MONO_FONT, 11))
    
    d_hud.text((CH_X0 + 105*SCALE, hud_y0 + 34*SCALE), "VCC_CORE", fill=(140, 155, 175, 200), font=get_font(MONO_FONT, 8))
    d_hud.text((CH_X0 + 105*SCALE, hud_y0 + 46*SCALE), "1.248 V", fill=(255, 215, 0, 255), font=get_font(MONO_FONT, 11))
    
    d_hud.text((CH_X0 + 195*SCALE, hud_y0 + 34*SCALE), "SILICON_PURITY", fill=(140, 155, 175, 200), font=get_font(MONO_FONT, 8))
    d_hud.text((CH_X0 + 195*SCALE, hud_y0 + 46*SCALE), "98.4 %", fill=(0, 255, 136, 255), font=get_font(MONO_FONT, 11))

    # Phone status bar
    d_hud.text((36*SCALE, 24*SCALE), "3:32", fill=(230, 235, 245, 220), font=get_font(REG_FONT, 11))
    d_hud.text((W - 80*SCALE, 24*SCALE), "14% 🪫", fill=(255, 80, 80, 220), font=get_font(REG_FONT, 11))

    # SWAP Button
    ctrl_y0 = CH_Y1 + 18 * SCALE
    btn_w = 64 * SCALE
    btn_cx = W // 2
    bx0 = btn_cx - btn_w // 2
    by0 = ctrl_y0
    bx1 = btn_cx + btn_w // 2
    by1 = by0 + btn_w
    d_hud.ellipse([(bx0 - 6*SCALE, by0 - 6*SCALE), (bx1 + 6*SCALE, by1 + 6*SCALE)], outline=(212, 175, 55, 180), width=2*SCALE)
    d_hud.ellipse([(bx0, by0), (bx1, by1)], fill=(25, 32, 42, 255), outline=(80, 100, 125, 255), width=2*SCALE)
    d_hud.ellipse([(bx0 + 6*SCALE, by0 + 6*SCALE), (bx1 - 6*SCALE, by1 - 6*SCALE)], outline=(255, 0, 127, 240), width=3*SCALE)
    f_sw = get_font(BOLD_FONT, 12)
    sbox = d_hud.textbbox((0, 0), "SWAP", font=f_sw)
    sw = sbox[2] - sbox[0]
    sh = sbox[3] - sbox[1]
    d_hud.text((btn_cx - sw//2, by0 + btn_w//2 - sh//2 - 2*SCALE), "SWAP", fill=(255, 240, 250, 255), font=f_sw)

    # Phone chassis
    d_hud.rounded_rectangle([8*SCALE, 8*SCALE, W - 8*SCALE, H - 8*SCALE], radius=44*SCALE, outline=(40, 50, 65, 255), width=2*SCALE)

    base = Image.alpha_composite(base, hud)
    return base

print("1. Rendering Translucent Black Motherboard with Grid Overlay...")
mb_black_grid = render_translucent_motherboard_phone(black_mb_raw, "FALLING // MATTE BLACK MOTHERBOARD", is_green=False, mb_alpha=124)
out_b = f"{OUT_DIR}/translucent_motherboard_black_grid.png"
mb_black_grid.save(out_b, "PNG")
mb_black_grid.save(f"{BRAIN_DIR}/translucent_motherboard_black_grid.png", "PNG")

print("2. Rendering Translucent Emerald Motherboard with Grid Overlay...")
mb_green_grid = render_translucent_motherboard_phone(emerald_mb_raw, "FALLING // EMERALD SERVER MOTHERBOARD", is_green=True, mb_alpha=124)
out_g = f"{OUT_DIR}/translucent_motherboard_emerald_grid.png"
mb_green_grid.save(out_g, "PNG")
mb_green_grid.save(f"{BRAIN_DIR}/translucent_motherboard_emerald_grid.png", "PNG")

# Compose side-by-side presentation sheet
print("3. Composing Translucent Motherboard Grid Showcase...")
sw = 1440
sh = 960
sheet = Image.new("RGBA", (sw, sh), (8, 11, 16, 255))
d_s = ImageDraw.Draw(sheet)

d_s.text((40, 24), "TRANSLUCENT MOTHERBOARD CHAMBER WITH 24x36 GAME GRID OVERLAY", fill=(245, 248, 255, 255), font=ImageFont.truetype(BOLD_FONT, 24))
d_s.text((40, 58), "Motherboard at 48% opacity: Leo Vance's 3:32 AM phone notifications clearly visible behind the board · 24x36 mathematical grid", fill=(130, 145, 165, 255), font=ImageFont.truetype(REG_FONT, 13))

fit_h = 810
r = float(fit_h) / H
fit_w = int(W * r)

m1 = mb_black_grid.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
m2 = mb_green_grid.resize((fit_w, fit_h), Image.Resampling.LANCZOS)

sheet.paste(m1, (120, 105), m1)
sheet.paste(m2, (120 + fit_w + 80, 105), m2)

f_lbl = ImageFont.truetype(BOLD_FONT, 13)
lbl1 = "OPTION A: TRANSLUCENT BLACK MOTHERBOARD (GRID ON)"
lbl2 = "OPTION B: TRANSLUCENT EMERALD SERVER (GRID ON)"

bb1 = d_s.textbbox((0, 0), lbl1, font=f_lbl)
w1 = bb1[2] - bb1[0]
bb2 = d_s.textbbox((0, 0), lbl2, font=f_lbl)
w2 = bb2[2] - bb2[0]

d_s.text((120 + (fit_w - w1)//2, 925), lbl1, fill=(0, 240, 255, 255), font=f_lbl)
d_s.text((120 + fit_w + 80 + (fit_w - w2)//2, 925), lbl2, fill=(0, 255, 136, 255), font=f_lbl)

# Right-side callout for Centered Silver Chip & Grid specs
cx_box = 120 + 2 * fit_w + 140
if cx_box + 220 < sw:
    d_s.rounded_rectangle([cx_box, 130, cx_box + 220, 560], radius=14, fill=(16, 21, 29, 255), outline=(35, 45, 60, 255), width=1)
    d_s.text((cx_box + 16, 148), "CENTERED SILVER CHIP", fill=(240, 245, 255, 255), font=ImageFont.truetype(BOLD_FONT, 12))
    d_s.text((cx_box + 16, 168), "Optical Ink Center Fixed", fill=(212, 175, 55, 255), font=ImageFont.truetype(MONO_FONT, 9))
    
    c_prev = chip_silver.resize((180, 180), Image.Resampling.LANCZOS)
    sheet.paste(c_prev, (cx_box + 20, 190), c_prev)
    
    d_s.text((cx_box + 16, 385), "GRID & TRANSLUCENCY:", fill=(0, 240, 255, 255), font=ImageFont.truetype(BOLD_FONT, 11))
    d_s.text((cx_box + 16, 408), "• 24×36 playfield grid\n• 14px per unit scale\n• Major axes every 6 cells\n• 48% motherboard alpha\n• Phone alerts clearly\n  readable underneath", fill=(140, 155, 175, 255), font=ImageFont.truetype(REG_FONT, 11))

showcase_out = f"{OUT_DIR}/translucent_motherboard_grid_showcase.png"
sheet.save(showcase_out, "PNG")
sheet.save(f"{BRAIN_DIR}/translucent_motherboard_grid_showcase.png", "PNG")
print(f"✓ Saved Translucent Motherboard Grid Showcase to {showcase_out}")

#!/usr/bin/env python3
"""
render_circuit_board_chamber.py
Generates a complete visual prototype of the Circuit Board (PCB / Motherboard) Chamber
with Processor Chip Game Blocks for Falling (Into The Darkness).

Outputs:
- assets/ui/tech_explorations/circuit_board_chamber_preview.png
- assets/ui/tech_explorations/silicon_theme_complete_presentation.png
- Mirrored to brain directory for Antigravity UI chat rendering.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = "/Users/georgearmah/into-the-darkness/assets/ui/tech_explorations"
BRAIN_DIR = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

# Screen Dimensions (iPhone 390x844 scaled 2x for retina sharpness: 780x1688)
SCALE = 2
W = 390 * SCALE
H = 844 * SCALE

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, int(size * SCALE))
    except Exception:
        return ImageFont.load_default()

print("Rendering Circuit Board Chamber Prototype (Polished)...")

# 1. Base Canvas - 3:32 AM Bedroom Gloom (Pure Opaque Solid Canvas)
base = Image.new("RGBA", (W, H), (10, 12, 16, 255))
d_base = ImageDraw.Draw(base)

# Soft radial vignetting / glow layer
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_glow = ImageDraw.Draw(glow_layer)
d_glow.ellipse([(W//2 - 280*SCALE, H//2 - 380*SCALE), (W//2 + 280*SCALE, H//2 + 380*SCALE)], fill=(18, 28, 42, 120))
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(80 * SCALE))
base = Image.alpha_composite(base, glow_layer)

# Phone chassis outline (iPhone 14 frame)
phone_pad = 8 * SCALE
d_base = ImageDraw.Draw(base)
d_base.rounded_rectangle([phone_pad, phone_pad, W - phone_pad, H - phone_pad], radius=44*SCALE, outline=(35, 45, 58, 255), width=2*SCALE)

# 2. Leo Vance's 3:32 AM Phone Notifications (Blurred Reality Layer behind chamber)
notif_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_notif = ImageDraw.Draw(notif_layer)

f_notif_title = get_font(BOLD_FONT, 12)
f_notif_body = get_font(REG_FONT, 11)
f_notif_time = get_font(REG_FONT, 10)

# Card 1: Slack alert
cx0, cy0, cx1, cy1 = 36 * SCALE, 270 * SCALE, 354 * SCALE, 334 * SCALE
d_notif.rounded_rectangle([cx0, cy0, cx1, cy1], radius=12*SCALE, fill=(32, 40, 52, 210), outline=(70, 85, 105, 160), width=1*SCALE)
d_notif.text((cx0 + 14*SCALE, cy0 + 10*SCALE), "SLACK • build-pipeline", fill=(220, 225, 235, 220), font=f_notif_title)
d_notif.text((cx1 - 56*SCALE, cy0 + 10*SCALE), "3:28 AM", fill=(140, 150, 165, 180), font=f_notif_time)
d_notif.text((cx0 + 14*SCALE, cy0 + 28*SCALE), "Build #4028 failed: NullPointerException in CoreEngine", fill=(170, 180, 195, 200), font=f_notif_body)

# Card 2: Message from Sarah
cy0_2, cy1_2 = cy0 + 78 * SCALE, cy1 + 78 * SCALE
d_notif.rounded_rectangle([cx0, cy0_2, cx1, cy1_2], radius=12*SCALE, fill=(32, 40, 52, 210), outline=(70, 85, 105, 160), width=1*SCALE)
d_notif.text((cx0 + 14*SCALE, cy0_2 + 10*SCALE), "MESSAGES • Sarah", fill=(220, 225, 235, 220), font=f_notif_title)
d_notif.text((cx1 - 56*SCALE, cy0_2 + 10*SCALE), "3:30 AM", fill=(140, 150, 165, 180), font=f_notif_time)
d_notif.text((cx0 + 14*SCALE, cy0_2 + 28*SCALE), "Are you still awake looking at code? Please go to sleep...", fill=(170, 180, 195, 200), font=f_notif_body)

# Blur the notification layer to simulate depth of field behind the chamber
notif_layer = notif_layer.filter(ImageFilter.GaussianBlur(6 * SCALE))
base = Image.alpha_composite(base, notif_layer)

# 3. Chamber Plate Layer (Circuit Board / PCB Motherboard)
# Chamber is 336x560 at (27, 140) in 390x844 space
ch_x0 = 27 * SCALE
ch_y0 = 140 * SCALE
ch_w = 336 * SCALE
ch_h = 560 * SCALE
ch_x1 = ch_x0 + ch_w
ch_y1 = ch_y0 + ch_h

pcb_plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_pcb = ImageDraw.Draw(pcb_plate)

# PCB Substrate: Matte Dark FR4 Solder Mask with 38% opacity so notifications glow through softly
fr4_bg = (12, 18, 26, 215) # Deep charcoal-matte solder mask
d_pcb.rounded_rectangle([ch_x0, ch_y0, ch_x1, ch_y1], radius=16*SCALE, fill=fr4_bg)

# Outer PCB Beveled Frame / Retaining Shield
d_pcb.rounded_rectangle([ch_x0, ch_y0, ch_x1, ch_y1], radius=16*SCALE, outline=(65, 82, 102, 255), width=2*SCALE)
d_pcb.rounded_rectangle([ch_x0+2*SCALE, ch_y0+2*SCALE, ch_x1-2*SCALE, ch_y1-2*SCALE], radius=14*SCALE, outline=(24, 32, 44, 220), width=2*SCALE)

# ENIG Immersion Gold & Copper Bus Traces Routing
c_gold_trace = (212, 175, 55, 160)
c_gold_bright = (255, 215, 0, 220)

# Vertical bus traces along left and right chamber walls
for i in range(7):
    tx_left = ch_x0 + (10 + i * 4) * SCALE
    tx_right = ch_x1 - (10 + i * 4) * SCALE
    d_pcb.line([(tx_left, ch_y0 + 26*SCALE), (tx_left, ch_y1 - 24*SCALE)], fill=c_gold_trace, width=1*SCALE)
    d_pcb.line([(tx_right, ch_y0 + 26*SCALE), (tx_right, ch_y1 - 24*SCALE)], fill=c_gold_trace, width=1*SCALE)

# Diagonal 45-degree breakout traces into chamber interior
for y_break in range(int(ch_y0 + 80*SCALE), int(ch_y1 - 60*SCALE), int(76*SCALE)):
    # Left breakouts
    d_pcb.line([(ch_x0 + 34*SCALE, y_break), (ch_x0 + 54*SCALE, y_break + 20*SCALE)], fill=c_gold_trace, width=1*SCALE)
    d_pcb.line([(ch_x0 + 54*SCALE, y_break + 20*SCALE), (ch_x0 + 80*SCALE, y_break + 20*SCALE)], fill=c_gold_trace, width=1*SCALE)
    d_pcb.ellipse([(ch_x0 + 78*SCALE, y_break + 18*SCALE), (ch_x0 + 84*SCALE, y_break + 24*SCALE)], fill=c_gold_bright, outline=(20, 20, 20, 255))
    
    # Right breakouts
    d_pcb.line([(ch_x1 - 34*SCALE, y_break + 40*SCALE), (ch_x1 - 54*SCALE, y_break + 20*SCALE)], fill=c_gold_trace, width=1*SCALE)
    d_pcb.line([(ch_x1 - 54*SCALE, y_break + 20*SCALE), (ch_x1 - 80*SCALE, y_break + 20*SCALE)], fill=c_gold_trace, width=1*SCALE)
    d_pcb.ellipse([(ch_x1 - 84*SCALE, y_break + 18*SCALE), (ch_x1 - 78*SCALE, y_break + 24*SCALE)], fill=c_gold_bright, outline=(20, 20, 20, 255))

# Solder Mask Via Arrays & Test Point Rings
for vx in range(int(ch_x0 + 44*SCALE), int(ch_x1 - 44*SCALE), int(52*SCALE)):
    for vy in range(int(ch_y0 + 70*SCALE), int(ch_y1 - 50*SCALE), int(64*SCALE)):
        d_pcb.ellipse([(vx-3*SCALE, vy-3*SCALE), (vx+3*SCALE, vy+3*SCALE)], fill=c_gold_trace, outline=(15, 20, 25, 200))
        d_pcb.ellipse([(vx-1*SCALE, vy-1*SCALE), (vx+1*SCALE, vy+1*SCALE)], fill=(10, 14, 18, 255))

# Silkscreen Markings (White / Gold)
f_silk_sub = get_font(MONO_FONT, 8)
f_silk_label = get_font(MONO_FONT, 9)

c_silk = (230, 235, 245, 170)
c_silk_gold = (212, 175, 55, 200)

d_pcb.text((ch_x0 + 16*SCALE, ch_y0 + 10*SCALE), "MOTHERBOARD // U1_CORE_ARRAY", fill=c_silk, font=f_silk_label)
d_pcb.text((ch_x1 - 100*SCALE, ch_y0 + 10*SCALE), "REV 4.2 • ENIG-30u", fill=c_silk, font=f_silk_sub)

d_pcb.text((ch_x0 + 16*SCALE, ch_y1 - 24*SCALE), "LGA_CHAMBER_BUS // 64-BIT DUAL CHANNEL", fill=c_silk, font=f_silk_sub)
d_pcb.text((ch_x1 - 92*SCALE, ch_y1 - 24*SCALE), "VCC_CORE: 1.25V", fill=c_silk_gold, font=f_silk_sub)

# Technical crosshair fiducial marks on 4 corners of PCB
fid_coords = [
    (ch_x0 + 20*SCALE, ch_y0 + 26*SCALE),
    (ch_x1 - 20*SCALE, ch_y0 + 26*SCALE),
    (ch_x0 + 20*SCALE, ch_y1 - 36*SCALE),
    (ch_x1 - 20*SCALE, ch_y1 - 36*SCALE)
]
for fx, fy in fid_coords:
    d_pcb.ellipse([(fx-4*SCALE, fy-4*SCALE), (fx+4*SCALE, fy+4*SCALE)], outline=c_gold_bright, width=1*SCALE)
    d_pcb.line([(fx-7*SCALE, fy), (fx+7*SCALE, fy)], fill=c_gold_bright, width=1*SCALE)
    d_pcb.line([(fx, fy-7*SCALE), (fx, fy+7*SCALE)], fill=c_gold_bright, width=1*SCALE)

# 4. Overflow Danger Limit Line (High Voltage Hazard Trace)
danger_y = ch_y0 + 96 * SCALE
d_pcb.line([(ch_x0 + 8*SCALE, danger_y), (ch_x1 - 8*SCALE, danger_y)], fill=(235, 50, 65, 230), width=2*SCALE)
d_pcb.line([(ch_x0 + 8*SCALE, danger_y+3*SCALE), (ch_x1 - 8*SCALE, danger_y+3*SCALE)], fill=(120, 20, 30, 160), width=1*SCALE)

# Danger warning silkscreen
f_warn = get_font(MONO_FONT, 8)
d_pcb.text((ch_x0 + 58*SCALE, danger_y - 12*SCALE), "⚠ VBUS_OVERVOLTAGE_LIMIT // BUFFER OVERFLOW", fill=(255, 90, 90, 220), font=f_warn)

# 5. Floor Bed (LGA Socket Contact Retention Bracket)
floor_y0 = ch_y1 - 16 * SCALE
floor_y1 = ch_y1 - 2 * SCALE
# Socket bracket background
d_pcb.rounded_rectangle([ch_x0 + 6*SCALE, floor_y0, ch_x1 - 6*SCALE, floor_y1], radius=4*SCALE, fill=(30, 36, 46, 255), outline=(75, 88, 105, 255), width=1*SCALE)
# Gold spring pins in socket bed
for px in range(int(ch_x0 + 14*SCALE), int(ch_x1 - 14*SCALE), int(8*SCALE)):
    d_pcb.line([(px, floor_y0 + 3*SCALE), (px, floor_y1 - 3*SCALE)], fill=c_gold_bright, width=2*SCALE)
    d_pcb.ellipse([(px-2*SCALE, floor_y0 + 2*SCALE), (px+2*SCALE, floor_y0 + 6*SCALE)], fill=(255, 240, 180, 255))

base = Image.alpha_composite(base, pcb_plate)

# 6. Settled Blocks on the Board (Processor Chips)
blocks_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

# Titan Monolith (Tier 11) - 154x154px at bottom center
titan_path = f"/Users/georgearmah/into-the-darkness/assets/ui/blocks/block_tier_11_154px.png"
if os.path.exists(titan_path):
    titan_img = Image.open(titan_path).convert("RGBA")
    t_w, t_h = int(154 * SCALE), int(154 * SCALE)
    titan_scaled = titan_img.resize((t_w, t_h), Image.Resampling.LANCZOS)
    tx = (W - t_w) // 2
    ty = floor_y0 - t_h
    blocks_layer.paste(titan_scaled, (tx, ty), titan_scaled)

# Tier 4 Cobalt processor block (56px) sitting to the left of Titan
b4_path = f"/Users/georgearmah/into-the-darkness/assets/ui/blocks/block_tier_4_56px.png"
if os.path.exists(b4_path):
    b4_img = Image.open(b4_path).convert("RGBA")
    b4_w = int(56 * SCALE)
    b4_scaled = b4_img.resize((b4_w, b4_w), Image.Resampling.LANCZOS)
    blocks_layer.paste(b4_scaled, (ch_x0 + 14*SCALE, floor_y0 - b4_w), b4_scaled)

# Tier 3 Cyan processor block (42px) sitting to the right of Titan
b3_path = f"/Users/georgearmah/into-the-darkness/assets/ui/blocks/block_tier_3_42px.png"
if os.path.exists(b3_path):
    b3_img = Image.open(b3_path).convert("RGBA")
    b3_w = int(42 * SCALE)
    b3_scaled = b3_img.resize((b3_w, b3_w), Image.Resampling.LANCZOS)
    blocks_layer.paste(b3_scaled, (ch_x1 - 14*SCALE - b3_w, floor_y0 - b3_w), b3_scaled)

# Block A: Dropping Processor Block at (W//2 - 40*SCALE, ch_y0 + 110*SCALE)
chip_80_path = f"{OUT_DIR}/chip_option1_server_cpu_80px.png"
if os.path.exists(chip_80_path):
    chip_img = Image.open(chip_80_path).convert("RGBA")
    chip_scaled = chip_img.resize((80 * SCALE, 80 * SCALE), Image.Resampling.LANCZOS)
    drop_x = (W - 80 * SCALE) // 2
    drop_y = ch_y0 + 115 * SCALE
    blocks_layer.paste(chip_scaled, (drop_x, drop_y), chip_scaled)

base = Image.alpha_composite(base, blocks_layer)

# 7. Dropper Assembly: SMT Pick-and-Place Gantry & Optical Laser
dropper_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_drop = ImageDraw.Draw(dropper_layer)

rail_y = ch_y0 + 32 * SCALE
rail_x0 = ch_x0 + 16 * SCALE
rail_x1 = ch_x1 - 16 * SCALE

# Precision Linear Motion Rail
d_drop.rounded_rectangle([rail_x0, rail_y, rail_x1, rail_y + 8*SCALE], radius=4*SCALE, fill=(35, 44, 56, 255), outline=(80, 95, 115, 255), width=1*SCALE)
d_drop.line([(rail_x0+4*SCALE, rail_y+4*SCALE), (rail_x1-4*SCALE, rail_y+4*SCALE)], fill=(210, 225, 240, 255), width=2*SCALE)

# SMT Vacuum Placement Head (centered over dropping block)
spigot_x = W // 2
head_w = 44 * SCALE
head_h = 24 * SCALE
hx0 = spigot_x - head_w // 2
hy0 = rail_y - 6 * SCALE
hx1 = spigot_x + head_w // 2
hy1 = hy0 + head_h

# Placement head CNC body
d_drop.rounded_rectangle([hx0, hy0, hx1, hy1], radius=6*SCALE, fill=(24, 30, 40, 255), outline=(95, 115, 140, 255), width=2*SCALE)
# Vacuum nozzle tip
nozzle_w = 12 * SCALE
d_drop.rectangle([spigot_x - nozzle_w//2, hy1, spigot_x + nozzle_w//2, hy1 + 10*SCALE], fill=(185, 195, 210, 255))
d_drop.ellipse([(spigot_x - 4*SCALE, hy1 + 8*SCALE), (spigot_x + 4*SCALE, hy1 + 12*SCALE)], fill=(40, 50, 65, 255))

# SMT Feeder label
f_feeder = get_font(MONO_FONT, 7)
d_drop.text((hx0 + 6*SCALE, hy0 + 6*SCALE), "SMT_PnP_A1", fill=(0, 240, 255, 240), font=f_feeder)

# Optical Alignment Crosshair Laser (Cyan vertical beam down to block)
laser_y0 = hy1 + 12 * SCALE
laser_y1 = ch_y0 + 115 * SCALE

d_drop.line([(spigot_x, laser_y0), (spigot_x, laser_y1)], fill=(0, 240, 255, 50), width=6*SCALE)
d_drop.line([(spigot_x, laser_y0), (spigot_x, laser_y1)], fill=(0, 240, 255, 150), width=2*SCALE)
d_drop.line([(spigot_x, laser_y0), (spigot_x, laser_y1)], fill=(255, 255, 255, 240), width=1*SCALE)

# Optical crosshair reticle on top of chip
ret_y = laser_y1
d_drop.ellipse([(spigot_x - 8*SCALE, ret_y - 8*SCALE), (spigot_x + 8*SCALE, ret_y + 8*SCALE)], outline=(0, 240, 255, 220), width=1*SCALE)
d_drop.line([(spigot_x - 12*SCALE, ret_y), (spigot_x + 12*SCALE, ret_y)], fill=(0, 240, 255, 240), width=1*SCALE)
d_drop.line([(spigot_x, ret_y - 12*SCALE), (spigot_x, ret_y + 12*SCALE)], fill=(0, 240, 255, 240), width=1*SCALE)

base = Image.alpha_composite(base, dropper_layer)

# 8. Motherboard BIOS / Telemetry HUD Header (Top Area: y = 54 to 124)
hud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_hud = ImageDraw.Draw(hud_layer)

hud_y0 = 56 * SCALE
hud_y1 = 124 * SCALE
hud_x0 = ch_x0
hud_x1 = ch_x1

# Header enclosure
d_hud.rounded_rectangle([hud_x0, hud_y0, hud_x1, hud_y1], radius=10*SCALE, fill=(16, 22, 30, 240), outline=(50, 65, 85, 255), width=1*SCALE)

# Telemetry readouts
f_hud_title = get_font(BOLD_FONT, 13)
f_hud_val = get_font(MONO_FONT, 11)
f_hud_sub = get_font(MONO_FONT, 8)

# Brand / Title
d_hud.text((hud_x0 + 16*SCALE, hud_y0 + 10*SCALE), "FALLING // SILICON ARCHITECTURE", fill=(240, 245, 255, 240), font=f_hud_title)

# Telemetry columns
# Col 1: Core Frequency
d_hud.text((hud_x0 + 16*SCALE, hud_y0 + 34*SCALE), "BUS_CLK", fill=(140, 155, 175, 200), font=f_hud_sub)
d_hud.text((hud_x0 + 16*SCALE, hud_y0 + 46*SCALE), "4.80 GHz", fill=(0, 240, 255, 255), font=f_hud_val)

# Col 2: Core Voltage
d_hud.text((hud_x0 + 105*SCALE, hud_y0 + 34*SCALE), "VCC_CORE", fill=(140, 155, 175, 200), font=f_hud_sub)
d_hud.text((hud_x0 + 105*SCALE, hud_y0 + 46*SCALE), "1.248 V", fill=(255, 215, 0, 255), font=f_hud_val)

# Col 3: Purity / Score
d_hud.text((hud_x0 + 195*SCALE, hud_y0 + 34*SCALE), "SILICON_PURITY", fill=(140, 155, 175, 200), font=f_hud_sub)
d_hud.text((hud_x0 + 195*SCALE, hud_y0 + 46*SCALE), "98.4 %", fill=(0, 255, 136, 255), font=f_hud_val)

# Battery & Time indicator at top phone bar
f_phone_bar = get_font(REG_FONT, 11)
d_hud.text((36*SCALE, 24*SCALE), "3:32", fill=(230, 235, 245, 220), font=f_phone_bar)
d_hud.text((W - 80*SCALE, 24*SCALE), "14% 🪫", fill=(255, 80, 80, 220), font=f_phone_bar)

# 9. Bottom Interactive Controls: SMT Tactile Micro-Switch "SWAP" Button
ctrl_y0 = ch_y1 + 18 * SCALE
btn_w = 64 * SCALE
btn_h = 64 * SCALE
btn_cx = W // 2
bx0 = btn_cx - btn_w // 2
by0 = ctrl_y0
bx1 = btn_cx + btn_w // 2
by1 = by0 + btn_h

# SMT Circular Footprint with gold annular ring & trace leads
d_hud.ellipse([(bx0 - 6*SCALE, by0 - 6*SCALE), (bx1 + 6*SCALE, by1 + 6*SCALE)], outline=(212, 175, 55, 180), width=2*SCALE)
# Routing traces entering button
d_hud.line([(bx0 - 30*SCALE, by0 + btn_h//2), (bx0 - 6*SCALE, by0 + btn_h//2)], fill=(212, 175, 55, 180), width=2*SCALE)
d_hud.line([(bx1 + 6*SCALE, by0 + btn_h//2), (bx1 + 30*SCALE, by0 + btn_h//2)], fill=(212, 175, 55, 180), width=2*SCALE)

# Tactile switch metallic actuator
d_hud.ellipse([(bx0, by0), (bx1, by1)], fill=(25, 32, 42, 255), outline=(80, 100, 125, 255), width=2*SCALE)
# Inner LED ring (illuminated magenta/cyan)
d_hud.ellipse([(bx0 + 6*SCALE, by0 + 6*SCALE), (bx1 - 6*SCALE, by1 - 6*SCALE)], outline=(255, 0, 127, 240), width=3*SCALE)

# SWAP text legend
f_swap = get_font(BOLD_FONT, 12)
sbox = d_hud.textbbox((0, 0), "SWAP", font=f_swap)
sw, sh = sbox[2] - sbox[0], sbox[3] - sbox[1]
d_hud.text((btn_cx - sw//2, by0 + btn_h//2 - sh//2 - 2*SCALE), "SWAP", fill=(255, 240, 250, 255), font=f_swap)

base = Image.alpha_composite(base, hud_layer)

# Save Master High-Res and 1:1 Display Image
out_master = f"{OUT_DIR}/circuit_board_chamber_preview.png"
brain_master = f"{BRAIN_DIR}/circuit_board_chamber_preview.png"
base.save(out_master, "PNG")
base.save(brain_master, "PNG")
print(f"✓ Saved Circuit Board Chamber preview to {out_master} and {brain_master}")

# Generate a side-by-side showcase comparing the Processor Chips and the Circuit Board Chamber
showcase = Image.new("RGBA", (1440, 900), (8, 12, 18, 255))
d_s = ImageDraw.Draw(showcase)

# Title
f_head = ImageFont.truetype(BOLD_FONT, 28)
f_subhead = ImageFont.truetype(REG_FONT, 14)
d_s.text((40, 30), "FALLING — SILICON CHIP BLOCKS & CIRCUIT BOARD CHAMBER", fill=(245, 248, 255, 255), font=f_head)
d_s.text((40, 68), "Full Theme Direction: Computer Processors as Game Blocks, Motherboard PCB Chamber with Immersion Gold Traces", fill=(140, 155, 175, 255), font=f_subhead)

# Paste Chamber Preview on the Left (scaled down to fit 750h)
ch_img = Image.open(out_master).convert("RGBA")
ch_ratio = 740.0 / ch_img.height
ch_fit_w = int(ch_img.width * ch_ratio)
ch_fit_h = 740
ch_fit = ch_img.resize((ch_fit_w, ch_fit_h), Image.Resampling.LANCZOS)
showcase.paste(ch_fit, (50, 110), ch_fit)

# Paste Chip Options Showcase on the Right
chips_sheet_path = f"{OUT_DIR}/processor_chips_showcase.png"
if os.path.exists(chips_sheet_path):
    chips_sheet = Image.open(chips_sheet_path).convert("RGBA")
    # Resize to fit right panel
    target_rw = 1440 - ch_fit_w - 120
    ratio = float(target_rw) / chips_sheet.width
    rh = int(chips_sheet.height * ratio)
    chips_resized = chips_sheet.resize((target_rw, rh), Image.Resampling.LANCZOS)
    showcase.paste(chips_resized, (ch_fit_w + 80, 110), chips_resized)

# Save combined theme presentation
combo_out = f"{OUT_DIR}/silicon_theme_complete_presentation.png"
combo_brain = f"{BRAIN_DIR}/silicon_theme_complete_presentation.png"
showcase.save(combo_out, "PNG")
showcase.save(combo_brain, "PNG")
print(f"✓ Saved Complete Presentation to {combo_out} and {combo_brain}")

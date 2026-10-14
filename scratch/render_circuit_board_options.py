#!/usr/bin/env python3
"""
render_circuit_board_options.py
Renders multi-option design explorations for:
1. Circuit Board Chamber Plates (3 Options: Stealth Matte Black, Classic Emerald Green, Deep Cobalt Server)
2. Dropper Assembly (3 Options: SMT Pick-and-Place Vacuum Head, Flex Ribbon Cable, Tape-and-Reel Feeder)
3. Floor Bed & SWAP Button (3 Options for each)

Outputs saved to assets/ui/tech_explorations/ and mirrored to brain dir.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = "/Users/georgearmah/into-the-darkness/assets/ui/tech_explorations"
BRAIN_DIR = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# ==============================================================================
# SECTION 1: 3 CIRCUIT BOARD CHAMBER OPTIONS
# ==============================================================================
print("1. Rendering 3 Circuit Board Chamber Variants...")

# Chamber dimensions: 336x560
CW, CH = 336, 560

def render_chamber_plate(theme_key):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    
    if theme_key == "stealth_black":
        # Option A: Stealth Matte Black & Gold ENIG
        bg_col = (14, 18, 24, 235)
        border_col = (65, 82, 102, 255)
        trace_col = (212, 175, 55, 170)
        trace_bright = (255, 215, 0, 230)
        silk_col = (230, 235, 245, 180)
        silk_accent = (0, 240, 255, 220)
        title_text = "STEALTH MATTE BLACK // ENIG GOLD"
        sub_text = "FR4-DARK • 24K IMMERSION GOLD • ULTRA-CLEAN CONTRAST"
        
    elif theme_key == "emerald_green":
        # Option B: Classic Industrial Emerald Green PCB
        bg_col = (8, 36, 22, 235)
        border_col = (28, 90, 56, 255)
        trace_col = (220, 160, 40, 180) # Bright copper/gold
        trace_bright = (255, 190, 50, 240)
        silk_col = (240, 250, 235, 200) # Crisp white-cream silkscreen
        silk_accent = (180, 255, 120, 220)
        title_text = "CLASSIC EMERALD GREEN PCB"
        sub_text = "RETRO HARDWARE • EXPOSED COPPER BUS • SOLDER MASK"
        
    elif theme_key == "cobalt_server":
        # Option C: Deep Cobalt Server Blade PCB
        bg_col = (8, 22, 38, 235)
        border_col = (24, 75, 125, 255)
        trace_col = (70, 160, 230, 180) # Silver-tin & cyan differential traces
        trace_bright = (0, 240, 255, 240)
        silk_col = (210, 235, 255, 180)
        silk_accent = (0, 240, 255, 240)
        title_text = "DEEP COBALT SERVER BLADE PCB"
        sub_text = "HIGH-SPEED DIFFERENTIAL PAIRS • CYAN TELEMETRY"

    # Base rounded substrate
    d.rounded_rectangle([0, 0, CW, CH], radius=16, fill=bg_col, outline=border_col, width=2)
    d.rounded_rectangle([3, 3, CW-3, CH-3], radius=13, outline=(0, 0, 0, 100), width=1)
    
    # Ground plane copper hatch grid (subtle)
    for x in range(20, CW-20, 28):
        d.line([(x, 15), (x, CH-15)], fill=(bg_col[0]+8, bg_col[1]+8, bg_col[2]+8, 100), width=1)
    for y in range(20, CH-20, 28):
        d.line([(15, y), (CW-15, y)], fill=(bg_col[0]+8, bg_col[1]+8, bg_col[2]+8, 100), width=1)

    # Bus traces on left and right walls
    for i in range(7):
        lx = 10 + i * 4
        rx = CW - 10 - i * 4
        d.line([(lx, 30), (lx, CH-30)], fill=trace_col, width=1)
        d.line([(rx, 30), (rx, CH-30)], fill=trace_col, width=1)

    # Breakout traces with circular via rings
    for yb in range(90, CH-70, 68):
        # Left
        d.line([(34, yb), (54, yb+16)], fill=trace_col, width=1)
        d.line([(54, yb+16), (78, yb+16)], fill=trace_col, width=1)
        d.ellipse([(76, yb+14), (82, yb+20)], fill=trace_bright, outline=(10, 15, 20, 255))
        d.ellipse([(78, yb+16), (80, yb+18)], fill=(0, 0, 0, 255))
        # Right
        d.line([(CW-34, yb+30), (CW-54, yb+16)], fill=trace_col, width=1)
        d.line([(CW-54, yb+16), (CW-78, yb+16)], fill=trace_col, width=1)
        d.ellipse([(CW-82, yb+14), (CW-76, yb+20)], fill=trace_bright, outline=(10, 15, 20, 255))
        d.ellipse([(CW-80, yb+16), (CW-78, yb+18)], fill=(0, 0, 0, 255))

    # Via array grid across center
    for vx in range(48, CW-48, 48):
        for vy in range(65, CH-45, 58):
            d.ellipse([(vx-3, vy-3), (vx+3, vy+3)], fill=trace_col, outline=(10, 15, 20, 200))
            d.ellipse([(vx-1, vy-1), (vx+1, vy+1)], fill=(5, 8, 12, 255))

    # Silkscreen technical typography
    f_title = get_font(BOLD_FONT, 9)
    f_sub = get_font(MONO_FONT, 7)
    
    d.text((16, 12), title_text, fill=silk_col, font=f_title)
    d.text((CW - 80, 13), "REV 4.2", fill=silk_accent, font=f_sub)
    d.text((16, CH - 22), sub_text, fill=silk_col, font=f_sub)
    
    # Corner fiducial markers
    for fx, fy in [(18, 26), (CW-18, 26), (18, CH-26), (CW-18, CH-26)]:
        d.ellipse([(fx-4, fy-4), (fx+4, fy+4)], outline=trace_bright, width=1)
        d.line([(fx-6, fy), (fx+6, fy)], fill=trace_bright, width=1)
        d.line([(fx, fy-6), (fx, fy+6)], fill=trace_bright, width=1)
        d.ellipse([(fx-1, fy-1), (fx+1, fy+1)], fill=trace_bright)

    return im

# Render all 3 chamber variants
ch_black = render_chamber_plate("stealth_black")
ch_green = render_chamber_plate("emerald_green")
ch_cobalt = render_chamber_plate("cobalt_server")

ch_black.save(f"{OUT_DIR}/chamber_option_a_stealth_black.png")
ch_green.save(f"{OUT_DIR}/chamber_option_b_emerald_green.png")
ch_cobalt.save(f"{OUT_DIR}/chamber_option_c_cobalt_server.png")

# Mirror to brain
ch_black.save(f"{BRAIN_DIR}/chamber_option_a_stealth_black.png")
ch_green.save(f"{BRAIN_DIR}/chamber_option_b_emerald_green.png")
ch_cobalt.save(f"{BRAIN_DIR}/chamber_option_c_cobalt_server.png")

# Compose 3-Chamber Comparison Sheet
sw = 1200
sh = 680
sheet_chambers = Image.new("RGBA", (sw, sh), (8, 11, 16, 255))
d_sc = ImageDraw.Draw(sheet_chambers)

f_h1 = get_font(BOLD_FONT, 24)
f_lead = get_font(REG_FONT, 13)
d_sc.text((36, 24), "CIRCUIT BOARD GAME CHAMBER — 3 BOARD AESTHETIC OPTIONS", fill=(240, 245, 255, 255), font=f_h1)
d_sc.text((36, 58), "Exact 336x560px chamber dimensions · Solder mask & immersion trace comparisons · Semi-translucent FR4 substrate", fill=(130, 145, 165, 255), font=f_lead)

# Paste the 3 chambers
opts = [
    ("OPTION A: STEALTH MATTE BLACK", ch_black, "Apple / Enterprise stealth look · 24K ENIG Gold · Max contrast with phone text"),
    ("OPTION B: INDUSTRIAL EMERALD GREEN", ch_green, "Classic electronics PCB · Exposed copper bus traces · Warm tactile tech vibe"),
    ("OPTION C: DEEP COBALT SERVER BLADE", ch_cobalt, "Workstation blade aesthetic · High-speed differential routing · Cyan LED accents")
]

card_w = 360
card_h = 580
start_x = 36
gap = 24

for idx, (opt_title, opt_img, opt_desc) in enumerate(opts):
    cx = start_x + idx * (card_w + gap)
    cy = 90
    
    # Card backing
    d_sc.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=14, fill=(16, 20, 28, 255), outline=(35, 45, 60, 255), width=1)
    
    # Chamber image centered in card (scale slightly to fit nicely)
    fit_w = 320
    ratio = fit_w / CW
    fit_h = int(CH * ratio)
    scaled_ch = opt_img.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
    sheet_chambers.paste(scaled_ch, (cx + (card_w - fit_w)//2, cy + 38), scaled_ch)
    
    # Title & description
    f_opt = get_font(BOLD_FONT, 12)
    f_desc = get_font(REG_FONT, 10)
    d_sc.text((cx + 18, cy + 14), opt_title, fill=(0, 240, 255, 255) if idx==0 else (240, 245, 255, 240), font=f_opt)
    d_sc.text((cx + 18, cy + card_h - 24), opt_desc, fill=(140, 155, 175, 255), font=f_desc)

chambers_showcase = f"{OUT_DIR}/circuit_board_chambers_showcase.png"
sheet_chambers.save(chambers_showcase, "PNG")
sheet_chambers.save(f"{BRAIN_DIR}/circuit_board_chambers_showcase.png", "PNG")
print(f"✓ Saved Chamber 3-Way Showcase to {chambers_showcase}")


# ==============================================================================
# SECTION 2: 3 OPTIONS FOR EACH SUPPORTING ELEMENT
# (Droppers, Floor Sockets, SWAP Buttons)
# ==============================================================================
print("2. Rendering 3 Options for Dropper, Floor Socket, and SWAP Button...")

# Dimensions for elements:
# Dropper Gantry: 340 x 70
# Floor Socket: 340 x 50
# SWAP Button: 90 x 90

dw, dh = 340, 70
fw, fh = 340, 48
bw, bh = 80, 80

# -----------------
# DROPPERS (3 Options)
# -----------------
# Dropper 1: SMT Pick-and-Place Vacuum Nozzle
drop1 = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
d1 = ImageDraw.Draw(drop1)
# Linear guide rail
d1.rounded_rectangle([10, 16, dw-10, 24], radius=4, fill=(35, 42, 52, 255), outline=(75, 88, 105, 255), width=1)
d1.line([(14, 20), (dw-14, 20)], fill=(210, 225, 240, 255), width=2)
# Carriage
cx = dw // 2
d1.rounded_rectangle([cx-24, 8, cx+24, 34], radius=5, fill=(24, 30, 40, 255), outline=(90, 110, 135, 255), width=2)
# Vacuum nozzle
d1.rectangle([cx-6, 34, cx+6, 46], fill=(180, 190, 205, 255))
d1.ellipse([(cx-4, 44), (cx+4, 48)], fill=(30, 40, 50, 255))
# Laser crosshair
d1.line([(cx, 48), (cx, 68)], fill=(0, 240, 255, 220), width=2)
d1.line([(cx-8, 64), (cx+8, 64)], fill=(0, 240, 255, 220), width=1)
f_s = get_font(MONO_FONT, 7)
d1.text((cx-20, 14), "SMT_PnP", fill=(0, 240, 255, 240), font=f_s)

# Dropper 2: Polyimide Flexible Ribbon Cable (FFC) Carriage
drop2 = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
d2 = ImageDraw.Draw(drop2)
# Overhead gold rail
d2.rounded_rectangle([10, 14, dw-10, 22], radius=4, fill=(28, 24, 20, 255), outline=(120, 95, 40, 255), width=1)
d2.line([(14, 18), (dw-14, 18)], fill=(220, 180, 60, 255), width=2)
# Hanging amber flex cable loops
cx = dw // 2
for x in range(cx-18, cx+20, 6):
    d2.line([(x, 22), (x, 38)], fill=(180, 110, 20, 255), width=2)
    d2.line([(x+1, 22), (x+1, 38)], fill=(240, 180, 50, 220), width=1)
# Socket clamp
d2.rounded_rectangle([cx-26, 36, cx+26, 52], radius=4, fill=(38, 30, 24, 255), outline=(180, 130, 45, 255), width=1)
d2.rectangle([cx-8, 52, cx+8, 62], fill=(212, 175, 55, 255))
d2.text((cx-22, 40), "FFC_BUS", fill=(255, 215, 0, 240), font=f_s)

# Dropper 3: Industrial Tape-and-Reel Chip Cassette
drop3 = Image.new("RGBA", (dw, dh), (0, 0, 0, 0))
d3 = ImageDraw.Draw(drop3)
# Cassette feeder housing
d3.rounded_rectangle([10, 12, dw-10, 30], radius=4, fill=(25, 28, 35, 255), outline=(60, 70, 85, 255), width=1)
# Perforated tape holes
for x in range(20, dw-20, 14):
    d3.ellipse([(x, 18), (x+5, 23)], fill=(12, 15, 20, 255), outline=(50, 60, 75, 255))
# Dispenser shuttle
cx = dw // 2
d3.rounded_rectangle([cx-28, 22, cx+28, 48], radius=6, fill=(40, 46, 58, 255), outline=(110, 130, 160, 255), width=2)
d3.rectangle([cx-12, 48, cx+12, 60], fill=(20, 24, 32, 255), outline=(0, 240, 255, 200), width=1)
d3.text((cx-24, 28), "FEEDER_8mm", fill=(200, 220, 245, 220), font=f_s)


# -----------------
# FLOOR SOCKETS (3 Options)
# -----------------
# Floor 1: Gold-Plated LGA Spring Pin Bed
floor1 = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
df1 = ImageDraw.Draw(floor1)
df1.rounded_rectangle([10, 8, fw-10, fh-8], radius=6, fill=(24, 30, 40, 255), outline=(65, 80, 100, 255), width=1)
for px in range(22, fw-22, 8):
    df1.line([(px, 16), (px, fh-16)], fill=(255, 215, 0, 240), width=2)
    df1.ellipse([(px-2, 13), (px+2, 17)], fill=(255, 240, 170, 255))
f_fl = get_font(MONO_FONT, 7)
df1.text((18, fh-14), "LGA_SOCKET_BED // SPRING-LOADED GOLD CONTACTS", fill=(212, 175, 55, 220), font=f_fl)

# Floor 2: Heavy-Duty Server PCIe Edge Slot
floor2 = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
df2 = ImageDraw.Draw(floor2)
df2.rounded_rectangle([10, 6, fw-10, fh-6], radius=4, fill=(18, 22, 28, 255), outline=(55, 65, 80, 255), width=2)
# Side retention latches
df2.rectangle([10, 4, 24, fh-4], fill=(70, 85, 105, 255))
df2.rectangle([fw-24, 4, fw-10, fh-4], fill=(70, 85, 105, 255))
# Gold fingers
for px in range(32, fw-32, 6):
    df2.rectangle([px, 12, px+3, fh-14], fill=(220, 180, 50, 240))
df2.text((36, fh-12), "PCIe_GEN5 // CARD-EDGE RETENTION SLOT", fill=(200, 215, 235, 200), font=f_fl)

# Floor 3: Zero Insertion Force (ZIF) Clamping Rail
floor3 = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
df3 = ImageDraw.Draw(floor3)
df3.rounded_rectangle([10, 10, fw-10, fh-10], radius=8, fill=(32, 38, 48, 255), outline=(85, 105, 130, 255), width=1)
# Silver lever arm on left
df3.line([(16, fh//2), (36, fh//2)], fill=(220, 230, 245, 255), width=4)
df3.ellipse([(34, fh//2-4), (42, fh//2+4)], fill=(255, 80, 80, 255))
# Gold contact pads
for px in range(48, fw-24, 10):
    df3.rounded_rectangle([px, 16, px+6, fh-16], radius=2, fill=(212, 175, 55, 255))
df3.text((54, fh-14), "ZIF_CLAMP // MECHANICAL RETENTION BUS", fill=(180, 200, 225, 200), font=f_fl)


# -----------------
# SWAP BUTTONS (3 Options)
# -----------------
# Button 1: SMT Tactile Micro-Switch with LED Halo
btn1 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
db1 = ImageDraw.Draw(btn1)
# Gold trace leads
db1.ellipse([(6, 6), (bw-6, bh-6)], outline=(212, 175, 55, 180), width=2)
db1.line([(0, bh//2), (6, bh//2)], fill=(212, 175, 55, 240), width=2)
db1.line([(bw-6, bh//2), (bw, bh//2)], fill=(212, 175, 55, 240), width=2)
# Switch body
db1.ellipse([(12, 12), (bw-12, bh-12)], fill=(24, 30, 40, 255), outline=(75, 95, 120, 255), width=2)
# Neon Magenta LED ring
db1.ellipse([(18, 18), (bw-18, bh-18)], outline=(255, 0, 127, 240), width=3)
f_b = get_font(BOLD_FONT, 11)
sb = db1.textbbox((0, 0), "SWAP", font=f_b)
db1.text(((bw-(sb[2]-sb[0]))//2, (bh-(sb[3]-sb[1]))//2-1), "SWAP", fill=(255, 240, 250, 255), font=f_b)

# Button 2: Capacitive ENIG Gold Touch Pad
btn2 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
db2 = ImageDraw.Draw(btn2)
# Concentric guard rings
db2.ellipse([(6, 6), (bw-6, bh-6)], outline=(212, 175, 55, 140), width=1)
db2.ellipse([(12, 12), (bw-12, bh-12)], outline=(212, 175, 55, 200), width=2)
# Solid immersion gold center pad
db2.ellipse([(18, 18), (bw-18, bh-18)], fill=(212, 175, 55, 255), outline=(255, 230, 120, 255), width=2)
db2.text(((bw-(sb[2]-sb[0]))//2, (bh-(sb[3]-sb[1]))//2-1), "SWAP", fill=(20, 24, 30, 255), font=f_b)

# Button 3: Low-Profile Tactile Cherry MX Square Switch
btn3 = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
db3 = ImageDraw.Draw(btn3)
# SMT square frame
db3.rounded_rectangle([8, 8, bw-8, bh-8], radius=8, fill=(30, 36, 46, 255), outline=(80, 100, 125, 255), width=2)
db3.rounded_rectangle([16, 16, bw-16, bh-16], radius=4, fill=(15, 20, 28, 255), outline=(0, 240, 255, 200), width=2)
db3.text(((bw-(sb[2]-sb[0]))//2, (bh-(sb[3]-sb[1]))//2-1), "SWAP", fill=(0, 240, 255, 255), font=f_b)


# ==============================================================================
# SECTION 3: COMPOSE COMPREHENSIVE HARDWARE COMPONENTS COMPARISON SHEET
# ==============================================================================
sheet_hw = Image.new("RGBA", (1280, 880), (8, 11, 16, 255))
d_hw = ImageDraw.Draw(sheet_hw)

d_hw.text((36, 24), "CIRCUIT BOARD HARDWARE COMPONENTS — 3 OPTIONS FOR EACH ELEMENT", fill=(240, 245, 255, 255), font=f_h1)
d_hw.text((36, 58), "Full hardware theme alignment · Dropper Assemblies · Chamber Floor Sockets · Interactive SWAP Buttons", fill=(130, 145, 165, 255), font=f_lead)

# Row 1: Dropper Assemblies (3 Options)
d_hw.text((36, 95), "1. DROPPER ASSEMBLY OPTIONS (CHIP PLACEMENT GANTRY)", fill=(0, 240, 255, 255), font=get_font(BOLD_FONT, 14))

drop_opts = [
    ("OPTION 1: SMT PICK-AND-PLACE VACUUM HEAD", drop1, "Pneumatic suction head · Precision linear guide rod · Collimated laser crosshair"),
    ("OPTION 2: POLYIMIDE FLEX RIBBON CABLE (FFC)", drop2, "Flexible copper-clad ribbon cable · Hanging bus loops · Low-profile gold clamp"),
    ("OPTION 3: TAPE-AND-REEL COMPONENT CASSETTE", drop3, "Perforated 8mm tape feeder · Mechanical indexing shuttle · Industrial automation")
]

for idx, (title, img, desc) in enumerate(drop_opts):
    x = 36 + idx * 405
    y = 125
    d_hw.rounded_rectangle([x, y, x + 385, y + 175], radius=12, fill=(16, 21, 29, 255), outline=(35, 46, 62, 255), width=1)
    d_hw.text((x + 16, y + 14), title, fill=(240, 245, 255, 240), font=get_font(BOLD_FONT, 10))
    # Center image
    sheet_hw.paste(img, (x + (385 - dw)//2, y + 42), img)
    d_hw.text((x + 16, y + 145), desc, fill=(130, 145, 165, 255), font=get_font(REG_FONT, 9))

# Row 2: Floor Sockets (3 Options)
d_hw.text((36, 325), "2. CHAMBER FLOOR BED OPTIONS (SOCKET RETENTION SEAT)", fill=(0, 240, 255, 255), font=get_font(BOLD_FONT, 14))

floor_opts = [
    ("OPTION 1: LGA SPRING-LOADED GOLD PIN BED", floor1, "Dense gold contact pins · Spring compression feedback · Authentic CPU socket"),
    ("OPTION 2: PCIe SERVER EDGE-CONNECTOR SLOT", floor2, "Heavy-duty gold finger retention slot · End retention latches · Server blade vibe"),
    ("OPTION 3: ZERO INSERTION FORCE (ZIF) RAIL", floor3, "Mechanical locking lever arm · Gold contact pads · Clean tactile industrial design")
]

for idx, (title, img, desc) in enumerate(floor_opts):
    x = 36 + idx * 405
    y = 355
    d_hw.rounded_rectangle([x, y, x + 385, y + 155], radius=12, fill=(16, 21, 29, 255), outline=(35, 46, 62, 255), width=1)
    d_hw.text((x + 16, y + 14), title, fill=(240, 245, 255, 240), font=get_font(BOLD_FONT, 10))
    sheet_hw.paste(img, (x + (385 - fw)//2, y + 45), img)
    d_hw.text((x + 16, y + 125), desc, fill=(130, 145, 165, 255), font=get_font(REG_FONT, 9))

# Row 3: SWAP Buttons (3 Options)
d_hw.text((36, 535), "3. INTERACTIVE CONTROL OPTIONS (SWAP BUTTON)", fill=(0, 240, 255, 255), font=get_font(BOLD_FONT, 14))

btn_opts = [
    ("OPTION 1: SMT TACTILE SWITCH + LED RING", btn1, "Surface-mount clicky switch · Gold solder leads · Illuminated neon magenta halo"),
    ("OPTION 2: CAPACITIVE GOLD TOUCH PAD", btn2, "Exposed 24K ENIG gold touch electrode · Concentric guard rings · Pure PCB surface"),
    ("OPTION 3: LOW-PROFILE TACTILE KEYCAP", btn3, "Square tactile micro-switch · Cyan backlight legend · Clicky mechanical feel")
]

for idx, (title, img, desc) in enumerate(btn_opts):
    x = 36 + idx * 405
    y = 565
    d_hw.rounded_rectangle([x, y, x + 385, y + 185], radius=12, fill=(16, 21, 29, 255), outline=(35, 46, 62, 255), width=1)
    d_hw.text((x + 16, y + 14), title, fill=(240, 245, 255, 240), font=get_font(BOLD_FONT, 10))
    sheet_hw.paste(img, (x + (385 - bw)//2, y + 42), img)
    d_hw.text((x + 16, y + 155), desc, fill=(130, 145, 165, 255), font=get_font(REG_FONT, 9))

# Save HW options showcase
hw_showcase = f"{OUT_DIR}/circuit_board_hardware_showcase.png"
sheet_hw.save(hw_showcase, "PNG")
sheet_hw.save(f"{BRAIN_DIR}/circuit_board_hardware_showcase.png", "PNG")
print(f"✓ Saved Hardware 3-Way Showcase to {hw_showcase}")

print("=== All options rendered successfully ===")

#!/usr/bin/env python3
"""
render_processor_chip_blocks.py
Generates game block designs themed as Computer Processor / Silicon Chips.
Subject: Magenta Tier 7 Processor Block (80x80px target, 512x512px master).
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = "/Users/georgearmah/into-the-darkness/assets/ui/tech_explorations"
BRAIN_DIR = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

M = 512
TARGET_PX = 80
pad = 28
x0, y0, x1, y1 = pad, pad, M - pad, M - pad

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def add_specular(draw, x, y, size=14, color=(255, 255, 255, 240)):
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    draw.line([(x - size//2, y - size//2), (x + size//2, y + size//2)], fill=(255, 255, 255, 180), width=3)

# ------------------------------------------------------------------------------
# CHIP OPTION 1: ANODIZED ENTERPRISE SERVER CPU (IHS HEAT SPREADER)
# Anodized solid magenta aluminum heat spreader with laser-etched specs,
# pin-1 gold triangle, perimeter substrate, and bold laser "7".
# ------------------------------------------------------------------------------
print("1. Rendering Chip Option 1: Anodized Server CPU...")
im1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))

# Drop shadow
s1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s1).rounded_rectangle([x0+4, y0+10, x1-4, y1+16], radius=24, fill=(0, 0, 0, 160))
im1 = Image.alpha_composite(s1.filter(ImageFilter.GaussianBlur(16)), im1)

draw1 = ImageDraw.Draw(im1)
# Outer PCB Substrate Carrier (Dark matte FR4 with gold corner alignment pads)
draw1.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(20, 24, 30, 255), outline=(55, 65, 80, 255), width=2)

# Gold perimeter contact pads / surface-mount capacitors along edges
c_gold = (212, 175, 55, 240)
for p in range(x0+40, x1-40, 36):
    # Top and bottom test pads
    draw1.rectangle([p, y0+6, p+16, y0+14], fill=c_gold)
    draw1.rectangle([p, y1-14, p+16, y1-6], fill=c_gold)
    # Left and right test pads
    draw1.rectangle([x0+6, p, x0+14, p+16], fill=c_gold)
    draw1.rectangle([x1-14, p, x1-6, p+16], fill=c_gold)

# Pin-1 Golden Index Triangle in top-left
draw1.polygon([(x0+12, y0+12), (x0+32, y0+12), (x0+12, y0+32)], fill=(255, 215, 0, 255))

# Integrated Heat Spreader (IHS) — SOLID ANODIZED MAGENTA LID
ihs_pad = 22
ix0, iy0, ix1, iy1 = x0 + ihs_pad, y0 + ihs_pad, x1 - ihs_pad, y1 - ihs_pad
icorner = 18

# Anodized magenta body
mr, mg, mb = 236, 40, 130
draw1.rounded_rectangle([ix0, iy0, ix1, iy1], radius=icorner, fill=(mr, mg, mb, 255))

# Brushed horizontal metal grain
for y in range(iy0, iy1):
    f = 1.0 - abs(y - (iy0 + iy1)//2) / ((iy1 - iy0)//2) * 0.25
    col = (int(mr * f), int(mg * f), int(mb * f), 255)
    if y % 3 == 0:
        draw1.line([(ix0+icorner//2, y), (ix1-icorner//2, y)], fill=col, width=1)

# Beveled Metallic Rim on Heat Spreader (CNC Diamond Chamfer)
draw1.line([(ix0+icorner, iy0+2), (ix1-icorner, iy0+2)], fill=(255, 230, 245, 240), width=4)
draw1.line([(ix0+2, iy0+icorner), (ix0+2, iy1-icorner)], fill=(255, 210, 235, 190), width=4)
draw1.line([(ix0+icorner, iy1-2), (ix1-icorner, iy1-2)], fill=(80, 5, 45, 255), width=4)
draw1.line([(ix1-2, iy0+icorner), (ix1-2, iy1-icorner)], fill=(80, 5, 45, 255), width=4)

# Laser-Etched Technical Spec Markings
f_spec = get_font(MONO_FONT, 14)
draw1.text((ix0+24, iy0+20), "APEX-7 // 7-CORE NEURAL DENSITY", fill=(255, 200, 230, 180), font=f_spec)
draw1.text((ix0+24, iy0+38), "4.8 GHz · 128MB L3 · SILICON-7", fill=(255, 200, 230, 140), font=f_spec)

# Bold Laser-Etched Stencil Numeral "7"
f_num = get_font(BOLD_FONT, 200)
bbox = draw1.textbbox((0, 0), "7", font=f_num)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 + 10

# Inset drop shadow
draw1.text((tx, ty+5), "7", fill=(70, 5, 38, 240), font=f_num)
# Laser-etched white face with bright rim
draw1.text((tx, ty), "7", fill=(255, 255, 255, 255), font=f_num)

# Laser barcode / serial footprint at bottom
draw1.text((ix0+24, iy1-32), "SN: 0x7F4A-3320-LEO", fill=(255, 200, 230, 140), font=f_spec)
for bx in range(ix1-90, ix1-24, 6):
    bh = 14 if bx % 12 == 0 else 8
    draw1.line([(bx, iy1-30), (bx, iy1-30+bh)], fill=(255, 220, 240, 180), width=2)

add_specular(draw1, ix0+icorner, iy0+4, size=16)

im1.save(f"{OUT_DIR}/chip_option1_server_cpu_master.png")
im1.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/chip_option1_server_cpu_80px.png")
im1.save(f"{BRAIN_DIR}/chip_option1_server_cpu_master.png")
im1.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/chip_option1_server_cpu_80px.png")

# ------------------------------------------------------------------------------
# CHIP OPTION 2: MULTI-CHIP MODULE (BARE SILICON DIE + 7 COMPUTE CORES)
# Substrate with central exposed magenta silicon die segmented into 7 compute units
# surrounded by miniature decoupling capacitors and gold trace bus.
# ------------------------------------------------------------------------------
print("2. Rendering Chip Option 2: Multi-Chip Silicon Die...")
im2 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
im2 = Image.alpha_composite(s1.filter(ImageFilter.GaussianBlur(16)), im2)
draw2 = ImageDraw.Draw(im2)

# Dark Silicon Substrate
draw2.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(16, 18, 24, 255), outline=(60, 70, 85, 255), width=2)

# Fine gold circuit traces radiating from center die
c_trace = (200, 155, 45, 100)
for a in range(0, 360, 15):
    rad = math.radians(a)
    sx = int(M//2 + 160 * math.cos(rad))
    sy = int(M//2 + 160 * math.sin(rad))
    ex = int(M//2 + 210 * math.cos(rad))
    ey = int(M//2 + 210 * math.sin(rad))
    draw2.line([(sx, sy), (ex, ey)], fill=c_trace, width=2)

# Miniature Decoupling Capacitors (SMD components) around die perimeter
for d in range(x0+48, x1-48, 24):
    draw2.rectangle([d, y0+24, d+14, y0+32], fill=(160, 130, 80, 255), outline=(220, 200, 140, 255))
    draw2.rectangle([d, y1-32, d+14, y1-24], fill=(160, 130, 80, 255), outline=(220, 200, 140, 255))

# Central BARE SILICON DIE — SOLID IRIDESCENT MAGENTA
dx0, dy0, dx1, dy1 = x0 + 44, y0 + 44, x1 - 44, y1 - 44
draw2.rounded_rectangle([dx0-4, dy0-4, dx1+4, dy1+4], radius=14, fill=(8, 10, 14, 255))
draw2.rounded_rectangle([dx0, dy0, dx1, dy1], radius=12, fill=(236, 40, 130, 255))

# 7-Core Silicon Architecture Grid Divisions (7 micro-die sections)
cw = (dx1 - dx0) // 3
ch = (dy1 - dy0) // 3
for gx in [dx0 + cw, dx0 + 2*cw]:
    draw2.line([(gx, dy0), (gx, dy1)], fill=(90, 8, 48, 140), width=2)
for gy in [dy0 + ch, dy0 + 2*ch]:
    draw2.line([(dx0, gy), (dx1, gy)], fill=(90, 8, 48, 140), width=2)

# Silicon wafer mirror reflection band (45-degree iridescent sheen)
draw2.polygon([(dx0+20, dy0), (dx0+80, dy0), (dx1, dy1-60), (dx1, dy1)], fill=(255, 180, 230, 45))

# Silicon Die Bevels
draw2.line([(dx0+12, dy0+2), (dx1-12, dy0+2)], fill=(255, 240, 250, 240), width=3)
draw2.line([(dx0+2, dy0+12), (dx0+2, dy1-12)], fill=(255, 220, 240, 200), width=3)

# Bold Crisp White "7"
f_die = get_font(BOLD_FONT, 200)
draw2.text((tx, ty+5), "7", fill=(60, 5, 30, 240), font=f_die)
draw2.text((tx, ty), "7", fill=(255, 255, 255, 255), font=f_die)

# Gold corner index triangle
draw2.polygon([(dx0+8, dy0+8), (dx0+26, dy0+8), (dx0+8, dy0+26)], fill=(255, 215, 0, 255))
add_specular(draw2, dx0+16, dy0+4, size=16)

im2.save(f"{OUT_DIR}/chip_option2_silicon_die_master.png")
im2.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/chip_option2_silicon_die_80px.png")
im2.save(f"{BRAIN_DIR}/chip_option2_silicon_die_master.png")
im2.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/chip_option2_silicon_die_80px.png")

# ------------------------------------------------------------------------------
# CHIP OPTION 3: VINTAGE CERAMIC PROCESSOR (GOLD LEAD FRAME / RETRO TECH)
# Rich magenta ceramic package, 24k gold braze seal lid frame, gold pins,
# gold silkscreen lettering "APEX 7000".
# ------------------------------------------------------------------------------
print("3. Rendering Chip Option 3: Vintage Ceramic Processor...")
im3 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
im3 = Image.alpha_composite(s1.filter(ImageFilter.GaussianBlur(16)), im3)
draw3 = ImageDraw.Draw(im3)

# Ceramic Package Body (Matte textured dark magenta ceramic)
draw3.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=(200, 25, 105, 255), outline=(130, 15, 65, 255), width=3)

# Ceramic texture micro-noise
noise = np.random.normal(0, 6, (M, M)).astype(np.float32)
arr3 = np.array(im3).astype(np.float32)
arr3[:, :, 0] = np.clip(arr3[:, :, 0] + noise, 0, 255)
arr3[:, :, 1] = np.clip(arr3[:, :, 1] + noise, 0, 255)
arr3[:, :, 2] = np.clip(arr3[:, :, 2] + noise, 0, 255)
im3 = Image.fromarray(arr3.astype(np.uint8))
draw3 = ImageDraw.Draw(im3)

# 24K Gold Braze Lid Frame (Inner gold seal line)
g_pad = 26
gx0, gy0, gx1, gy1 = x0 + g_pad, y0 + g_pad, x1 - g_pad, y1 - g_pad
# Gold border
draw3.rounded_rectangle([gx0, gy0, gx1, gy1], radius=18, outline=(212, 175, 55, 255), width=8)
draw3.rounded_rectangle([gx0+4, gy0+4, gx1-4, gy1-4], radius=14, outline=(255, 225, 95, 255), width=2)

# Solid Saturated Magenta Center Lid
draw3.rounded_rectangle([gx0+8, gy0+8, gx1-8, gy1-8], radius=12, fill=(236, 40, 130, 255))

# Gold silkscreen technical text
draw3.text((gx0+24, gy0+22), "APX 7000-MG", fill=(240, 215, 120, 240), font=get_font(MONO_FONT, 16))
draw3.text((gx0+24, gy0+42), "MALAYSIA · 3:32 AM", fill=(220, 190, 90, 200), font=get_font(MONO_FONT, 13))

# Gold Corner Index Tab
draw3.rectangle([gx0, gy0, gx0+28, gy0+28], fill=(255, 215, 0, 255))
draw3.ellipse([gx0+8, gy0+8, gx0+20, gy0+20], fill=(160, 120, 20, 255))

# Centered Gold/White "7"
draw3.text((tx, ty+5), "7", fill=(100, 10, 50, 240), font=f_die)
draw3.text((tx, ty), "7", fill=(255, 255, 255, 255), font=f_die)
# Gold rim around text
draw3.text((tx-1, ty-1), "7", fill=(255, 225, 110, 160), font=f_die)

add_specular(draw3, gx0+18, gy0+4, size=16)

im3.save(f"{OUT_DIR}/chip_option3_ceramic_processor_master.png")
im3.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/chip_option3_ceramic_processor_80px.png")
im3.save(f"{BRAIN_DIR}/chip_option3_ceramic_processor_master.png")
im3.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/chip_option3_ceramic_processor_80px.png")

# ------------------------------------------------------------------------------
# CHIP OPTION 4: MODERN MINIMALIST BGA SoC (APPLE M-SERIES STYLE)
# Satin anodized magenta monolithic lid with diamond-cut chamfers,
# laser-etched minimalist "7", and sleek dark perimeter BGA lip.
# ------------------------------------------------------------------------------
print("4. Rendering Chip Option 4: Modern Minimalist SoC...")
im4 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
im4 = Image.alpha_composite(s1.filter(ImageFilter.GaussianBlur(16)), im4)
draw4 = ImageDraw.Draw(im4)

# Perimeter dark substrate lip (2px border)
draw4.rounded_rectangle([x0, y0, x1, y1], radius=32, fill=(18, 22, 28, 255), outline=(45, 52, 65, 255), width=2)

# Solid Anodized Magenta Monolith (Fills nearly 96% of the package)
soc_pad = 14
sx0, sy0, sx1, sy1 = x0 + soc_pad, y0 + soc_pad, x1 - soc_pad, y1 - soc_pad
scorner = 26
draw4.rounded_rectangle([sx0, sy0, sx1, sy1], radius=scorner, fill=(236, 40, 130, 255))

# Smooth satin anodized vertical lighting gradient
for y in range(sy0, sy1):
    prog = (y - sy0) / (sy1 - sy0)
    col = (
        int(245 - 25 * prog),
        int(55 - 20 * prog),
        int(145 - 30 * prog),
        255
    )
    draw4.line([(sx0 + scorner//2, y), (sx1 - scorner//2, y)], fill=col, width=1)

# CNC Diamond-Cut Beveled Chamfer
draw4.line([(sx0+scorner, sy0+3), (sx1-scorner, sy0+3)], fill=(255, 235, 248, 240), width=4)
draw4.line([(sx0+3, sy0+scorner), (sx0+3, sy1-scorner)], fill=(255, 215, 235, 190), width=4)
draw4.line([(sx0+scorner, sy1-3), (sx1-scorner, sy1-3)], fill=(90, 8, 48, 255), width=4)
draw4.line([(sx1-3, sy0+scorner), (sx1-3, sy1-scorner)], fill=(90, 8, 48, 255), width=4)

# 45-degree diagonal corner chamfers
cham = 30
draw4.line([(sx0, sy0+cham), (sx0+cham, sy0)], fill=(255, 255, 255, 220), width=4)
draw4.line([(sx1-cham, sy0), (sx1, sy0+cham)], fill=(255, 255, 255, 180), width=4)
draw4.line([(sx0, sy1-cham), (sx0+cham, sy1)], fill=(90, 8, 48, 255), width=4)
draw4.line([(sx1-cham, sy1), (sx1, sy1-cham)], fill=(90, 8, 48, 255), width=4)

# Minimalist Laser Stencil "7"
draw4.text((tx, ty+5), "7", fill=(70, 5, 38, 240), font=f_die)
draw4.text((tx, ty), "7", fill=(255, 255, 255, 255), font=f_die)

# Minimal laser etched silicon label
draw4.text((sx0+32, sy1-36), "APEX M7 // 3.32", fill=(255, 200, 230, 160), font=get_font(MONO_FONT, 14))

add_specular(draw4, sx0+scorner, sy0+4, size=18)

im4.save(f"{OUT_DIR}/chip_option4_minimalist_soc_master.png")
im4.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/chip_option4_minimalist_soc_80px.png")
im4.save(f"{BRAIN_DIR}/chip_option4_minimalist_soc_master.png")
im4.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/chip_option4_minimalist_soc_80px.png")

# ------------------------------------------------------------------------------
# COMPOSE 4-WAY CHIP SHOWCASE SHEET
# ------------------------------------------------------------------------------
print("Composing 4-way chip comparison sheet...")
SW, SH = 1440, 520
comp = Image.new("RGBA", (SW, SH), (7, 9, 14, 255))
cdraw = ImageDraw.Draw(comp)

font_t = ImageFont.truetype(BOLD_FONT, 24)
font_s = ImageFont.truetype(REG_FONT, 14)
font_tag = ImageFont.truetype(BOLD_FONT, 13)

cdraw.text((40, 24), "PROCESSOR CHIP GAME BLOCKS — SOLID MAGENTA #7", fill=(240, 246, 252, 255), font=font_t)
cdraw.text((40, 60), "Theme Concept: Game blocks designed as computer processors & silicon packages · Full magenta body", fill=(139, 148, 158, 255), font=font_s)

opts = [
    {
        "title": "1. SERVER CPU (IHS LID)",
        "sub": "Anodized magenta heat spreader\nLaser specs · Pin-1 gold triangle · Test pads",
        "img": im1,
        "tag": "ENTERPRISE CPU"
    },
    {
        "title": "2. BARE SILICON DIE (MCM)",
        "sub": "Exposed magenta silicon die with 7 cores\nSMD capacitors · Radiating gold trace bus",
        "img": im2,
        "tag": "MULTI-CHIP DIE"
    },
    {
        "title": "3. CERAMIC PROCESSOR",
        "sub": "Rich magenta ceramic body · Gold braze seal\nGold silkscreen 'APX 7000' · Vintage tech",
        "img": im3,
        "tag": "RETRO CERAMIC"
    },
    {
        "title": "4. MINIMALIST SoC (M-SERIES)",
        "sub": "Satin anodized magenta monolithic lid\nDiamond chamfers · Clean laser typography",
        "img": im4,
        "tag": "MODERN CLEAN-TECH"
    }
]

cw = 325
for i, opt in enumerate(opts):
    cx = 40 + i * (cw + 20)
    cdraw.rounded_rectangle([cx, 96, cx + cw, 480], radius=14, fill=(18, 22, 30, 255), outline=(45, 52, 65, 255), width=1)
    cdraw.text((cx + 18, 114), opt["title"], fill=(0, 240, 255, 255), font=font_tag)
    
    p = opt["img"].resize((210, 210), Image.Resampling.LANCZOS)
    comp.paste(p, (cx + (cw - 210)//2, 148), p)
    
    lines = opt["sub"].split("\n")
    cdraw.text((cx + 18, 386), lines[0], fill=(240, 246, 252, 255), font=font_s)
    cdraw.text((cx + 18, 408), lines[1], fill=(139, 148, 158, 255), font=font_s)
    
    cdraw.line([(cx + 18, 436), (cx + cw - 18, 436)], fill=(35, 42, 54, 255), width=1)
    cdraw.text((cx + 18, 448), "In-Game 80×80px scale:", fill=(110, 120, 135, 255), font=font_s)
    small_p = opt["img"].resize((32, 32), Image.Resampling.LANCZOS)
    comp.paste(small_p, (cx + cw - 50, 442), small_p)

comp.save(f"{OUT_DIR}/processor_chips_showcase.png")
comp.save(f"{BRAIN_DIR}/processor_chips_showcase.png")
print("✓ Showcase saved to OUT_DIR and BRAIN_DIR")

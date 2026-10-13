#!/usr/bin/env python3
"""
render_tech_magenta_7_options.py
Generates 5 distinct, high-fidelity tech-related options for a single game block:
Color: Magenta (#FF007F / #EC4899)
Number: 7
Size: Master 512x512px, Target 80x80px
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = "/Users/georgearmah/into-the-darkness/assets/ui/tech_explorations"
os.makedirs(OUT_DIR, exist_ok=True)

M = 512
TARGET_PX = 80
BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(REG_FONT, size)
        except Exception:
            return ImageFont.load_default()

def add_specular(draw, x, y, size=14, color=(255, 255, 255, 240)):
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    draw.line([(x - size//2, y - size//2), (x + size//2, y + size//2)], fill=(255, 255, 255, 180), width=3)

# ==============================================================================
# OPTION 1: VECTOR PHOSPHOR CRT (ANALOG TERMINAL)
# ==============================================================================
print("1. Rendering Option 1: Vector Phosphor CRT...")
im1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
pad = 28
x0, y0, x1, y1 = pad, pad, M - pad, M - pad
corner = 40

# Ambient drop shadow
s1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s1).rounded_rectangle([x0+4, y0+8, x1-4, y1+12], radius=corner, fill=(0, 0, 0, 150))
im1 = Image.alpha_composite(s1.filter(ImageFilter.GaussianBlur(16)), im1)

# Curved CRT Glass aperture body (Deep smoked cathode glass)
draw1 = ImageDraw.Draw(im1)
draw1.rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=(14, 8, 18, 240), outline=(55, 30, 65, 255), width=4)

# Horizontal Raster Scanlines
for y in range(y0+6, y1-6, 4):
    draw1.line([(x0+12, y), (x1-12, y)], fill=(0, 0, 0, 80), width=2)

# Outer Phosphor Glow Layer
glow1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
gdraw1 = ImageDraw.Draw(glow1)
# Glowing Vector Wireframe Box
inset = 24
gx0, gy0, gx1, gy1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
gdraw1.rounded_rectangle([gx0, gy0, gx1, gy1], radius=24, outline=(255, 0, 128, 220), width=6)
# 3D Vector Depth lines (wireframe cube depth)
gdraw1.line([(gx0, gy0+24), (gx0+40, gy0)], fill=(255, 0, 128, 180), width=3)
gdraw1.line([(gx1, gy0+24), (gx1-40, gy0)], fill=(255, 0, 128, 180), width=3)
gdraw1.line([(gx0, gy1-24), (gx0+40, gy1)], fill=(255, 0, 128, 180), width=3)
gdraw1.line([(gx1, gy1-24), (gx1-40, gy1)], fill=(255, 0, 128, 180), width=3)

# CRT Vector "7"
f_crt = get_font(MONO_FONT, 230)
bbox = gdraw1.textbbox((0, 0), "7", font=f_crt)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 - 16
# Vector bloom aura
gdraw1.text((tx, ty), "7", fill=(255, 0, 128, 255), font=f_crt)

# Blur the glow for CRT phosphor diffusion
blurred_glow = glow1.filter(ImageFilter.GaussianBlur(10))
im1 = Image.alpha_composite(im1, blurred_glow)

# Re-draw crisp hot white/magenta vector center core
draw1 = ImageDraw.Draw(im1)
draw1.rounded_rectangle([gx0, gy0, gx1, gy1], radius=24, outline=(255, 180, 220, 255), width=2)
draw1.text((tx, ty), "7", fill=(255, 230, 245, 255), font=f_crt)

# Curved glass specular reflection glare across top corner
for i in range(20):
    alpha = int(40 * (1.0 - i / 20.0))
    draw1.arc([x0+8, y0+8, x1-8, y1-8], start=190, end=260, fill=(255, 255, 255, alpha), width=3)

im1.save(f"{OUT_DIR}/option1_vector_crt_master.png")
im1.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/option1_vector_crt_80px.png")

# ==============================================================================
# OPTION 2: SERVER BLADE / ENTERPRISE SILICON (DATACENTER HARDWARE)
# ==============================================================================
print("2. Rendering Option 2: Server Blade / Enterprise Silicon...")
im2 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
s2 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s2).rounded_rectangle([x0+4, y0+8, x1-4, y1+12], radius=24, fill=(0, 0, 0, 160))
im2 = Image.alpha_composite(s2.filter(ImageFilter.GaussianBlur(16)), im2)
draw2 = ImageDraw.Draw(im2)

# Matte dark titanium server chassis body
draw2.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(24, 28, 36, 255), outline=(75, 85, 100, 255), width=3)

# Brushed metal horizontal texture
for y in range(y0+4, y1-4):
    if y % 3 == 0:
        draw2.line([(x0+8, y), (x1-8, y)], fill=(32, 38, 48, 255), width=1)

# Subtle PCB copper circuit traces on surface
c_gold = (180, 115, 35, 70)
draw2.line([(x0+40, y0+60), (x0+90, y0+60), (x0+120, y0+90)], fill=c_gold, width=2)
draw2.line([(x1-40, y1-60), (x1-90, y1-60), (x1-120, y1-90)], fill=c_gold, width=2)
draw2.ellipse([x0+38, y0+58, x0+42, y0+62], fill=c_gold)
draw2.ellipse([x1-42, y1-62, x1-38, y1-58], fill=c_gold)

# Recessed glowing neon magenta status lightpipe channel
chan_pad = 22
cx0, cy0, cx1, cy1 = x0 + chan_pad, y0 + chan_pad, x1 - chan_pad, y1 - chan_pad
# Inset channel shadow
draw2.rounded_rectangle([cx0-2, cy0-2, cx1+2, cy1+2], radius=16, fill=(10, 12, 16, 255))
# Glowing Magenta Lightpipe
draw2.rounded_rectangle([cx0, cy0, cx1, cy1], radius=14, outline=(255, 0, 128, 255), width=4)

# Inner Module Face
face_pad = 36
fx0, fy0, fx1, fy1 = x0 + face_pad, y0 + face_pad, x1 - face_pad, y1 - face_pad
draw2.rounded_rectangle([fx0, fy0, fx1, fy1], radius=12, fill=(16, 18, 24, 255))

# Hex-drive mounting screws at 4 corners
for hx, hy in [(x0+14, y0+14), (x1-14, y0+14), (x0+14, y1-14), (x1-14, y1-14)]:
    draw2.ellipse([hx-6, hy-6, hx+6, hy+6], fill=(50, 58, 70, 255), outline=(120, 135, 155, 255), width=1)
    draw2.line([(hx-3, hy), (hx+3, hy)], fill=(20, 24, 30, 255), width=1)

# Industrial Laser-Etched Stencil "7"
f_blade = get_font(BOLD_FONT, 200)
bbox = draw2.textbbox((0, 0), "7", font=f_blade)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 - 14

# Inset drop shadow
draw2.text((tx, ty+4), "7", fill=(0, 0, 0, 240), font=f_blade)
# Solid white silkscreen stencil with magenta backlit rim
draw2.text((tx, ty), "7", fill=(245, 248, 255, 255), font=f_blade)

# Status LED dot in top right
draw2.ellipse([x1-32, y0+32, x1-22, y0+42], fill=(255, 0, 128, 255))

im2.save(f"{OUT_DIR}/option2_server_blade_master.png")
im2.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/option2_server_blade_80px.png")

# ==============================================================================
# OPTION 3: OPTICAL DICHROIC SILICON PRISM (QUANTUM HARDWARE)
# ==============================================================================
print("3. Rendering Option 3: Optical Dichroic Silicon Prism...")
im3 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
s3 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s3).rounded_rectangle([x0+4, y0+8, x1-4, y1+14], radius=32, fill=(0, 0, 0, 170))
im3 = Image.alpha_composite(s3.filter(ImageFilter.GaussianBlur(16)), im3)

# Smoked dark obsidian base body
draw3 = ImageDraw.Draw(im3)
draw3.rounded_rectangle([x0, y0, x1, y1], radius=32, fill=(14, 16, 22, 255), outline=(55, 18, 40, 255), width=3)

# Subsurface internal radial magenta light source
rad_bg = Image.new("RGBA", (M, M), (0, 0, 0, 0))
rdraw = ImageDraw.Draw(rad_bg)
for r in range(160, 0, -4):
    prog = 1.0 - (r / 160.0)
    alpha = int(190 * prog)
    rdraw.ellipse([M//2 - r, M//2 - r, M//2 + r, M//2 + r], fill=(255, 0, 128, alpha))
rad_bg = rad_bg.filter(ImageFilter.GaussianBlur(18))
im3 = Image.alpha_composite(im3, rad_bg)
draw3 = ImageDraw.Draw(im3)

# Precision 3D Beveled Prism Edge Reflections (Top/Left Specular Rim)
draw3.line([(x0+32, y0), (x1-32, y0)], fill=(255, 255, 255, 240), width=4)
draw3.line([(x0, y0+32), (x0, y1-32)], fill=(255, 255, 255, 200), width=4)
# Chromatic aberration fringe (Cyan on left bevel, Magenta on right)
draw3.line([(x0+2, y0+32), (x0+2, y1-32)], fill=(0, 240, 255, 180), width=2)
draw3.line([(x1-2, y0+32), (x1-2, y1-32)], fill=(255, 0, 128, 180), width=2)

# Floating Holographic Numeral "7"
f_prism = get_font(BOLD_FONT, 210)
bbox = draw3.textbbox((0, 0), "7", font=f_prism)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 - 14

# Magenta bloom behind text
t_glow = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(t_glow).text((tx, ty), "7", fill=(255, 0, 128, 255), font=f_prism)
im3 = Image.alpha_composite(im3, t_glow.filter(ImageFilter.GaussianBlur(14)))

# Crisp white holographic core
draw3 = ImageDraw.Draw(im3)
draw3.text((tx, ty), "7", fill=(255, 255, 255, 255), font=f_prism)

# Diagonal Specular Glints on vertices
add_specular(draw3, x0+32, y0+6, size=16)
add_specular(draw3, x1-32, y0+6, size=12)

im3.save(f"{OUT_DIR}/option3_optical_prism_master.png")
im3.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/option3_optical_prism_80px.png")

# ==============================================================================
# OPTION 4: INDUSTRIAL BENCH INSTRUMENT (TEKTRONIX / HARDWARE TEST GEAR)
# ==============================================================================
print("4. Rendering Option 4: Industrial Bench Instrument...")
im4 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
s4 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s4).rounded_rectangle([x0+4, y0+8, x1-4, y1+12], radius=16, fill=(0, 0, 0, 160))
im4 = Image.alpha_composite(s4.filter(ImageFilter.GaussianBlur(16)), im4)
draw4 = ImageDraw.Draw(im4)

# Heavy rugged molded polycarbonate bezel (dark olive-slate)
draw4.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(30, 35, 42, 255), outline=(70, 80, 95, 255), width=4)

# Rubberized corner impact bumpers
bump_size = 32
draw4.polygon([(x0, y0), (x0+bump_size, y0), (x0, y0+bump_size)], fill=(15, 18, 22, 255))
draw4.polygon([(x1, y0), (x1-bump_size, y0), (x1, y0+bump_size)], fill=(15, 18, 22, 255))
draw4.polygon([(x0, y1), (x0+bump_size, y1), (x0, y1-bump_size)], fill=(15, 18, 22, 255))
draw4.polygon([(x1, y1), (x1-bump_size, y1), (x1, y1-bump_size)], fill=(15, 18, 22, 255))

# Recessed Display Bezel with graticule screen
b_pad = 28
bx0, by0, bx1, by1 = x0 + b_pad, y0 + b_pad, x1 - b_pad, y1 - b_pad
draw4.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(12, 14, 18, 255), outline=(45, 52, 65, 255), width=2)

# Millimeter Graticule Grid (like oscilloscope screen)
for gx in range(bx0+24, bx1-12, 32):
    draw4.line([(gx, by0+4), (gx, by1-4)], fill=(255, 0, 128, 25), width=1)
for gy in range(by0+24, by1-12, 32):
    draw4.line([(bx0+4, gy), (bx1-4, gy)], fill=(255, 0, 128, 25), width=1)

# Center crosshairs
cx, cy = (bx0 + bx1) // 2, (by0 + by1) // 2
draw4.line([(cx, by0+8), (cx, by1-8)], fill=(255, 0, 128, 60), width=1)
draw4.line([(bx0+8, cy), (bx1-8, cy)], fill=(255, 0, 128, 60), width=1)

# LED Segment / Industrial "7"
f_inst = get_font(BOLD_FONT, 195)
bbox = draw4.textbbox((0, 0), "7", font=f_inst)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 - 14

# Magenta phosphor glow
draw4.text((tx, ty+3), "7", fill=(120, 0, 60, 255), font=f_inst)
draw4.text((tx, ty), "7", fill=(255, 0, 128, 255), font=f_inst)
# White-hot LED center bar
draw4.text((tx-1, ty-1), "7", fill=(255, 200, 230, 255), font=f_inst)

im4.save(f"{OUT_DIR}/option4_industrial_instrument_master.png")
im4.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/option4_industrial_instrument_80px.png")

# ==============================================================================
# OPTION 5: CYBER OBSIDIAN LIGHTPIPE (PRECISION SCI-FI)
# ==============================================================================
print("5. Rendering Option 5: Cyber Obsidian Lightpipe...")
im5 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
s5 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s5).rounded_rectangle([x0+4, y0+8, x1-4, y1+12], radius=32, fill=(0, 0, 0, 160))
im5 = Image.alpha_composite(s5.filter(ImageFilter.GaussianBlur(16)), im5)
draw5 = ImageDraw.Draw(im5)

# Aerospace titanium frame
draw5.rounded_rectangle([x0, y0, x1, y1], radius=32, fill=(45, 52, 65, 255), outline=(180, 195, 215, 240), width=3)
# Top specular rim
draw5.line([(x0+32, y0), (x1-32, y0)], fill=(255, 255, 255, 240), width=3)

# Inner Deep Obsidian Core
in_pad = 20
ix0, iy0, ix1, iy1 = x0 + in_pad, y0 + in_pad, x1 - in_pad, y1 - in_pad
draw5.rounded_rectangle([ix0, iy0, ix1, iy1], radius=20, fill=(8, 10, 15, 255))

# Neon Magenta Lightpipe border
draw5.rounded_rectangle([ix0, iy0, ix1, iy1], radius=20, outline=(255, 0, 128, 240), width=4)

# Diagonal corner chamfer glints
notch = 28
draw5.line([(ix0, iy0+notch), (ix0+notch, iy0)], fill=(255, 255, 255, 200), width=2)
draw5.line([(ix1-notch, iy0), (ix1, iy0+notch)], fill=(255, 255, 255, 200), width=2)

# Bold Typographic "7"
f_obs = get_font(BOLD_FONT, 205)
bbox = draw5.textbbox((0, 0), "7", font=f_obs)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 - 14

# Inset shadow & Magenta backlight
draw5.text((tx, ty+5), "7", fill=(0, 0, 0, 255), font=f_obs)
draw5.text((tx, ty+2), "7", fill=(255, 0, 128, 180), font=f_obs)
draw5.text((tx, ty), "7", fill=(255, 255, 255, 255), font=f_obs)

add_specular(draw5, x0+32, y0+4, size=14)

im5.save(f"{OUT_DIR}/option5_cyber_obsidian_lightpipe_master.png")
im5.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/option5_cyber_obsidian_lightpipe_80px.png")

# ==============================================================================
# COMPOSE 5-WAY COMPARATIVE SHOWCASE SHEET
# ==============================================================================
print("\nComposing side-by-side comparison sheet...")
SW = 1600
SH = 560
comp = Image.new("RGBA", (SW, SH), (7, 9, 14, 255))
cdraw = ImageDraw.Draw(comp)

# Title
f_title = get_font(BOLD_FONT, 28)
cdraw.text((40, 24), "TECH THEME EXPLORATIONS: MAGENTA #7 GAME BLOCK", fill=(240, 246, 252, 255), font=f_title)
f_sub = get_font(REG_FONT, 16)
cdraw.text((40, 62), "Direct visual comparison across 5 technical hardware aesthetics · Master 512px renders + 80px 1:1 scale", fill=(139, 148, 158, 255), font=f_sub)

options = [
    {"title": "1. Vector Phosphor CRT", "sub": "Curved cathode glass · Raster scanlines · Electron beam persistence", "file": f"{OUT_DIR}/option1_vector_crt_master.png"},
    {"title": "2. Enterprise Server Blade", "sub": "Matte titanium chassis · Hex bolts · Copper PCB traces · Status LED", "file": f"{OUT_DIR}/option2_server_blade_master.png"},
    {"title": "3. Optical Silicon Prism", "sub": "Dichroic glass · Subsurface laser refraction · Floating holographic glyph", "file": f"{OUT_DIR}/option3_optical_prism_master.png"},
    {"title": "4. Bench Instrument", "sub": "Molded polymer housing · Millimeter graticule grid · Oscilloscope vibe", "file": f"{OUT_DIR}/option4_industrial_instrument_master.png"},
    {"title": "5. Cyber Obsidian Lightpipe", "sub": "Aerospace alloy chamfers · Mirror obsidian core · Neon edge channel", "file": f"{OUT_DIR}/option5_cyber_obsidian_lightpipe_master.png"},
]

card_w = 280
start_x = 40
card_y = 110

for i, opt in enumerate(options):
    cx = start_x + i * (card_w + 24)
    # Card background
    cdraw.rounded_rectangle([cx, card_y, cx + card_w, card_y + 410], radius=12, fill=(18, 22, 30, 240), outline=(45, 52, 65, 200), width=1)
    
    # Image preview
    p_img = Image.open(opt["file"]).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
    comp.paste(p_img, (cx + (card_w - 220)//2, card_y + 16), p_img)
    
    # Titles
    f_card_t = get_font(BOLD_FONT, 15)
    cdraw.text((cx + 16, card_y + 252), opt["title"], fill=(0, 240, 255, 255), font=f_card_t)
    
    # Text wrapping for subtitle
    f_card_s = get_font(REG_FONT, 12)
    words = opt["sub"].split(" · ")
    for line_idx, line in enumerate(words):
        cdraw.text((cx + 16, card_y + 280 + line_idx * 18), "• " + line, fill=(160, 175, 195, 255), font=f_card_s)
        
    # 1:1 scale preview tag at bottom
    cdraw.line([(cx + 16, card_y + 355), (cx + card_w - 16, card_y + 355)], fill=(35, 42, 54, 255), width=1)
    cdraw.text((cx + 16, card_y + 368), "In-Game 80×80px scale:", fill=(110, 120, 135, 255), font=f_card_s)
    small_p = Image.open(opt["file"]).convert("RGBA").resize((32, 32), Image.Resampling.LANCZOS)
    comp.paste(small_p, (cx + card_w - 48, card_y + 362), small_p)

comp.save(f"{OUT_DIR}/magenta_7_tech_showcase.png")
print(f"✓ Showcase sheet saved to {OUT_DIR}/magenta_7_tech_showcase.png")
print("=== All Tech Options Rendered Successfully ===")

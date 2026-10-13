#!/usr/bin/env python3
"""
render_solid_magenta_7_variants.py
Renders the Tier 7 block where the ENTIRE BLOCK is rich vibrant Magenta,
with distinct Cyber Obsidian / high-tech material finishes.
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
corner = 44

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

def get_font(size):
    return ImageFont.truetype(BOLD_FONT, size)

def add_specular(draw, x, y, size=16, color=(255, 255, 255, 240)):
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    draw.line([(x - size//2, y - size//2), (x + size//2, y + size//2)], fill=(255, 255, 255, 180), width=3)

# ------------------------------------------------------------------------------
# VARIANT A: GLOSSY BEVELED CYBER POLYMER (THEME 1 CANONICAL)
# Exactly matching the Yellow 1, Magenta 2, Cyan 3 blocks from art_theme1_cyber_obsidian_390.jpg
# Solid rich magenta throughout, directional 3D lighting, glossy chamfered bevels, quadrant seam lines.
# ------------------------------------------------------------------------------
print("Rendering Variant A: Glossy Beveled Cyber Polymer...")
im_a = Image.new("RGBA", (M, M), (0, 0, 0, 0))
# Shadow
sa = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(sa).rounded_rectangle([x0+4, y0+10, x1-4, y1+16], radius=corner, fill=(0, 0, 0, 150))
im_a = Image.alpha_composite(sa.filter(ImageFilter.GaussianBlur(18)), im_a)

draw_a = ImageDraw.Draw(im_a)
# Base solid magenta body: Vibrant #FF007F / #EC4899
mr, mg, mb = 236, 40, 130  # Rich saturated magenta
draw_a.rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=(mr, mg, mb, 255))

# Vertical lighting gradient: slightly lighter top (key light), absorbing rich deeper tone at bottom
for y in range(y0, y1):
    prog = (y - y0) / (y1 - y0)
    if prog < 0.45:
        tint = int((1.0 - prog / 0.45) * 40)
        col = (min(255, mr + tint), min(255, mg + tint + 10), min(255, mb + tint), 255)
    else:
        shade = (prog - 0.45) / 0.55 * 0.35
        col = (int(mr * (1.0 - shade)), int(mg * (1.0 - shade)), int(mb * (1.0 - shade)), 255)
    draw_a.line([(x0 + corner//2, y), (x1 - corner//2, y)], fill=col, width=1)

# Outer 3D Specular Bevels
bw = 14
# Top specular highlight
draw_a.line([(x0 + corner, y0 + 4), (x1 - corner, y0 + 4)], fill=(255, 220, 240, 230), width=bw)
# Left specular highlight
draw_a.line([(x0 + 4, y0 + corner), (x0 + 4, y1 - corner)], fill=(255, 200, 230, 180), width=bw)
# Bottom dark shadow bevel
draw_a.line([(x0 + corner, y1 - 4), (x1 - corner, y1 - 4)], fill=(80, 5, 45, 240), width=bw)
# Right dark shadow bevel
draw_a.line([(x1 - 4, y0 + corner), (x1 - 4, y1 - corner)], fill=(90, 8, 50, 200), width=bw)

# Inner recessed face border
inset = 28
draw_a.rounded_rectangle([x0 + inset, y0 + inset, x1 - inset, y1 - inset], radius=corner - 14, 
                         outline=(255, 255, 255, 60), width=2)

# Quadrant seam lines (like multi-cell block in Theme 1)
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
draw_a.line([(cx, y0 + inset), (cx, y1 - inset)], fill=(90, 8, 48, 180), width=3)
draw_a.line([(cx + 1, y0 + inset), (cx + 1, y1 - inset)], fill=(255, 200, 230, 80), width=1)
draw_a.line([(x0 + inset, cy), (x1 - inset, cy)], fill=(90, 8, 48, 180), width=3)
draw_a.line([(x0 + inset, cy + 1), (x1 - inset, cy + 1)], fill=(255, 200, 230, 80), width=1)

# Crisp white bold "7"
font = get_font(210)
bbox = draw_a.textbbox((0, 0), "7", font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (M - tw) // 2
ty = (M - th) // 2 - 12
# Inset shadow
draw_a.text((tx, ty + 6), "7", fill=(70, 5, 40, 240), font=font)
# Solid white text
draw_a.text((tx, ty), "7", fill=(255, 255, 255, 255), font=font)

# Specular glint on top-left corner
add_specular(draw_a, x0 + corner, y0 + corner//2, size=18)

im_a.save(f"{OUT_DIR}/magenta_7_solid_variant_a_glossy_master.png")
im_a.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/magenta_7_solid_variant_a_glossy_80px.png")
im_a.save(f"{BRAIN_DIR}/magenta_7_solid_variant_a_glossy_master.png")
im_a.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/magenta_7_solid_variant_a_glossy_80px.png")

# ------------------------------------------------------------------------------
# VARIANT B: TITANIUM-CHAMFERED SOLID MAGENTA MONOLITH
# Solid rich magenta core + precision brushed aerospace titanium chamfered bezel
# (Direct visual sibling to the Tier 11 Titan, but with solid magenta body!)
# ------------------------------------------------------------------------------
print("Rendering Variant B: Titanium Chamfered Solid Magenta...")
im_b = Image.new("RGBA", (M, M), (0, 0, 0, 0))
im_b = Image.alpha_composite(sa.filter(ImageFilter.GaussianBlur(18)), im_b)
draw_b = ImageDraw.Draw(im_b)

# Outer Titanium Frame
draw_b.rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=(185, 195, 210, 255), outline=(225, 235, 248, 255), width=2)
# Brushed titanium metallic lines
for y in range(y0, y1):
    f = math.sin((y - y0)/(y1 - y0) * math.pi) * 0.3 + 0.7
    if y % 3 == 0:
        draw_b.line([(x0+corner//2, y), (x1-corner//2, y)], fill=(int(180*f), int(192*f), int(210*f), 255), width=1)

# Frame specular highlights
draw_b.line([(x0 + corner, y0 + 2), (x1 - corner, y0 + 2)], fill=(255, 255, 255, 240), width=4)
draw_b.line([(x0 + 2, y0 + corner), (x0 + 2, y1 - corner)], fill=(255, 255, 255, 180), width=4)
draw_b.line([(x0 + corner, y1 - 2), (x1 - corner, y1 - 2)], fill=(65, 75, 90, 255), width=4)
draw_b.line([(x1 - 2, y0 + corner), (x1 - 2, y1 - corner)], fill=(65, 75, 90, 255), width=4)

# Inner SOLID MAGENTA Face
f_pad = 22
ix0, iy0, ix1, iy1 = x0 + f_pad, y0 + f_pad, x1 - f_pad, y1 - f_pad
icorner = corner - 14

# Inset frame bevel shadow
draw_b.rounded_rectangle([ix0-2, iy0-2, ix1+2, iy1+2], radius=icorner+2, fill=(40, 10, 25, 255))
# Solid Magenta Core
draw_b.rounded_rectangle([ix0, iy0, ix1, iy1], radius=icorner, fill=(236, 40, 130, 255))

# Vertical gradient inside magenta face
for y in range(iy0, iy1):
    prog = (y - iy0) / (iy1 - iy0)
    shade = prog * 0.3
    col = (int(245 * (1.0 - shade)), int(45 * (1.0 - shade)), int(135 * (1.0 - shade)), 255)
    draw_b.line([(ix0 + icorner//2, y), (ix1 - icorner//2, y)], fill=col, width=1)

# Diagonal 45-degree corner facets on titanium frame
cham = 34
draw_b.line([(x0, y0 + cham), (x0 + cham, y0)], fill=(255, 255, 255, 220), width=4)
draw_b.line([(x1 - cham, y0), (x1, y0 + cham)], fill=(255, 255, 255, 180), width=4)
draw_b.line([(x0, y1 - cham), (x0 + cham, y1)], fill=(70, 80, 95, 255), width=4)
draw_b.line([(x1 - cham, y1), (x1, y1 - cham)], fill=(70, 80, 95, 255), width=4)

# Center split seam
cx = (ix0 + ix1) // 2
draw_b.line([(cx, iy0), (cx, iy1)], fill=(90, 8, 48, 180), width=2)
draw_b.line([(cx + 1, iy0), (cx + 1, iy1)], fill=(255, 200, 230, 70), width=1)

# Centered White "7"
draw_b.text((tx, ty + 6), "7", fill=(50, 5, 25, 240), font=font)
draw_b.text((tx, ty), "7", fill=(255, 255, 255, 255), font=font)

add_specular(draw_b, x0 + corner, y0 + 2, size=16)

im_b.save(f"{OUT_DIR}/magenta_7_solid_variant_b_titanium_frame_master.png")
im_b.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/magenta_7_solid_variant_b_titanium_frame_80px.png")
im_b.save(f"{BRAIN_DIR}/magenta_7_solid_variant_b_titanium_frame_master.png")
im_b.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/magenta_7_solid_variant_b_titanium_frame_80px.png")

# ------------------------------------------------------------------------------
# VARIANT C: SUBSURFACE CRYSTAL MAGENTA (INTERNAL TRANSLUCENT DEPTH)
# Solid rich fuchsia body with deep internal luminescence and refractive crystal bevels
# ------------------------------------------------------------------------------
print("Rendering Variant C: Subsurface Crystal Magenta...")
im_c = Image.new("RGBA", (M, M), (0, 0, 0, 0))
im_c = Image.alpha_composite(sa.filter(ImageFilter.GaussianBlur(18)), im_c)
draw_c = ImageDraw.Draw(im_c)

# Solid dark fuchsia base
draw_c.rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=(180, 15, 90, 255))

# Subsurface internal glowing magenta core
rad_c = Image.new("RGBA", (M, M), (0, 0, 0, 0))
rc_draw = ImageDraw.Draw(rad_c)
for r in range(170, 0, -4):
    prog = 1.0 - (r / 170.0)
    alpha = int(220 * prog)
    rc_draw.ellipse([M//2 - r, M//2 - r, M//2 + r, M//2 + r], fill=(255, 40, 160, alpha))
rad_c = rad_c.filter(ImageFilter.GaussianBlur(18))

# Mask to body
mask = Image.new("L", (M, M), 0)
ImageDraw.Draw(mask).rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=255)
im_c.paste(rad_c, (0, 0), mask)
draw_c = ImageDraw.Draw(im_c)

# Crystal refraction 3D chamfers
draw_c.line([(x0 + corner, y0 + 3), (x1 - corner, y0 + 3)], fill=(255, 255, 255, 240), width=6)
draw_c.line([(x0 + 3, y0 + corner), (x0 + 3, y1 - corner)], fill=(255, 255, 255, 200), width=6)
draw_c.line([(x0 + corner, y1 - 3), (x1 - corner, y1 - 3)], fill=(70, 5, 35, 255), width=6)
draw_c.line([(x1 - 3, y0 + corner), (x1 - 3, y1 - corner)], fill=(70, 5, 35, 255), width=6)

# Inner crystal perimeter groove
draw_c.rounded_rectangle([x0 + 20, y0 + 20, x1 - 20, y1 - 20], radius=corner - 10, 
                         outline=(255, 180, 230, 90), width=2)

# Bold White "7"
draw_c.text((tx, ty + 6), "7", fill=(60, 5, 30, 240), font=font)
draw_c.text((tx, ty), "7", fill=(255, 255, 255, 255), font=font)

add_specular(draw_c, x0 + corner, y0 + 4, size=18)
add_specular(draw_c, x1 - corner, y0 + 4, size=14)

im_c.save(f"{OUT_DIR}/magenta_7_solid_variant_c_crystal_master.png")
im_c.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{OUT_DIR}/magenta_7_solid_variant_c_crystal_80px.png")
im_c.save(f"{BRAIN_DIR}/magenta_7_solid_variant_c_crystal_master.png")
im_c.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS).save(f"{BRAIN_DIR}/magenta_7_solid_variant_c_crystal_80px.png")

# ------------------------------------------------------------------------------
# COMPOSE 3-WAY SOLID MAGENTA SPOTLIGHT SHEET
# ------------------------------------------------------------------------------
print("Composing 3-way solid magenta comparison sheet...")
SW, SH = 1200, 520
comp = Image.new("RGBA", (SW, SH), (7, 9, 14, 255))
cdraw = ImageDraw.Draw(comp)

font_t = ImageFont.truetype(BOLD_FONT, 24)
font_s = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
font_tag = ImageFont.truetype(BOLD_FONT, 13)

cdraw.text((40, 24), "SOLID MAGENTA #7 GAME BLOCK — 3 FINISH OPTIONS", fill=(240, 246, 252, 255), font=font_t)
cdraw.text((40, 60), "The entire block is solid, rich magenta · Comparing glossy polymer, titanium-framed, and crystal finishes", fill=(139, 148, 158, 255), font=font_s)

opts = [
    {
        "title": "A. GLOSSY BEVELED CYBER POLYMER",
        "sub": "Exact match to Theme 1 Yellow 1, Magenta 2, Cyan 3\nSolid saturated magenta · 3D chamfers · Quadrant seams",
        "img": im_a,
        "tag": "CANONICAL THEME 1 MATCH"
    },
    {
        "title": "B. TITANIUM-FRAMED SOLID MAGENTA",
        "sub": "Brushed aerospace titanium frame + Solid magenta face\nDirect visual sibling to the Tier 11 Titan Monolith",
        "img": im_b,
        "tag": "TITANIUM BEZEL HYBRID"
    },
    {
        "title": "C. SUBSURFACE CRYSTAL MAGENTA",
        "sub": "Deep internal luminescence + Refractive crystal bevels\nRich gem-like fuchsia depth with specular vertex glints",
        "img": im_c,
        "tag": "HIGH-TECH CRYSTAL"
    }
]

cw = 360
for i, opt in enumerate(opts):
    cx = 40 + i * (cw + 20)
    cdraw.rounded_rectangle([cx, 96, cx + cw, 480], radius=14, fill=(18, 22, 30, 255), outline=(45, 52, 65, 255), width=1)
    cdraw.text((cx + 20, 114), opt["title"], fill=(0, 240, 255, 255), font=font_tag)
    
    p = opt["img"].resize((220, 220), Image.Resampling.LANCZOS)
    comp.paste(p, (cx + (cw - 220)//2, 148), p)
    
    # Subtitle
    lines = opt["sub"].split("\n")
    cdraw.text((cx + 20, 386), lines[0], fill=(240, 246, 252, 255), font=font_s)
    cdraw.text((cx + 20, 408), lines[1], fill=(139, 148, 158, 255), font=font_s)
    
    # 1:1 scale preview
    cdraw.line([(cx + 20, 436), (cx + cw - 20, 436)], fill=(35, 42, 54, 255), width=1)
    cdraw.text((cx + 20, 448), "In-Game 80×80px scale:", fill=(110, 120, 135, 255), font=font_s)
    small_p = opt["img"].resize((32, 32), Image.Resampling.LANCZOS)
    comp.paste(small_p, (cx + cw - 52, 442), small_p)

comp.save(f"{OUT_DIR}/solid_magenta_7_showcase.png")
comp.save(f"{BRAIN_DIR}/solid_magenta_7_showcase.png")
print("✓ Showcase saved to OUT_DIR and BRAIN_DIR")

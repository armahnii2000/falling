#!/usr/bin/env python3
"""
render_silver_processor_chips.py
Renders processor chip game blocks with:
- Silver / Metallic backdrop (heat spreader / metal frame / carrier)
- Inner square being the tier color (Magenta for #7) and tier number.
- Mathematically centered numerals (accounting for glyph ascent/descent ink bbox).

Subject: Magenta Tier 7 Processor Block (80x80px target, 512x512px master).
Generates 4 distinct design variations of this concept.
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

def draw_centered_numeral(draw, cx, cy, text, font, fill_color, shadow_color=None):
    """
    Draws text perfectly centered at (cx, cy) using exact glyph ink bounding box.
    Eliminates Pillow's default top-left baseline/descent offset.
    """
    bb = draw.textbbox((0, 0), text, font=font)
    tx = int(cx - (bb[0] + bb[2]) / 2.0)
    ty = int(cy - (bb[1] + bb[3]) / 2.0)
    if shadow_color:
        draw.text((tx + 2, ty + 3), text, fill=shadow_color, font=font)
    draw.text((tx, ty), text, fill=fill_color, font=font)

def draw_brushed_metal_rect(draw, x0, y0, x1, y1, radius=16, base_rgb=(210, 215, 225), grain_strength=18):
    """Draws a rounded rectangle filled with anisotropic brushed silver metal texture."""
    w = x1 - x0
    h = y1 - y0
    
    mask = Image.new("L", (M, M), 0)
    ImageDraw.Draw(mask).rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=255)
    
    tex = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    d_tex = ImageDraw.Draw(tex)
    
    np.random.seed(42)
    noise = np.random.normal(0, grain_strength, (h, 1)).astype(np.float32)
    
    for y in range(y0, y1):
        rel_y = (y - y0) / float(h)
        grad = 1.15 - rel_y * 0.35
        row_noise = float(noise[y - y0, 0])
        r = int(np.clip(base_rgb[0] * grad + row_noise, 0, 255))
        g = int(np.clip(base_rgb[1] * grad + row_noise, 0, 255))
        b = int(np.clip(base_rgb[2] * grad + row_noise, 0, 255))
        d_tex.line([(x0, y), (x1, y)], fill=(r, g, b, 255), width=1)
        
    d_tex.line([(x0 + radius, y0 + 2), (x1 - radius, y0 + 2)], fill=(255, 255, 255, 220), width=3)
    d_tex.line([(x0 + 2, y0 + radius), (x0 + 2, y1 - radius)], fill=(255, 255, 255, 180), width=3)
    d_tex.line([(x0 + radius, y1 - 2), (x1 - radius, y1 - 2)], fill=(70, 75, 85, 240), width=3)
    d_tex.line([(x1 - 2, y0 + radius), (x1 - 2, y1 - radius)], fill=(70, 75, 85, 240), width=3)
    
    tex.putalpha(Image.composite(tex.split()[3], mask, mask))
    return tex

# ==============================================================================
# OPTION 1: BRUSHED NICKEL IHS WITH INSET SILICON CORE DIE
# ==============================================================================
print("1. Rendering Option 1: Brushed Nickel IHS (Centered Numeral)...")
im1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))

# Drop shadow
s1 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s1).rounded_rectangle([x0+4, y0+12, x1-4, y1+16], radius=24, fill=(0, 0, 0, 160))
im1 = Image.alpha_composite(s1.filter(ImageFilter.GaussianBlur(16)), im1)

# Outer Dark PCB Substrate Carrier
d1 = ImageDraw.Draw(im1)
d1.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(20, 25, 32, 255), outline=(50, 60, 75, 255), width=2)
d1.polygon([(x0+12, y0+12), (x0+32, y0+12), (x0+12, y0+32)], fill=(255, 215, 0, 255))

for p in range(x0+44, x1-44, 38):
    d1.rectangle([p, y0+6, p+18, y0+14], fill=(212, 175, 55, 230))
    d1.rectangle([p, y1-14, p+18, y1-6], fill=(212, 175, 55, 230))
    d1.rectangle([x0+6, p, x0+14, p+18], fill=(212, 175, 55, 230))
    d1.rectangle([x1-14, p, x1-6, p+18], fill=(212, 175, 55, 230))

# Silver Metallic Backdrop (Brushed Nickel Heat Spreader)
ihs_pad = 22
ix0, iy0, ix1, iy1 = x0 + ihs_pad, y0 + ihs_pad, x1 - ihs_pad, y1 - ihs_pad
ihs_metal = draw_brushed_metal_rect(d1, ix0, iy0, ix1, iy1, radius=18, base_rgb=(210, 216, 226), grain_strength=12)
im1 = Image.alpha_composite(im1, ihs_metal)
d1 = ImageDraw.Draw(im1)

# Laser-etched technical specs ON the silver metal backdrop
f_mono = get_font(MONO_FONT, 13)
d1.text((ix0 + 24, iy0 + 20), "APEX-7 // 7-CORE NEURAL DENSITY", fill=(95, 105, 120, 230), font=f_mono)
d1.text((ix0 + 24, iy0 + 38), "4.8 GHz · 128MB L3 · SILICON DIE", fill=(115, 125, 140, 200), font=f_mono)
d1.text((ix0 + 24, iy1 - 32), "SN: 0x7F4A-3320-LEO", fill=(115, 125, 140, 200), font=f_mono)

bx = ix1 - 56
by = iy1 - 42
d1.rectangle([bx, by, bx+32, by+24], fill=(160, 170, 185, 255), outline=(100, 110, 125, 255))
d1.rectangle([bx+4, by+4, bx+12, by+12], fill=(40, 45, 55, 255))
d1.rectangle([bx+20, by+4, bx+28, by+10], fill=(40, 45, 55, 255))
d1.rectangle([bx+14, by+14, bx+24, by+20], fill=(40, 45, 55, 255))

# INNER SQUARE: Perfectly centered inside the backdrop
core_w = 260
core_h = 260
cx0 = (M - core_w) // 2
cy0 = (M - core_h) // 2
cx1 = cx0 + core_w
cy1 = cy0 + core_h
die_center_x = (cx0 + cx1) // 2
die_center_y = (cy0 + cy1) // 2

# Dark sealant rim
d1.rounded_rectangle([cx0-4, cy0-4, cx1+4, cy1+4], radius=14, fill=(35, 40, 50, 255), outline=(15, 20, 26, 255), width=2)

# Solid Saturated Magenta Core Die (#EC2882)
mr, mg, mb = 236, 40, 130
d1.rounded_rectangle([cx0, cy0, cx1, cy1], radius=12, fill=(mr, mg, mb, 255))

# Core divisions
c_grid = (255, 90, 170, 120)
d1.line([(cx0 + core_w//3, cy0), (cx0 + core_w//3, cy1)], fill=c_grid, width=1)
d1.line([(cx0 + 2*core_w//3, cy0), (cx0 + 2*core_w//3, cy1)], fill=c_grid, width=1)
d1.line([(cx0, cy0 + core_h//2), (cx1, cy0 + core_h//2)], fill=c_grid, width=1)

# Inner die beveled rim
d1.line([(cx0+12, cy0+2), (cx1-12, cy0+2)], fill=(255, 180, 220, 220), width=2)
d1.line([(cx0+2, cy0+12), (cx0+2, cy1-12)], fill=(255, 180, 220, 180), width=2)
d1.line([(cx0+12, cy1-2), (cx1-12, cy1-2)], fill=(120, 10, 60, 255), width=2)
d1.line([(cx1-2, cy0+12), (cx1-2, cy1-12)], fill=(120, 10, 60, 255), width=2)

# Mathematically Centered Numeral "7" in white
f_num = get_font(BOLD_FONT, 160)
draw_centered_numeral(d1, die_center_x, die_center_y, "7", f_num, (255, 255, 255, 255), shadow_color=(80, 5, 45, 200))

# Specular glint on corner of die
d1.line([(cx0-6, cy0+4), (cx0+14, cy0+4)], fill=(255, 255, 255, 220), width=2)
d1.line([(cx0+4, cy0-6), (cx0+4, cy0+14)], fill=(255, 255, 255, 220), width=2)

# ==============================================================================
# OPTION 2: CHROME BEVELED HEATSINK FRAME WITH RECESSED MAGENTA DIE
# ==============================================================================
print("2. Rendering Option 2: Chrome Frame (Centered Numeral)...")
im2 = Image.new("RGBA", (M, M), (0, 0, 0, 0))

# Drop shadow
s2 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s2).rounded_rectangle([x0+4, y0+12, x1-4, y1+16], radius=24, fill=(0, 0, 0, 160))
im2 = Image.alpha_composite(s2.filter(ImageFilter.GaussianBlur(16)), im2)

# Full Silver Metallic Body (Polished Aluminum)
metal_body = draw_brushed_metal_rect(ImageDraw.Draw(im2), x0, y0, x1, y1, radius=24, base_rgb=(225, 230, 238), grain_strength=10)
im2 = Image.alpha_composite(im2, metal_body)
d2 = ImageDraw.Draw(im2)

# 4 Corner Hex Mounting Screws on the silver frame
screw_coords = [(x0+24, y0+24), (x1-24, y0+24), (x0+24, y1-24), (x1-24, y1-24)]
for sx, sy in screw_coords:
    d2.ellipse([(sx-12, sy-12), (sx+12, sy+12)], fill=(140, 148, 160, 255), outline=(75, 82, 92, 255), width=2)
    d2.ellipse([(sx-8, sy-8), (sx+8, sy+8)], fill=(185, 192, 202, 255))
    d2.line([(sx-5, sy), (sx+5, sy)], fill=(50, 55, 65, 255), width=2)
    d2.line([(sx, sy-5), (sx, sy+5)], fill=(50, 55, 65, 255), width=2)

# Top laser typography on chrome
d2.text((x0+52, y0+16), "TITAN-X // METALLIC CHASSIS", fill=(90, 100, 115, 230), font=get_font(MONO_FONT, 13))

# Recessed Inner Magenta Square Die
rx0, ry0, rx1, ry1 = x0 + 58, y0 + 58, x1 - 58, y1 - 58
d2.rounded_rectangle([rx0-4, ry0-4, rx1+4, ry1+4], radius=16, fill=(40, 45, 55, 255), outline=(15, 20, 25, 255), width=2)
d2.rounded_rectangle([rx0, ry0, rx1, ry1], radius=14, fill=(240, 30, 120, 255))

# Diagonal specular glass gloss sheen across the magenta die
gloss = Image.new("RGBA", (M, M), (0, 0, 0, 0))
d_gloss = ImageDraw.Draw(gloss)
d_gloss.polygon([(rx0, ry0), (rx0+160, ry0), (rx0, ry0+160)], fill=(255, 255, 255, 60))
gloss = gloss.filter(ImageFilter.GaussianBlur(8))
im2 = Image.alpha_composite(im2, gloss)
d2 = ImageDraw.Draw(im2)

# Perfectly Centered Numeral
f_num2 = get_font(BOLD_FONT, 175)
draw_centered_numeral(d2, (rx0+rx1)//2, (ry0+ry1)//2, "7", f_num2, (255, 245, 250, 255), shadow_color=(60, 5, 30, 200))

# ==============================================================================
# OPTION 3: MODERN MINIMALIST SILVER SoC (APPLE M-SERIES STYLE)
# ==============================================================================
print("3. Rendering Option 3: Modern Minimalist Silver SoC (Centered Numeral)...")
im3 = Image.new("RGBA", (M, M), (0, 0, 0, 0))

s3 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s3).rounded_rectangle([x0+4, y0+12, x1-4, y1+16], radius=24, fill=(0, 0, 0, 160))
im3 = Image.alpha_composite(s3.filter(ImageFilter.GaussianBlur(16)), im3)

d3 = ImageDraw.Draw(im3)
d3.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(18, 22, 28, 255), outline=(45, 55, 68, 255), width=2)

sx0, sy0, sx1, sy1 = x0 + 12, y0 + 12, x1 - 12, y1 - 12
satin_lid = draw_brushed_metal_rect(d3, sx0, sy0, sx1, sy1, radius=20, base_rgb=(235, 238, 244), grain_strength=6)
im3 = Image.alpha_composite(im3, satin_lid)
d3 = ImageDraw.Draw(im3)

cut_sz = 16
d3.polygon([(sx0, sy0+cut_sz), (sx0+cut_sz, sy0), (sx0, sy0)], fill=(18, 22, 28, 255))
d3.polygon([(sx1-cut_sz, sy0), (sx1, sy0+cut_sz), (sx1, sy0)], fill=(18, 22, 28, 255))
d3.polygon([(sx0, sy1-cut_sz), (sx0+cut_sz, sy1), (sx0, sy1)], fill=(18, 22, 28, 255))
d3.polygon([(sx1-cut_sz, sy1), (sx1, sy1-cut_sz), (sx1, sy1)], fill=(18, 22, 28, 255))

mx0, my0, mx1, my1 = x0 + 75, y0 + 75, x1 - 75, y1 - 75
d3.rounded_rectangle([mx0-3, my0-3, mx1+3, my1+3], radius=14, fill=(160, 170, 185, 255), outline=(100, 110, 125, 255), width=1)
d3.rounded_rectangle([mx0, my0, mx1, my1], radius=12, fill=(236, 40, 130, 255))

f_num3 = get_font(BOLD_FONT, 170)
draw_centered_numeral(d3, (mx0+mx1)//2, (my0+my1)//2, "7", f_num3, (255, 255, 255, 255))
d3.text((sx0 + 24, sy1 - 28), "APEX M7 // 3.32 AM", fill=(120, 130, 145, 220), font=get_font(MONO_FONT, 12))

# ==============================================================================
# OPTION 4: CERAMIC BGA WITH SILVER LID & INTEGRATED HEAT PIPE TRACES
# ==============================================================================
print("4. Rendering Option 4: Ceramic Package with Silver Shield (Centered Numeral)...")
im4 = Image.new("RGBA", (M, M), (0, 0, 0, 0))

s4 = Image.new("RGBA", (M, M), (0, 0, 0, 0))
ImageDraw.Draw(s4).rounded_rectangle([x0+4, y0+12, x1-4, y1+16], radius=24, fill=(0, 0, 0, 160))
im4 = Image.alpha_composite(s4.filter(ImageFilter.GaussianBlur(16)), im4)

d4 = ImageDraw.Draw(im4)
d4.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(25, 28, 36, 255), outline=(60, 70, 85, 255), width=2)

d4.rectangle([x0+6, y0+6, x0+26, y0+26], fill=(212, 175, 55, 255))
d4.rectangle([x1-26, y0+6, x1-6, y0+26], fill=(212, 175, 55, 255))
d4.rectangle([x0+6, y1-26, x0+26, y1-6], fill=(212, 175, 55, 255))
d4.rectangle([x1-26, y1-26, x1-6, y1-6], fill=(212, 175, 55, 255))

cx0, cy0, cx1, cy1 = x0 + 32, y0 + 32, x1 - 32, y1 - 32
plate_metal = draw_brushed_metal_rect(d4, cx0, cy0, cx1, cy1, radius=18, base_rgb=(215, 222, 232), grain_strength=14)
im4 = Image.alpha_composite(im4, plate_metal)
d4 = ImageDraw.Draw(im4)

d4.line([(cx0+16, cy0+36), (cx1-16, cy0+36)], fill=(185, 115, 45, 180), width=4)
d4.line([(cx0+16, cy1-36), (cx1-16, cy1-36)], fill=(185, 115, 45, 180), width=4)

qx0, qy0, qx1, qy1 = x0 + 72, y0 + 72, x1 - 72, y1 - 72
d4.rounded_rectangle([qx0-4, qy0-4, qx1+4, qy1+4], radius=14, fill=(212, 175, 55, 255), outline=(255, 230, 120, 255), width=2)
d4.rounded_rectangle([qx0, qy0, qx1, qy1], radius=11, fill=(236, 40, 130, 255))

f_num4 = get_font(BOLD_FONT, 170)
draw_centered_numeral(d4, (qx0+qx1)//2, (qy0+qy1)//2, "7", f_num4, (255, 255, 255, 255), shadow_color=(60, 5, 30, 200))

# Save masters and 80px scales
variants = [
    ("silver_chip_opt1_nickel_ihs", im1, "1. Brushed Nickel IHS (Desktop CPU)", "Silver brushed nickel lid · Laser specs · Inset magenta square die"),
    ("silver_chip_opt2_chrome_chassis", im2, "2. Chrome Frame with Recessed Die", "Polished aluminum chassis · Hex corner screws · Deeply recessed magenta die"),
    ("silver_chip_opt3_minimalist_soc", im3, "3. Minimalist Silver SoC (M-Series)", "Satin silver aluminum monolith · 45° diamond corners · Clean magenta die"),
    ("silver_chip_opt4_ceramic_hybrid", im4, "4. Ceramic Base + Silver Shield", "Ceramic substrate with gold pads · Silver shield · Gold-brazed magenta die")
]

for slug, img, title, desc in variants:
    m_path = f"{OUT_DIR}/{slug}_master.png"
    b_m_path = f"{BRAIN_DIR}/{slug}_master.png"
    img.save(m_path, "PNG")
    img.save(b_m_path, "PNG")
    
    img_80 = img.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS)
    g_path = f"{OUT_DIR}/{slug}_80px.png"
    b_g_path = f"{BRAIN_DIR}/{slug}_80px.png"
    img_80.save(g_path, "PNG")
    img_80.save(b_g_path, "PNG")

# Compose 4-Way Comparison Sheet
sw = 1440
sh = 520
sheet = Image.new("RGBA", (sw, sh), (8, 11, 16, 255))
d_s = ImageDraw.Draw(sheet)

d_s.text((36, 24), "PROCESSOR CHIP GAME BLOCKS — SILVER METALLIC BACKDROP + CENTERED DIE", fill=(240, 245, 255, 255), font=get_font(BOLD_FONT, 22))
d_s.text((36, 56), "Precision Centering Update: Glyph ink bounding box centered perfectly in both X and Y inside the inner colored square", fill=(130, 145, 165, 255), font=get_font(REG_FONT, 13))

card_w = 325
card_h = 410
start_x = 36
gap = 24

for idx, (slug, img, title, desc) in enumerate(variants):
    cx = start_x + idx * (card_w + gap)
    cy = 85
    d_s.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=14, fill=(16, 20, 28, 255), outline=(35, 45, 60, 255), width=1)
    d_s.text((cx + 16, cy + 14), title, fill=(0, 240, 255, 255), font=get_font(BOLD_FONT, 11))
    
    fit_img = img.resize((210, 210), Image.Resampling.LANCZOS)
    d_s.rounded_rectangle([cx + 16, cy + 38, cx + card_w - 16, cy + 258], radius=8, fill=(0, 0, 0, 200))
    sheet.paste(fit_img, (cx + (card_w - 210)//2, cy + 43), fit_img)
    
    d_s.text((cx + 16, cy + 270), desc, fill=(135, 150, 170, 255), font=get_font(REG_FONT, 10))
    d_s.line([(cx + 16, cy + 340), (cx + card_w - 16, cy + 340)], fill=(35, 45, 60, 255), width=1)
    d_s.text((cx + 16, cy + 355), "In-game 80×80px scale:", fill=(110, 125, 145, 255), font=get_font(REG_FONT, 10))
    
    img_80 = img.resize((TARGET_PX, TARGET_PX), Image.Resampling.LANCZOS)
    sheet.paste(img_80, (cx + card_w - TARGET_PX - 20, cy + 320), img_80)

sheet_out = f"{OUT_DIR}/silver_processor_chips_showcase.png"
sheet.save(sheet_out, "PNG")
sheet.save(f"{BRAIN_DIR}/silver_processor_chips_showcase.png", "PNG")
print(f"✓ Saved updated centered Silver Processor Showcase to {sheet_out}")

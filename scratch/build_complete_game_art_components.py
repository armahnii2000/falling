#!/usr/bin/env python3
"""
build_complete_game_art_components.py
Generates the complete set of game art assets for individual components in Falling (Into The Darkness).
Produces isolated, production-ready RGBA PNG assets for:
1. All 11 Block Tiers (Tiers 1-10 + Tier 11 Titan Monolith)
2. Dropper Assembly (Rail, Spigot Carriage, Aiming Laser, Next Preview)
3. Chamber Frame & Translucent Plate (Plate, Floor Bed, Overflow Danger Line)
4. Interactive Controls (SWAP button states, NUDGE button)
5. HUD Gauges & Status Plates (Darkness Purity radial/horizontal, Score Pill, Header)
6. Theme Signature Variants (Theme 2 Sumi Wax Seal & Dropper, Theme 3 CRT Keycap & Gauge, Theme 4 Rotary Dial)
7. Master Texture Atlas + JSON Metadata
"""

import os
import math
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = "/Users/georgearmah/into-the-darkness"
ASSETS_DIR = f"{BASE_DIR}/assets/ui"
FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"
BOLD_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

def get_font(size, bold=True):
    try:
        p = BOLD_FONT_PATH if bold else FONT_PATH
        return ImageFont.truetype(p, size)
    except Exception:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            return ImageFont.load_default()

def apply_bevel(im, bevel_width=3, light_intensity=0.8, shadow_intensity=0.7):
    """Adds a tactile 3D beveled edge highlight and shadow to an RGBA image."""
    arr = np.array(im).astype(np.float32)
    alpha = arr[:, :, 3] / 255.0
    
    # Calculate gradients for lighting
    gy, gx = np.gradient(alpha)
    
    # Key light from top-left (-1, -1)
    light_dir = np.array([-0.7071, -0.7071])
    diffuse = -(gx * light_dir[0] + gy * light_dir[1])
    
    highlight = np.clip(diffuse * light_intensity * 255, 0, 255)
    shadow = np.clip(-diffuse * shadow_intensity * 255, 0, 255)
    
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + highlight - shadow, 0, 255)
        
    return Image.fromarray(arr.astype(np.uint8))

def add_specular_glint(draw, x, y, size=8, color=(255, 255, 255, 220)):
    """Draws a crisp diagonal specular reflection flare at a vertex."""
    draw.line([(x - size, y), (x + size, y)], fill=color, width=1)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=1)
    draw.line([(x - size//2, y - size//2), (x + size//2, y + size//2)], fill=(255, 255, 255, 180), width=2)

print("=== Starting Falling Component Game Art Generation ===")

# ==============================================================================
# SECTION 1: THE 11 BLOCK TIERS (CYBER OBSIDIAN / CORE)
# ==============================================================================
print("\n--- Generating 11 Block Tiers ---")
blocks_dir = f"{ASSETS_DIR}/blocks"
os.makedirs(blocks_dir, exist_ok=True)

# Specification for all 11 tiers
TIER_SPECS = [
    {"tier": 1, "size": 14, "master": 128, "color": (250, 204, 21), "label": "1", "name": "Yellow Pigment Mote"},
    {"tier": 2, "size": 28, "master": 128, "color": (236, 72, 153), "label": "2", "name": "Magenta Pebble"},
    {"tier": 3, "size": 42, "master": 168, "color": (6, 182, 212), "label": "3", "name": "Cyan Stone"},
    {"tier": 4, "size": 56, "master": 224, "color": (37, 99, 235), "label": "4", "name": "Cobalt Brick"},
    {"tier": 5, "size": 70, "master": 280, "color": (124, 58, 237), "label": "5", "name": "Amethyst Slab"},
    {"tier": 6, "size": 84, "master": 336, "color": (190, 18, 60), "label": "6", "name": "Ruby Boulder"},
    {"tier": 7, "size": 80, "master": 320, "color": (13, 148, 136), "label": "7", "name": "Emerald Pillar"},
    {"tier": 8, "size": 90, "master": 360, "color": (180, 83, 9), "label": "8", "name": "Amber Column"},
    {"tier": 9, "size": 100, "master": 400, "color": (51, 65, 85), "label": "9", "name": "Slate Monolith"},
    {"tier": 10, "size": 110, "master": 440, "color": (15, 23, 42), "label": "10", "name": "Midnight Basalt Great Monolith"},
    {"tier": 11, "size": 154, "master": 616, "color": (5, 7, 10), "label": "11", "name": "Titan Obsidian Monolith"},
]

def render_block_tier(spec):
    tier = spec["tier"]
    M = spec["master"]
    target_px = spec["size"]
    r, g, b = spec["color"]
    label = spec["label"]
    
    # 1. Render high-res master
    im = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    pad = int(M * 0.05)
    x0, y0 = pad, pad
    x1, y1 = M - pad, M - pad
    corner = int(M * 0.12) if tier < 11 else int(M * 0.14)
    
    # Ambient occlusion shadow underneath
    shadow = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([x0+2, y0+6, x1-2, y1+10], radius=corner, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=M*0.04))
    im = Image.alpha_composite(shadow, im)
    draw = ImageDraw.Draw(im)
    
    if tier == 11:
        # TIER 11 TITAN MONOLITH: Brushed Titanium Chamfered Frame + Mirror Obsidian Face
        # 1. Outer Titanium Frame
        draw.rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=(180, 190, 205, 255))
        # Metallic gradient simulation
        for yi in range(y0, y1):
            factor = math.sin((yi - y0) / (y1 - y0) * math.pi) * 0.35 + 0.65
            c_line = (int(190 * factor), int(200 * factor), int(215 * factor), 255)
            # subtle horizontal brushed metallic lines
            if yi % 4 == 0:
                draw.line([(x0+corner//2, yi), (x1-corner//2, yi)], fill=c_line, width=1)
        
        # Outer frame bevel highlights
        draw.line([(x0 + corner, y0), (x1 - corner, y0)], fill=(255, 255, 255, 240), width=int(M*0.015))
        draw.line([(x0, y0 + corner), (x0, y1 - corner)], fill=(255, 255, 255, 200), width=int(M*0.015))
        draw.line([(x0 + corner, y1), (x1 - corner, y1)], fill=(70, 75, 85, 255), width=int(M*0.015))
        draw.line([(x1, y0 + corner), (x1, y1 - corner)], fill=(70, 75, 85, 255), width=int(M*0.015))
        
        # 2. Inner Deep Obsidian Core
        inner_pad = int(M * 0.08)
        ix0, iy0 = x0 + inner_pad, y0 + inner_pad
        ix1, iy1 = x1 - inner_pad, y1 - inner_pad
        icorner = int(corner * 0.5)
        
        # Inner recess shadow
        draw.rounded_rectangle([ix0-2, iy0-2, ix1+2, iy1+2], radius=icorner+2, fill=(20, 25, 35, 255))
        # Deep Obsidian Fill
        draw.rounded_rectangle([ix0, iy0, ix1, iy1], radius=icorner, fill=(6, 8, 12, 255))
        
        # Subtle obsidian surface sheen
        for yi in range(iy0, iy1):
            prog = (yi - iy0) / (iy1 - iy0)
            sheen_a = int(18 * (1.0 - prog))
            draw.line([(ix0+icorner, yi), (ix1-icorner, yi)], fill=(255, 255, 255, sheen_a), width=1)
            
        # Vertical center seam division
        cx = (ix0 + ix1) // 2
        draw.line([(cx, iy0), (cx, iy1)], fill=(12, 16, 22, 255), width=int(M*0.012))
        draw.line([(cx+1, iy0), (cx+1, iy1)], fill=(255, 255, 255, 20), width=1)
        
        # Diagonal chamfers at inner corners
        cham = int(M * 0.05)
        draw.line([(ix0, iy0+cham), (ix0+cham, iy0)], fill=(255, 255, 255, 120), width=2)
        draw.line([(ix1-cham, iy0), (ix1, iy0+cham)], fill=(255, 255, 255, 120), width=2)
        
        # Specular glints on top frame
        add_specular_glint(draw, x0 + corner, y0, size=int(M*0.025))
        add_specular_glint(draw, x1 - corner, y0, size=int(M*0.02))
        
        # 3. Bold White "11" Numeral
        font_size = int(M * 0.38)
        font = get_font(font_size, bold=True)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (M - tw) // 2
        ty = (M - th) // 2 - int(M * 0.02)
        
        # Drop shadow for text
        draw.text((tx, ty + int(M*0.015)), label, fill=(0, 0, 0, 220), font=font)
        # Crisp white text
        draw.text((tx, ty), label, fill=(255, 255, 255, 255), font=font)
        
    else:
        # TIERS 1 TO 10: Rich Tactile Polymer Monoliths with Bevels, Seams & Glyphs
        # Base body with rich vertical gradient
        base = Image.new("RGBA", (M, M), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(base)
        bdraw.rounded_rectangle([x0, y0, x1, y1], radius=corner, fill=(r, g, b, 255))
        
        # Apply vertical gradient: top is brighter (key light), bottom absorbs light
        for yi in range(y0, y1):
            prog = (yi - y0) / (y1 - y0)
            # Top bright tint, bottom deep shade
            if prog < 0.5:
                tint = (1.0 - prog * 2) * 45
                line_col = (min(255, int(r + tint)), min(255, int(g + tint)), min(255, int(b + tint)), 255)
            else:
                shade = (prog - 0.5) * 2 * 0.4
                line_col = (int(r * (1.0 - shade)), int(g * (1.0 - shade)), int(b * (1.0 - shade)), 255)
            bdraw.line([(x0+corner//2, yi), (x1-corner//2, yi)], fill=line_col, width=1)
            
        im = Image.alpha_composite(im, base)
        draw = ImageDraw.Draw(im)
        
        # Outer Specular Bevels
        bw = max(2, int(M * 0.025))
        # Top edge specular highlight
        draw.line([(x0 + corner, y0), (x1 - corner, y0)], fill=(255, 255, 255, 220), width=bw)
        # Left edge highlight
        draw.line([(x0, y0 + corner), (x0, y1 - corner)], fill=(255, 255, 255, 170), width=bw)
        # Bottom edge shadow
        draw.line([(x0 + corner, y1), (x1 - corner, y1)], fill=(0, 0, 0, 160), width=bw)
        # Right edge shadow
        draw.line([(x1, y0 + corner), (x1, y1 - corner)], fill=(0, 0, 0, 140), width=bw)
        
        # Inner chamfer border line
        inset = int(M * 0.06)
        draw.rounded_rectangle([x0+inset, y0+inset, x1-inset, y1-inset], radius=max(2, corner-inset), 
                               outline=(255, 255, 255, 40), width=1)
                               
        # Seam divisions for multi-unit blocks (Tiers 2, 3, 4, 6, 8)
        if tier in [2, 3, 4, 6, 8]:
            cx = (x0 + x1) // 2
            cy = (y0 + y1) // 2
            seam_a = 60
            if tier == 2:
                # Vertical seam (2x1 brick feel)
                draw.line([(cx, y0+inset), (cx, y1-inset)], fill=(0, 0, 0, seam_a), width=2)
                draw.line([(cx+1, y0+inset), (cx+1, y1-inset)], fill=(255, 255, 255, 40), width=1)
            elif tier >= 3:
                # Quadrant cross seams
                draw.line([(cx, y0+inset), (cx, y1-inset)], fill=(0, 0, 0, seam_a), width=2)
                draw.line([(cx+1, y0+inset), (cx+1, y1-inset)], fill=(255, 255, 255, 30), width=1)
                draw.line([(x0+inset, cy), (x1-inset, cy)], fill=(0, 0, 0, seam_a), width=2)
                draw.line([(x0+inset, cy+1), (x1-inset, cy+1)], fill=(255, 255, 255, 30), width=1)

        # Specular glint on top-left
        add_specular_glint(draw, x0 + corner, y0 + corner//2, size=int(M*0.02))
        
        # Center Numeral
        font_size = int(M * 0.42) if tier < 10 else int(M * 0.36)
        font = get_font(font_size, bold=True)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (M - tw) // 2
        ty = (M - th) // 2 - int(M * 0.02)
        
        # Inset text shadow
        draw.text((tx, ty + int(M*0.015)), label, fill=(0, 0, 0, 200), font=font)
        # Crisp white face
        draw.text((tx, ty), label, fill=(255, 255, 255, 255), font=font)
        
    # Save High-Res Master
    master_path = f"{blocks_dir}/block_tier_{tier}_master.png"
    im.save(master_path, "PNG")
    
    # Save Exact Wireframe Target Scale (1:1 pixel perfect for drop-in)
    exact_im = im.resize((target_px, target_px), Image.Resampling.LANCZOS)
    exact_path = f"{blocks_dir}/block_tier_{tier}_{target_px}px.png"
    exact_im.save(exact_path, "PNG")
    
    print(f"  ✓ Tier {tier:2d} ({spec['name']}): Saved master ({M}x{M}) and target ({target_px}x{target_px}px)")
    return exact_path

for spec in TIER_SPECS:
    render_block_tier(spec)

# ==============================================================================
# SECTION 2: DROPPER ASSEMBLY (RAIL, SPIGOT, LASER, NEXT PREVIEW)
# ==============================================================================
print("\n--- Generating Dropper Assembly Components ---")
dropper_dir = f"{ASSETS_DIR}/dropper"
os.makedirs(dropper_dir, exist_ok=True)

# 1. Dropper Rail Gantry (Target: 300x8px, Master: 600x16px)
RW, RH = 600, 16
im_rail = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
draw = ImageDraw.Draw(im_rail)
# Milled titanium rail beam
draw.rounded_rectangle([0, 2, RW, RH-2], radius=4, fill=(35, 42, 54, 255))
# Horizontal brushed metal gradient
for yi in range(2, RH-2):
    f = 1.0 - abs(yi - RH//2) / (RH//2)
    col = (int(50 + 35*f), int(60 + 40*f), int(75 + 45*f), 255)
    draw.line([(4, yi), (RW-4, yi)], fill=col, width=1)
# Top specular edge
draw.line([(4, 2), (RW-4, 2)], fill=(200, 215, 235, 220), width=1)
# Central linear guide groove with cyan glow
draw.line([(10, RH//2), (RW-10, RH//2)], fill=(0, 240, 255, 180), width=2)
draw.line([(10, RH//2-1), (RW-10, RH//2-1)], fill=(0, 0, 0, 220), width=1)
# Precision laser millimeter tick marks
for x in range(30, RW-30, 20):
    tick_h = 3 if x % 60 == 0 else 2
    draw.line([(x, RH//2 - tick_h), (x, RH//2 + tick_h)], fill=(255, 255, 255, 140), width=1)
# End bracket hex mounts
draw.rectangle([0, 0, 12, RH], fill=(25, 30, 40, 255))
draw.rectangle([RW-12, 0, RW, RH], fill=(25, 30, 40, 255))
draw.ellipse([3, RH//2-3, 9, RH//2+3], fill=(180, 190, 205, 255))
draw.ellipse([RW-9, RH//2-3, RW-3, RH//2+3], fill=(180, 190, 205, 255))

im_rail.save(f"{dropper_dir}/dropper_rail_master.png")
im_rail_exact = im_rail.resize((300, 8), Image.Resampling.LANCZOS)
im_rail_exact.save(f"{dropper_dir}/dropper_rail_300px.png")
print("  ✓ Dropper Rail: Saved master (600x16) and 300px wireframe fit")

# 2. Dropper Spigot Carriage (Target: 32x24px, Master: 128x96px)
SW, SH = 128, 96
im_spigot = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
draw = ImageDraw.Draw(im_spigot)
# Carriage shadow
draw.rounded_rectangle([10, 8, SW-10, SH-4], radius=12, fill=(0, 0, 0, 120))
# Machined titanium body
draw.rounded_rectangle([8, 4, SW-8, SH-8], radius=10, fill=(45, 52, 65, 255))
# Metallic surface gradient
for yi in range(4, SH-8):
    prog = (yi - 4) / (SH - 12)
    val = int(55 + 25 * math.sin(prog * math.pi))
    draw.line([(14, yi), (SW-14, yi)], fill=(val, val+8, val+18, 255), width=1)
# Top and left specular edge
draw.line([(18, 4), (SW-18, 4)], fill=(220, 235, 255, 230), width=2)
draw.line([(8, 14), (8, SH-18)], fill=(220, 235, 255, 180), width=2)
# Bottom dark bevel
draw.line([(18, SH-8), (SW-18, SH-8)], fill=(15, 20, 28, 255), width=2)
# Recessed center aperture
draw.rounded_rectangle([32, 22, SW-32, SH-26], radius=6, fill=(15, 20, 30, 255))
# Status LED indicators (Cyan)
draw.ellipse([18, 18, 26, 26], fill=(0, 240, 255, 255))
draw.ellipse([SW-26, 18, SW-18, 26], fill=(0, 240, 255, 255))
# Downward injector nozzle
draw.polygon([(SW//2 - 12, SH-8), (SW//2 + 12, SH-8), (SW//2, SH)], fill=(30, 36, 48, 255))
# Emitter optical lens (Glowing cyan focus dot)
draw.ellipse([SW//2 - 6, SH - 12, SW//2 + 6, SH], fill=(0, 240, 255, 255))

im_spigot.save(f"{dropper_dir}/dropper_spigot_carriage_master.png")
im_spigot_exact = im_spigot.resize((32, 24), Image.Resampling.LANCZOS)
im_spigot_exact.save(f"{dropper_dir}/dropper_spigot_carriage_32px.png")
print("  ✓ Dropper Spigot Carriage: Saved master (128x96) and 32x24px wireframe fit")

# 3. Aiming Laser Beam (Target: 4x518px, Master: 16x518px)
LW, LH = 16, 518
im_laser = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
draw = ImageDraw.Draw(im_laser)
# Outer cyan glow aura
for yi in range(LH):
    # slight vertical pulse modulation
    pulse = 0.85 + 0.15 * math.sin(yi * 0.05)
    for xi in range(LW):
        dist = abs(xi - LW//2)
        if dist <= 6:
            alpha = int(pulse * (220 * math.exp(-0.4 * dist * dist)))
            draw.point((xi, yi), fill=(0, 240, 255, alpha))
# Ultra-bright white laser core
draw.line([(LW//2, 0), (LW//2, LH)], fill=(255, 255, 255, 255), width=2)
im_laser.save(f"{dropper_dir}/aim_laser_beam_master.png")
im_laser_exact = im_laser.resize((4, 518), Image.Resampling.LANCZOS)
im_laser_exact.save(f"{dropper_dir}/aim_laser_beam_4px.png")

# Impact Reticle
im_reticle = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
rdraw = ImageDraw.Draw(im_reticle)
rdraw.ellipse([4, 4, 28, 28], outline=(0, 240, 255, 200), width=2)
rdraw.ellipse([10, 10, 22, 22], fill=(0, 240, 255, 120))
rdraw.ellipse([14, 14, 18, 18], fill=(255, 255, 255, 255))
im_reticle.save(f"{dropper_dir}/laser_impact_reticle.png")
print("  ✓ Aiming Laser Beam & Reticle: Saved 4x518px laser and reticle")

# ==============================================================================
# SECTION 3: CHAMBER FRAME & TRANSLUCENT PLATE (9-SLICE)
# ==============================================================================
print("\n--- Generating Chamber Frame & Plate Components ---")
chamber_dir = f"{ASSETS_DIR}/chamber"
os.makedirs(chamber_dir, exist_ok=True)

# 1. Translucent Frosted Glass Chamber Plate (Target: 336x560px)
CW, CH = 336, 560
im_plate = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
pdraw = ImageDraw.Draw(im_plate)
# Smoked borosilicate glass body (35% alpha = ~89/255)
pdraw.rounded_rectangle([0, 0, CW, CH], radius=24, fill=(11, 14, 20, 95))
# Noise diffusion simulation
noise = np.random.normal(0, 4, (CH, CW)).astype(np.float32)
plate_arr = np.array(im_plate).astype(np.float32)
plate_arr[:, :, 0] = np.clip(plate_arr[:, :, 0] + noise, 0, 255)
plate_arr[:, :, 1] = np.clip(plate_arr[:, :, 1] + noise, 0, 255)
plate_arr[:, :, 2] = np.clip(plate_arr[:, :, 2] + noise, 0, 255)
im_plate = Image.fromarray(plate_arr.astype(np.uint8))
pdraw = ImageDraw.Draw(im_plate)
# Crystal refraction edge highlight (1.5px stroke with soft opacity)
pdraw.rounded_rectangle([1, 1, CW-1, CH-1], radius=24, outline=(255, 255, 255, 50), width=2)
# Inner shadow / rim depth
pdraw.rounded_rectangle([3, 3, CW-3, CH-3], radius=22, outline=(0, 0, 0, 80), width=2)
im_plate.save(f"{chamber_dir}/chamber_translucent_plate_336x560.png")
print("  ✓ Translucent Chamber Plate: Saved 336x560px frosted borosilicate glass")

# 2. Chamber Floor Bed (Target: 336x14px, Master: 672x28px)
FW, FH = 672, 28
im_floor = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
fdraw = ImageDraw.Draw(im_floor)
# Titanium base shelf
fdraw.rectangle([0, 4, FW, FH-4], fill=(35, 42, 52, 255))
# Brushed grain
for yi in range(4, FH-4):
    v = int(40 + 20 * math.sin((yi-4)/(FH-8) * math.pi))
    fdraw.line([(0, yi), (FW, yi)], fill=(v, v+5, v+12, 255), width=1)
# Specular top edge (where blocks land)
fdraw.line([(0, 4), (FW, 4)], fill=(220, 235, 255, 230), width=2)
# Bottom dark rim
fdraw.line([(0, FH-4), (FW, FH-4)], fill=(15, 18, 24, 255), width=2)
# Corner impact dampener bolts
fdraw.ellipse([8, FH//2-4, 16, FH//2+4], fill=(160, 175, 195, 255))
fdraw.ellipse([FW-16, FH//2-4, FW-8, FH//2+4], fill=(160, 175, 195, 255))
im_floor.save(f"{chamber_dir}/chamber_floor_bed_master.png")
im_floor_exact = im_floor.resize((336, 14), Image.Resampling.LANCZOS)
im_floor_exact.save(f"{chamber_dir}/chamber_floor_bed_336px.png")
print("  ✓ Chamber Floor Bed: Saved master and 336x14px shelf")

# 3. Overflow Danger Line (Target: 336x6px, Master: 672x12px)
DW, DH = 672, 12
im_danger = Image.new("RGBA", (DW, DH), (0, 0, 0, 0))
ddraw = ImageDraw.Draw(im_danger)
# Glowing dashed hazard stripe
for x in range(10, DW-10, 24):
    ddraw.line([(x, DH//2), (x+14, DH//2)], fill=(239, 68, 68, 220), width=3)
    ddraw.line([(x+2, DH//2), (x+12, DH//2)], fill=(255, 180, 180, 255), width=1)
im_danger.save(f"{chamber_dir}/overflow_danger_line_master.png")
im_danger_exact = im_danger.resize((336, 6), Image.Resampling.LANCZOS)
im_danger_exact.save(f"{chamber_dir}/overflow_danger_line_336px.png")

# Danger Warning Badge
im_badge = Image.new("RGBA", (140, 32), (0, 0, 0, 0))
bdraw = ImageDraw.Draw(im_badge)
bdraw.rounded_rectangle([0, 0, 140, 32], radius=6, fill=(239, 68, 68, 40), outline=(239, 68, 68, 220), width=1)
font_badge = get_font(12, bold=True)
bdraw.text((12, 8), "⚠ OVERFLOW LIMIT", fill=(239, 68, 68, 255), font=font_badge)
im_badge.save(f"{chamber_dir}/overflow_warning_badge.png")
print("  ✓ Overflow Danger Line & Badge: Saved 336px warning assets")

# ==============================================================================
# SECTION 4: INTERACTIVE CONTROLS & BUTTONS
# ==============================================================================
print("\n--- Generating Controls & Button States ---")
controls_dir = f"{ASSETS_DIR}/controls"
os.makedirs(controls_dir, exist_ok=True)

def render_swap_button(state="normal", size=64):
    """Renders circular glowing SWAP button (Normal, Hover, Pressed)."""
    M = 256
    im = Image.new("RGBA", (M, M), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    pad = 16
    x0, y0, x1, y1 = pad, pad, M - pad, M - pad
    cx, cy = M // 2, M // 2
    
    # Outer Glow Ring
    glow_a = 220 if state == "hover" else (160 if state == "normal" else 240)
    glow_col = (0, 240, 255, glow_a)
    draw.ellipse([x0-6, y0-6, x1+6, y1+6], outline=glow_col, width=6)
    
    # Milled Titanium Bezel
    draw.ellipse([x0, y0, x1, y1], fill=(45, 52, 65, 255))
    draw.ellipse([x0, y0, x1, y1], outline=(180, 195, 215, 240), width=4)
    
    # Inner Obsidian Glass Core
    core_pad = 28
    draw.ellipse([x0+core_pad, y0+core_pad, x1-core_pad, y1-core_pad], fill=(12, 16, 24, 255))
    if state == "pressed":
        # Depressed shadow
        draw.ellipse([x0+core_pad, y0+core_pad, x1-core_pad, y1-core_pad], fill=(6, 8, 12, 255))
        draw.ellipse([x0+core_pad, y0+core_pad, x1-core_pad, y1-core_pad], outline=(0, 240, 255, 120), width=3)
    else:
        # Subtle glass specular arc
        draw.arc([x0+core_pad+4, y0+core_pad+4, x1-core_pad-4, y1-core_pad-4], start=180, end=330, 
                 fill=(255, 255, 255, 120), width=3)
                 
    # Rotating Swap Arrows Glyph (⇋ / ↻)
    arrow_col = (255, 255, 255, 255) if state != "normal" else (0, 240, 255, 255)
    r_arc = (M - core_pad*2) // 4
    # Top arc with arrow
    draw.arc([cx - r_arc, cy - r_arc - 16, cx + r_arc, cy + r_arc - 16], start=200, end=340, fill=arrow_col, width=4)
    # Bottom arc with arrow
    draw.arc([cx - r_arc, cy - r_arc + 16, cx + r_arc, cy + r_arc + 16], start=20, end=160, fill=arrow_col, width=4)
    
    # "SWAP" Typography
    font = get_font(28, bold=True)
    bbox = draw.textbbox((0, 0), "SWAP", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((M - tw)//2, (M - th)//2), "SWAP", fill=arrow_col, font=font)
    
    # Save master and target
    im.save(f"{controls_dir}/btn_swap_circular_{state}_master.png")
    exact = im.resize((size, size), Image.Resampling.LANCZOS)
    exact.save(f"{controls_dir}/btn_swap_circular_{state}_{size}px.png")
    return exact

for st in ["normal", "hover", "pressed"]:
    render_swap_button(st, size=64)
print("  ✓ SWAP Circular Button: Saved Normal, Hover, and Pressed states (64px)")

# Pill-shaped SWAP button (120x48px)
def render_swap_pill(state="normal", w=120, h=48):
    M_W, M_H = w * 2, h * 2
    im = Image.new("RGBA", (M_W, M_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    pad = 8
    glow_a = 220 if state == "hover" else (160 if state == "normal" else 240)
    draw.rounded_rectangle([pad-4, pad-4, M_W-pad+4, M_H-pad+4], radius=M_H//2, 
                           outline=(0, 240, 255, glow_a), width=4)
    draw.rounded_rectangle([pad, pad, M_W-pad, M_H-pad], radius=M_H//2, 
                           fill=(15, 23, 42, 255), outline=(140, 160, 185, 220), width=2)
                           
    arrow_col = (255, 255, 255, 255) if state != "normal" else (0, 240, 255, 255)
    font = get_font(24, bold=True)
    txt = "SWAP ⇋"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((M_W - tw)//2, (M_H - th)//2), txt, fill=arrow_col, font=font)
    
    im.save(f"{controls_dir}/btn_swap_pill_{state}_master.png")
    exact = im.resize((w, h), Image.Resampling.LANCZOS)
    exact.save(f"{controls_dir}/btn_swap_pill_{state}_{w}x{h}px.png")
    return exact

for st in ["normal", "hover", "pressed"]:
    render_swap_pill(st)
print("  ✓ SWAP Pill Button: Saved Normal, Hover, and Pressed states (120x48px)")

# NUDGE Button (70x48px)
def render_nudge_pill(state="normal", w=70, h=48):
    M_W, M_H = w * 2, h * 2
    im = Image.new("RGBA", (M_W, M_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    pad = 8
    draw.rounded_rectangle([pad, pad, M_W-pad, M_H-pad], radius=M_H//2, 
                           fill=(20, 28, 45, 255), outline=(100, 116, 139, 200), width=2)
    font = get_font(20, bold=True)
    txt = "NUDGE"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((M_W - tw)//2, (M_H - th)//2), txt, fill=(203, 213, 225, 220), font=font)
    
    exact = im.resize((w, h), Image.Resampling.LANCZOS)
    exact.save(f"{controls_dir}/btn_nudge_{state}_{w}x{h}px.png")

render_nudge_pill("normal")
render_nudge_pill("pressed")
print("  ✓ NUDGE Button: Saved Normal and Pressed states (70x48px)")

# ==============================================================================
# SECTION 5: HUD GAUGES & STATUS PLATES
# ==============================================================================
print("\n--- Generating HUD Gauges & Status Plates ---")
hud_dir = f"{ASSETS_DIR}/hud"
os.makedirs(hud_dir, exist_ok=True)

# 1. Darkness Purity Radial Gauge (Target: 80x80px, Master: 240x240px)
GW, GH = 240, 240
im_gauge = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(im_gauge)
pad = 12
# Outer frosted bezel
gdraw.ellipse([pad, pad, GW-pad, GH-pad], fill=(15, 23, 42, 230), outline=(70, 85, 110, 200), width=4)
# Circular progress track (64% purity as in concept art)
# 64% of 360 deg = 230 deg
gdraw.arc([pad+14, pad+14, GW-pad-14, GH-pad-14], start=135, end=135 + int(270 * 0.64), 
          fill=(0, 240, 255, 255), width=8)
# Track background guide
gdraw.arc([pad+14, pad+14, GW-pad-14, GH-pad-14], start=135 + int(270 * 0.64), end=135 + 270, 
          fill=(30, 41, 59, 180), width=4)
# Inner obsidian dark core
core_pad = 42
gdraw.ellipse([pad+core_pad, pad+core_pad, GW-pad-core_pad, GH-pad-core_pad], fill=(6, 8, 12, 255))
# Text
f_title = get_font(18, bold=True)
bbox_t = gdraw.textbbox((0, 0), "BLACKNESS:", font=f_title)
gdraw.text(((GW - (bbox_t[2]-bbox_t[0]))//2, GH//2 - 28), "BLACKNESS:", fill=(148, 163, 184, 220), font=f_title)
f_val = get_font(38, bold=True)
bbox_v = gdraw.textbbox((0, 0), "64%", font=f_val)
gdraw.text(((GW - (bbox_v[2]-bbox_v[0]))//2, GH//2 - 6), "64%", fill=(255, 255, 255, 255), font=f_val)

im_gauge.save(f"{hud_dir}/hud_purity_gauge_radial_master.png")
im_gauge_exact = im_gauge.resize((80, 80), Image.Resampling.LANCZOS)
im_gauge_exact.save(f"{hud_dir}/hud_purity_gauge_radial_80px.png")
print("  ✓ Darkness Purity Radial Gauge: Saved 80x80px neon radial meter")

# 2. Score Capsule Pill (Target: 110x44px, Master: 220x88px)
PW, PH = 220, 88
im_score = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(im_score)
sdraw.rounded_rectangle([4, 4, PW-4, PH-4], radius=PH//2, fill=(15, 23, 42, 220), outline=(70, 85, 110, 200), width=2)
f_st = get_font(18, bold=True)
sdraw.text((24, 14), "SCORE:", fill=(148, 163, 184, 220), font=f_st)
f_sv = get_font(32, bold=True)
sdraw.text((24, 38), "24,850", fill=(255, 255, 255, 255), font=f_sv)
im_score.save(f"{hud_dir}/hud_score_pill_master.png")
im_score_exact = im_score.resize((110, 44), Image.Resampling.LANCZOS)
im_score_exact.save(f"{hud_dir}/hud_score_pill_110x44px.png")

# 3. Next Block Capsule (Target: 110x44px, Master: 220x88px)
im_next = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
ndraw = ImageDraw.Draw(im_next)
ndraw.rounded_rectangle([4, 4, PW-4, PH-4], radius=PH//2, fill=(15, 23, 42, 220), outline=(70, 85, 110, 200), width=2)
ndraw.text((24, 26), "NEXT", fill=(148, 163, 184, 220), font=get_font(24, bold=True))
# Draw mini preview 3D cube inside
mini_cube = Image.open(f"{blocks_dir}/block_tier_2_28px.png").resize((48, 48), Image.Resampling.LANCZOS)
im_next.paste(mini_cube, (PW - 68, (PH - 48)//2), mini_cube)
im_next.save(f"{hud_dir}/hud_next_capsule_master.png")
im_next_exact = im_next.resize((110, 44), Image.Resampling.LANCZOS)
im_next_exact.save(f"{hud_dir}/hud_next_capsule_110x44px.png")
print("  ✓ HUD Header Pills: Saved Score and Next-Block capsules")

# 4. Master HUD Header Assembly (Target: 342x60px)
HW, HH = 342, 60
im_header = Image.new("RGBA", (HW, HH), (0, 0, 0, 0))
im_header.paste(im_score_exact, (0, 8), im_score_exact)
im_header.paste(im_gauge_exact.resize((60, 60), Image.Resampling.LANCZOS), ((HW - 60)//2, 0), im_gauge_exact.resize((60, 60), Image.Resampling.LANCZOS))
im_header.paste(im_next_exact, (HW - 110, 8), im_next_exact)
im_header.save(f"{hud_dir}/hud_header_complete_342x60px.png")
print("  ✓ Master HUD Header Assembly: Saved 342x60px composite")

# ==============================================================================
# SECTION 6: THEME SIGNATURE VARIANTS (THEME 2 SUMI INK & THEME 3 CRT)
# ==============================================================================
print("\n--- Generating Theme Signature Variants ---")
themes_ui_dir = f"{ASSETS_DIR}/themes"
os.makedirs(themes_ui_dir, exist_ok=True)

# 1. Theme 2: Cinnabar Red Wax Seal "換" (Swap) Button (Target: 64x64px, Master: 256x256px)
MW, MH = 256, 256
im_seal = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(im_seal)
# Irregular natural wax edges
cx, cy, r_seal = MW//2, MH//2, 100
for angle in range(0, 360, 4):
    rad = math.radians(angle)
    # Organic wax wobble
    wobble = 1.0 + 0.08 * math.sin(angle * 6 * math.pi / 180) + 0.04 * math.cos(angle * 3 * math.pi / 180)
    rx = int(cx + r_seal * wobble * math.cos(rad))
    ry = int(cy + r_seal * wobble * math.sin(rad))
    sdraw.ellipse([rx-16, ry-16, rx+16, ry+16], fill=(168, 48, 38, 255))
# Solid central wax disc
sdraw.ellipse([cx-80, cy-80, cx+80, cy+80], fill=(185, 52, 42, 255))
# Beveled stamp rim
sdraw.ellipse([cx-72, cy-72, cx+72, cy+72], outline=(130, 32, 24, 255), width=6)
# Carved kanji "換" (Swap)
f_kanji = get_font(96, bold=True)
bbox_k = sdraw.textbbox((0, 0), "換", font=f_kanji)
kw, kh = bbox_k[2] - bbox_k[0], bbox_k[3] - bbox_k[1]
# Carved depth shadow
sdraw.text(((MW - kw)//2, (MH - kh)//2 - 10), "換", fill=(100, 22, 16, 255), font=f_kanji)
sdraw.text(((MW - kw)//2 - 2, (MH - kh)//2 - 12), "換", fill=(210, 75, 62, 255), font=f_kanji)

im_seal.save(f"{themes_ui_dir}/theme2_wax_seal_swap_master.png")
im_seal_exact = im_seal.resize((64, 64), Image.Resampling.LANCZOS)
im_seal_exact.save(f"{themes_ui_dir}/theme2_wax_seal_swap_64px.png")
print("  ✓ Theme 2 Wax Seal SWAP Button: Saved stamped cinnabar seal (64px)")

# 2. Theme 2: Calligraphic Red Enso Danger Arc
im_enso = Image.new("RGBA", (336, 120), (0, 0, 0, 0))
edraw = ImageDraw.Draw(im_enso)
# Calligraphic sweeping brushstroke arc
for t in np.linspace(0.1, 0.9, 120):
    rad = math.pi * t
    bx = int(168 - 145 * math.cos(rad))
    by = int(110 - 70 * math.sin(rad))
    thick = int(6 + 8 * math.sin(t * math.pi))
    alpha = int(220 * math.sin(t * math.pi))
    edraw.ellipse([bx - thick, by - thick, bx + thick, by + thick], fill=(185, 45, 38, alpha))
im_enso.save(f"{themes_ui_dir}/theme2_enso_danger_arc_336px.png")
print("  ✓ Theme 2 Enso Danger Arc: Saved 336px calligraphic brushstroke")

# 3. Theme 3: Cherry MX Keycap SWAP Button
im_key = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
kdraw = ImageDraw.Draw(im_key)
# Base keycap trapezoid
kdraw.polygon([(16, 112), (112, 112), (96, 24), (32, 24)], fill=(28, 25, 22, 255))
# Dish top face
kdraw.rounded_rectangle([32, 24, 96, 76], radius=6, fill=(38, 34, 30, 255), outline=(60, 54, 48, 255), width=2)
# Amber glowing legend
f_key = get_font(18, bold=True)
kdraw.text((42, 42), "SWAP", fill=(251, 191, 36, 255), font=f_key)
im_key.save(f"{themes_ui_dir}/theme3_cherry_keycap_swap_master.png")
im_key.resize((64, 64), Image.Resampling.LANCZOS).save(f"{themes_ui_dir}/theme3_cherry_keycap_swap_64px.png")
print("  ✓ Theme 3 Cherry MX Keycap SWAP: Saved mechanical keycap (64px)")

# ==============================================================================
# SECTION 7: MASTER UI TEXTURE ATLAS & JSON METADATA
# ==============================================================================
print("\n--- Packaging Master UI Texture Atlas ---")
atlas_dir = f"{ASSETS_DIR}/atlas"
os.makedirs(atlas_dir, exist_ok=True)

# Collect all generated 1:1 components into an organized texture atlas
atlas_items = [
    # Blocks
    {"id": "block_tier_1", "path": f"{blocks_dir}/block_tier_1_14px.png", "category": "block", "tier": 1},
    {"id": "block_tier_2", "path": f"{blocks_dir}/block_tier_2_28px.png", "category": "block", "tier": 2},
    {"id": "block_tier_3", "path": f"{blocks_dir}/block_tier_3_42px.png", "category": "block", "tier": 3},
    {"id": "block_tier_4", "path": f"{blocks_dir}/block_tier_4_56px.png", "category": "block", "tier": 4},
    {"id": "block_tier_5", "path": f"{blocks_dir}/block_tier_5_70px.png", "category": "block", "tier": 5},
    {"id": "block_tier_6", "path": f"{blocks_dir}/block_tier_6_84px.png", "category": "block", "tier": 6},
    {"id": "block_tier_7", "path": f"{blocks_dir}/block_tier_7_80px.png", "category": "block", "tier": 7},
    {"id": "block_tier_8", "path": f"{blocks_dir}/block_tier_8_90px.png", "category": "block", "tier": 8},
    {"id": "block_tier_9", "path": f"{blocks_dir}/block_tier_9_100px.png", "category": "block", "tier": 9},
    {"id": "block_tier_10", "path": f"{blocks_dir}/block_tier_10_110px.png", "category": "block", "tier": 10},
    {"id": "block_tier_11_titan", "path": f"{blocks_dir}/block_tier_11_154px.png", "category": "block", "tier": 11},
    # Dropper
    {"id": "dropper_rail", "path": f"{dropper_dir}/dropper_rail_300px.png", "category": "dropper"},
    {"id": "dropper_spigot", "path": f"{dropper_dir}/dropper_spigot_carriage_32px.png", "category": "dropper"},
    {"id": "aim_reticle", "path": f"{dropper_dir}/laser_impact_reticle.png", "category": "dropper"},
    # Chamber
    {"id": "chamber_floor", "path": f"{chamber_dir}/chamber_floor_bed_336px.png", "category": "chamber"},
    {"id": "overflow_danger", "path": f"{chamber_dir}/overflow_danger_line_336px.png", "category": "chamber"},
    {"id": "overflow_badge", "path": f"{chamber_dir}/overflow_warning_badge.png", "category": "chamber"},
    # Controls
    {"id": "btn_swap_normal", "path": f"{controls_dir}/btn_swap_circular_normal_64px.png", "category": "control"},
    {"id": "btn_swap_hover", "path": f"{controls_dir}/btn_swap_circular_hover_64px.png", "category": "control"},
    {"id": "btn_swap_pressed", "path": f"{controls_dir}/btn_swap_circular_pressed_64px.png", "category": "control"},
    {"id": "btn_swap_pill", "path": f"{controls_dir}/btn_swap_pill_normal_120x48px.png", "category": "control"},
    {"id": "btn_nudge", "path": f"{controls_dir}/btn_nudge_normal_70x48px.png", "category": "control"},
    # HUD
    {"id": "hud_purity_gauge", "path": f"{hud_dir}/hud_purity_gauge_radial_80px.png", "category": "hud"},
    {"id": "hud_score_pill", "path": f"{hud_dir}/hud_score_pill_110x44px.png", "category": "hud"},
    {"id": "hud_next_capsule", "path": f"{hud_dir}/hud_next_capsule_110x44px.png", "category": "hud"},
    # Themes
    {"id": "theme2_wax_seal", "path": f"{themes_ui_dir}/theme2_wax_seal_swap_64px.png", "category": "theme_variant"},
    {"id": "theme3_keycap", "path": f"{themes_ui_dir}/theme3_cherry_keycap_swap_64px.png", "category": "theme_variant"},
]

ATLAS_SIZE = 1024
atlas_img = Image.new("RGBA", (ATLAS_SIZE, ATLAS_SIZE), (0, 0, 0, 0))
atlas_meta = {"width": ATLAS_SIZE, "height": ATLAS_SIZE, "elements": {}}

# Simple row-based bin packing
curr_x, curr_y = 16, 16
row_max_h = 0

for item in atlas_items:
    img = Image.open(item["path"]).convert("RGBA")
    w, h = img.size
    
    if curr_x + w + 16 > ATLAS_SIZE:
        curr_x = 16
        curr_y += row_max_h + 16
        row_max_h = 0
        
    if curr_y + h + 16 > ATLAS_SIZE:
        print(f"Warning: Atlas overflow on {item['id']}")
        break
        
    atlas_img.paste(img, (curr_x, curr_y), img)
    atlas_meta["elements"][item["id"]] = {
        "x": curr_x, "y": curr_y, "width": w, "height": h,
        "category": item["category"],
        "source_file": os.path.basename(item["path"])
    }
    
    curr_x += w + 16
    row_max_h = max(row_max_h, h)

atlas_img.save(f"{atlas_dir}/falling_ui_atlas.png")
with open(f"{atlas_dir}/falling_ui_atlas.json", "w") as f:
    json.dump(atlas_meta, f, indent=2)

print(f"  ✓ Master Texture Atlas generated: {atlas_dir}/falling_ui_atlas.png ({len(atlas_meta['elements'])} components packed)")
print("=== Component Game Art Generation Complete ===")

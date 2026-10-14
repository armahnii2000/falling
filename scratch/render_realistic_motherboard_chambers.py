#!/usr/bin/env python3
"""
render_realistic_motherboard_chambers.py
Constructs production-grade, photorealistic motherboard game chambers for Falling:
1. Modern Matte Black Workstation Motherboard (ASUS ROG / Enterprise style)
2. Classic Emerald Server Motherboard (Intel/Supermicro server style)
Populated with the new Silver Metallic Processor Chip Blocks (inner colored die).

Outputs:
- assets/ui/tech_explorations/realistic_motherboard_black_preview.png
- assets/ui/tech_explorations/realistic_motherboard_emerald_preview.png
- assets/ui/tech_explorations/realistic_motherboards_showcase.png
Mirrored to brain directory.
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = "/Users/georgearmah/into-the-darkness"
OUT_DIR = f"{BASE_DIR}/assets/ui/tech_explorations"
BRAIN_DIR = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"

SCALE = 2
W = 390 * SCALE
H = 844 * SCALE

CW = 336 * SCALE
CH = 560 * SCALE
CH_X0 = 27 * SCALE
CH_Y0 = 140 * SCALE
CH_X1 = CH_X0 + CW
CH_Y1 = CH_Y0 + CH

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
MONO_FONT = "/System/Library/Fonts/Menlo.ttc"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, int(size * SCALE))
    except Exception:
        return ImageFont.load_default()

# Load the realistic motherboard source photos
black_mb_path = f"{BRAIN_DIR}/motherboard_pcb_topdown_1791988126479.jpg"
emerald_mb_path = f"{BRAIN_DIR}/emerald_server_motherboard_macro_1791988135704.jpg"

black_mb_raw = Image.open(black_mb_path).convert("RGBA")
emerald_mb_raw = Image.open(emerald_mb_path).convert("RGBA")

# Load silver chip blocks
chip_silver_path = f"{OUT_DIR}/silver_chip_opt1_nickel_ihs_master.png"
chip_silver = Image.open(chip_silver_path).convert("RGBA")

titan_path = f"{BASE_DIR}/assets/ui/blocks/block_tier_11_154px.png"
titan_img = Image.open(titan_path).convert("RGBA")

def build_phone_chamber_mockup(mb_img, theme_title, theme_sub, is_green=False):
    # Base Canvas (bedroom gloom 3:32 AM)
    base = Image.new("RGBA", (W, H), (10, 12, 16, 255))
    
    # Notifications Layer (faintly blurred behind the motherboard)
    notif = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_notif = ImageDraw.Draw(notif)
    f_nt = get_font(BOLD_FONT, 12)
    f_nb = get_font(REG_FONT, 11)
    f_tm = get_font(REG_FONT, 10)
    
    cx0, cy0, cx1, cy1 = 36 * SCALE, 270 * SCALE, 354 * SCALE, 334 * SCALE
    d_notif.rounded_rectangle([cx0, cy0, cx1, cy1], radius=12*SCALE, fill=(35, 42, 54, 210), outline=(75, 90, 110, 160), width=1*SCALE)
    d_notif.text((cx0 + 14*SCALE, cy0 + 10*SCALE), "SLACK • build-pipeline", fill=(225, 230, 240, 220), font=f_nt)
    d_notif.text((cx1 - 56*SCALE, cy0 + 10*SCALE), "3:28 AM", fill=(145, 155, 170, 180), font=f_tm)
    d_notif.text((cx0 + 14*SCALE, cy0 + 28*SCALE), "Build #4028 failed: NullPointerException in CoreEngine", fill=(175, 185, 200, 200), font=f_nb)
    
    cy0_2, cy1_2 = cy0 + 78 * SCALE, cy1 + 78 * SCALE
    d_notif.rounded_rectangle([cx0, cy0_2, cx1, cy1_2], radius=12*SCALE, fill=(35, 42, 54, 210), outline=(75, 90, 110, 160), width=1*SCALE)
    d_notif.text((cx0 + 14*SCALE, cy0_2 + 10*SCALE), "MESSAGES • Sarah", fill=(225, 230, 240, 220), font=f_nt)
    d_notif.text((cx1 - 56*SCALE, cy0_2 + 10*SCALE), "3:30 AM", fill=(145, 155, 170, 180), font=f_tm)
    d_notif.text((cx0 + 14*SCALE, cy0_2 + 28*SCALE), "Are you still awake looking at code? Please go to sleep...", fill=(175, 185, 200, 200), font=f_nb)
    
    notif = notif.filter(ImageFilter.GaussianBlur(6 * SCALE))
    base = Image.alpha_composite(base, notif)
    
    # Crop and scale the motherboard image to fit the chamber area (336x560)
    # Target aspect ratio is 336 / 560 = 0.6
    mb_w, mb_h = mb_img.size
    # Center crop vertical slice
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
    
    # Apply rounded corner mask and subtle transparency so notifications glow through softly
    ch_mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(ch_mask).rounded_rectangle([0, 0, CW, CH], radius=16*SCALE, fill=220) # 86% opacity
    
    # Chamber plate layer
    ch_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mb_scaled.putalpha(ch_mask)
    ch_layer.paste(mb_scaled, (CH_X0, CH_Y0), mb_scaled)
    
    # Outer motherboard chassis bezel / retaining brackets
    d_ch = ImageDraw.Draw(ch_layer)
    bezel_col = (45, 110, 75, 255) if is_green else (75, 90, 110, 255)
    d_ch.rounded_rectangle([CH_X0, CH_Y0, CH_X1, CH_Y1], radius=16*SCALE, outline=bezel_col, width=2*SCALE)
    d_ch.rounded_rectangle([CH_X0+2*SCALE, CH_Y0+2*SCALE, CH_X1-2*SCALE, CH_Y1-2*SCALE], radius=14*SCALE, outline=(15, 20, 28, 200), width=1*SCALE)
    
    # Danger limit line across the motherboard
    danger_y = CH_Y0 + 96 * SCALE
    d_ch.line([(CH_X0 + 8*SCALE, danger_y), (CH_X1 - 8*SCALE, danger_y)], fill=(240, 50, 65, 240), width=2*SCALE)
    f_warn = get_font(MONO_FONT, 8)
    d_ch.text((CH_X0 + 54*SCALE, danger_y - 12*SCALE), "⚠ VBUS_OVERVOLTAGE_LIMIT // BUFFER OVERFLOW", fill=(255, 90, 90, 230), font=f_warn)
    
    # Chamber floor: LGA CPU Socket Retention Bed at the bottom
    floor_y0 = CH_Y1 - 20 * SCALE
    floor_y1 = CH_Y1 - 2 * SCALE
    d_ch.rounded_rectangle([CH_X0 + 8*SCALE, floor_y0, CH_X1 - 8*SCALE, floor_y1], radius=4*SCALE, fill=(25, 30, 40, 255), outline=(90, 105, 125, 255), width=1*SCALE)
    # Gold contact pins
    for px in range(int(CH_X0 + 16*SCALE), int(CH_X1 - 16*SCALE), int(8*SCALE)):
        d_ch.line([(px, floor_y0 + 3*SCALE), (px, floor_y1 - 3*SCALE)], fill=(255, 215, 0, 240), width=2*SCALE)
        d_ch.ellipse([(px-2*SCALE, floor_y0 + 2*SCALE), (px+2*SCALE, floor_y0 + 6*SCALE)], fill=(255, 240, 180, 255))
        
    base = Image.alpha_composite(base, ch_layer)
    
    # Settled Blocks on the Motherboard
    blocks_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # Titan Monolith (Tier 11) - 154x154px at bottom center
    t_w, t_h = int(154 * SCALE), int(154 * SCALE)
    titan_scaled = titan_img.resize((t_w, t_h), Image.Resampling.LANCZOS)
    tx = (W - t_w) // 2
    ty = floor_y0 - t_h
    blocks_layer.paste(titan_scaled, (tx, ty), titan_scaled)
    
    # Silver Chip Block (Dropping block, 80x80px at 2x = 160x160px)
    chip_w = 80 * SCALE
    chip_scaled = chip_silver.resize((chip_w, chip_w), Image.Resampling.LANCZOS)
    drop_x = (W - chip_w) // 2
    drop_y = CH_Y0 + 115 * SCALE
    blocks_layer.paste(chip_scaled, (drop_x, drop_y), chip_scaled)
    
    base = Image.alpha_composite(base, blocks_layer)
    
    # Dropper Assembly (SMT Pick-and-Place head with laser)
    drop_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_d = ImageDraw.Draw(drop_layer)
    rail_y = CH_Y0 + 32 * SCALE
    rail_x0 = CH_X0 + 16 * SCALE
    rail_x1 = CH_X1 - 16 * SCALE
    d_d.rounded_rectangle([rail_x0, rail_y, rail_x1, rail_y + 8*SCALE], radius=4*SCALE, fill=(35, 44, 56, 255), outline=(85, 100, 120, 255), width=1*SCALE)
    d_d.line([(rail_x0+4*SCALE, rail_y+4*SCALE), (rail_x1-4*SCALE, rail_y+4*SCALE)], fill=(220, 230, 245, 255), width=2*SCALE)
    
    # SMT Head
    spigot_x = W // 2
    head_w = 44 * SCALE
    head_h = 24 * SCALE
    hx0 = spigot_x - head_w // 2
    hy0 = rail_y - 6 * SCALE
    hx1 = spigot_x + head_w // 2
    hy1 = hy0 + head_h
    d_d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=6*SCALE, fill=(24, 30, 40, 255), outline=(95, 115, 140, 255), width=2*SCALE)
    d_d.rectangle([spigot_x - 6*SCALE, hy1, spigot_x + 6*SCALE, hy1 + 10*SCALE], fill=(185, 195, 210, 255))
    d_d.text((hx0 + 6*SCALE, hy0 + 6*SCALE), "SMT_PnP_A1", fill=(0, 240, 255, 240), font=get_font(MONO_FONT, 7))
    
    # Laser crosshair
    laser_y0 = hy1 + 10 * SCALE
    laser_y1 = drop_y
    d_d.line([(spigot_x, laser_y0), (spigot_x, laser_y1)], fill=(0, 240, 255, 160), width=2*SCALE)
    d_d.ellipse([(spigot_x - 8*SCALE, laser_y1 - 8*SCALE), (spigot_x + 8*SCALE, laser_y1 + 8*SCALE)], outline=(0, 240, 255, 220), width=1*SCALE)
    d_d.line([(spigot_x - 12*SCALE, laser_y1), (spigot_x + 12*SCALE, laser_y1)], fill=(0, 240, 255, 240), width=1*SCALE)
    d_d.line([(spigot_x, laser_y1 - 12*SCALE), (spigot_x, laser_y1 + 12*SCALE)], fill=(0, 240, 255, 240), width=1*SCALE)
    
    base = Image.alpha_composite(base, drop_layer)
    
    # Motherboard BIOS Telemetry Header
    hud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_hud = ImageDraw.Draw(hud)
    hud_y0 = 56 * SCALE
    hud_y1 = 124 * SCALE
    d_hud.rounded_rectangle([CH_X0, hud_y0, CH_X1, hud_y1], radius=10*SCALE, fill=(16, 22, 30, 245), outline=(55, 70, 90, 255), width=1*SCALE)
    d_hud.text((CH_X0 + 16*SCALE, hud_y0 + 10*SCALE), theme_title, fill=(245, 248, 255, 255), font=get_font(BOLD_FONT, 13))
    
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

print("Rendering Realistic Black Motherboard Chamber...")
mockup_black = build_phone_chamber_mockup(black_mb_raw, "FALLING // MATTE BLACK MOTHERBOARD", "ASUS ROG / WORKSTATION ARCHITECTURE", is_green=False)
out_black = f"{OUT_DIR}/realistic_motherboard_black_preview.png"
mockup_black.save(out_black, "PNG")
mockup_black.save(f"{BRAIN_DIR}/realistic_motherboard_black_preview.png", "PNG")

print("Rendering Realistic Emerald Server Motherboard Chamber...")
mockup_green = build_phone_chamber_mockup(emerald_mb_raw, "FALLING // EMERALD SERVER MOTHERBOARD", "ENTERPRISE DUAL-LGA HARDWARE", is_green=True)
out_green = f"{OUT_DIR}/realistic_motherboard_emerald_preview.png"
mockup_green.save(out_green, "PNG")
mockup_green.save(f"{BRAIN_DIR}/realistic_motherboard_emerald_preview.png", "PNG")

# Compose side-by-side presentation sheet
print("Composing Realistic Motherboards Showcase Sheet...")
sw = 1440
sh = 960
sheet = Image.new("RGBA", (sw, sh), (8, 11, 16, 255))
d_s = ImageDraw.Draw(sheet)

f_h1 = ImageFont.truetype(BOLD_FONT, 26)
f_lead = ImageFont.truetype(REG_FONT, 13)
d_s.text((40, 26), "FALLING — REALISTIC MOTHERBOARD GAME BOARDS & SILVER CHIP BLOCKS", fill=(245, 248, 255, 255), font=f_h1)
d_s.text((40, 62), "Comparing 2 photorealistic motherboard chambers populated with the new Silver Metallic Processor Chip Blocks (#7 Magenta)", fill=(130, 145, 165, 255), font=f_lead)

# Fit both phone stages side by side
fit_h = 820
r = float(fit_h) / H
fit_w = int(W * r)

mb1_fit = mockup_black.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
mb2_fit = mockup_green.resize((fit_w, fit_h), Image.Resampling.LANCZOS)

sheet.paste(mb1_fit, (120, 105), mb1_fit)
sheet.paste(mb2_fit, (120 + fit_w + 80, 105), mb2_fit)

# Labels below each phone stage
f_lbl = ImageFont.truetype(BOLD_FONT, 13)
lbl1 = "OPTION A: MATTE BLACK MOTHERBOARD"
lbl2 = "OPTION B: EMERALD SERVER MOTHERBOARD"

bb1 = d_s.textbbox((0, 0), lbl1, font=f_lbl)
w1 = bb1[2] - bb1[0]
bb2 = d_s.textbbox((0, 0), lbl2, font=f_lbl)
w2 = bb2[2] - bb2[0]

d_s.text((120 + (fit_w - w1)//2, 930), lbl1, fill=(0, 240, 255, 255), font=f_lbl)
d_s.text((120 + fit_w + 80 + (fit_w - w2)//2, 930), lbl2, fill=(0, 255, 136, 255), font=f_lbl)

# Add right-side callout for the Silver Processor Block
chip_preview = chip_silver.resize((180, 180), Image.Resampling.LANCZOS)
cx_box = 120 + 2 * fit_w + 140
if cx_box + 220 < sw:
    d_s.rounded_rectangle([cx_box, 160, cx_box + 220, 480], radius=14, fill=(16, 21, 29, 255), outline=(35, 45, 60, 255), width=1)
    d_s.text((cx_box + 16, 175), "SILVER CHIP BLOCK", fill=(240, 245, 255, 255), font=ImageFont.truetype(BOLD_FONT, 12))
    d_s.text((cx_box + 16, 195), "Brushed Nickel IHS", fill=(212, 175, 55, 255), font=ImageFont.truetype(MONO_FONT, 10))
    sheet.paste(chip_preview, (cx_box + 20, 220), chip_preview)
    d_s.text((cx_box + 16, 420), "• Silver metallic backdrop\n• Inset magenta square die\n• Laser numeral '7'", fill=(140, 155, 175, 255), font=ImageFont.truetype(REG_FONT, 11))

showcase_out = f"{OUT_DIR}/realistic_motherboards_showcase.png"
sheet.save(showcase_out, "PNG")
sheet.save(f"{BRAIN_DIR}/realistic_motherboards_showcase.png", "PNG")

print(f"✓ Saved Realistic Motherboards Showcase to {showcase_out}")

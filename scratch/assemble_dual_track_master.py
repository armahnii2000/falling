#!/usr/bin/env python3
"""
assemble_dual_track_master.py
Generates the comprehensive dual-track master storyboard:
Left column: MacBook Pro (Tiers 1-11)
Right column: iPhone Screen (Tiers 1-11)
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = '/Users/georgearmah/into-the-darkness'
SB_DIR = f'{BASE_DIR}/assets/ui/storyboard'
BRAIN_DIR = '/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272'

BOLD_FONT = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
REG_FONT = '/System/Library/Fonts/Helvetica.ttc'

f_hero = ImageFont.truetype(BOLD_FONT, 32)
f_title = ImageFont.truetype(BOLD_FONT, 22)
f_sub = ImageFont.truetype(REG_FONT, 14)

# Load the sheets
m1 = Image.open(f'{SB_DIR}/macbook_track_tiers_1_to_4_1791471747464.jpg').convert('RGBA')
m2 = Image.open(f'{SB_DIR}/macbook_track_tiers_5_to_8_1791471766388.jpg').convert('RGBA')
m3 = Image.open(f'{SB_DIR}/macbook_track_tiers_9_to_11_1791471784204.jpg').convert('RGBA')

p1 = Image.open(f'{SB_DIR}/phone_refined_tiers_1_to_4.png').convert('RGBA')
p2 = Image.open(f'{SB_DIR}/phone_refined_tiers_5_to_8.png').convert('RGBA')
p3 = Image.open(f'{SB_DIR}/phone_refined_tiers_9_to_11.png').convert('RGBA')

TARGET_W = 1200

def resize_w(img, w):
    h = int(img.height * (w / img.width))
    return img.resize((w, h), Image.Resampling.LANCZOS)

m1_r = resize_w(m1, TARGET_W)
p1_r = resize_w(p1, TARGET_W)
h1 = max(m1_r.height, p1_r.height)

m2_r = resize_w(m2, TARGET_W)
p2_r = resize_w(p2, TARGET_W)
h2 = max(m2_r.height, p2_r.height)

m3_r = resize_w(m3, TARGET_W)
p3_r = resize_w(p3, TARGET_W)
h3 = max(m3_r.height, p3_r.height)

ROW_GAP = 70
HEADER_H = 160
COL_GAP = 50
TOTAL_W = 60 + TARGET_W + COL_GAP + TARGET_W + 60
TOTAL_H = HEADER_H + h1 + ROW_GAP + h2 + ROW_GAP + h3 + 80

master = Image.new('RGBA', (TOTAL_W, TOTAL_H), (10, 13, 18, 255))
d = ImageDraw.Draw(master)

# Header
d.text((60, 36), 'FALLING (INTO THE DARKNESS) — MASTER DUAL-TRACK STORYBOARD (TIERS 1–11)', fill=(255, 255, 255, 255), font=f_hero)
d.text((60, 84), 'The 11-Stage Screenlife Parallel: MacBook Pro (Corporate & Code Paper Trail) vs. iPhone (Personal, Domestic & Financial Ruin)', fill=(140, 160, 185, 255), font=f_sub)

col1_x = 60
col2_x = 60 + TARGET_W + COL_GAP
y_curr = HEADER_H

# Row 1
d.text((col1_x, y_curr - 34), '💻 MACBOOK PRO: TIERS 1–4 (THE EUPHORIC ASCENT)', fill=(96, 165, 250, 255), font=f_title)
d.text((col2_x, y_curr - 34), '📱 IPHONE: TIERS 1–4 (THE DOMESTIC DREAM)', fill=(52, 211, 153, 255), font=f_title)
master.paste(m1_r, (col1_x, y_curr), m1_r)
master.paste(p1_r, (col2_x, y_curr), p1_r)
y_curr += h1 + ROW_GAP

# Row 2
d.text((col1_x, y_curr - 34), '💻 MACBOOK PRO: TIERS 5–8 (THE CRUNCH & SHAM EXIT)', fill=(251, 191, 36, 255), font=f_title)
d.text((col2_x, y_curr - 34), '📱 IPHONE: TIERS 5–8 (THE NEGLECT & FALSE HOPE)', fill=(251, 146, 60, 255), font=f_title)
master.paste(m2_r, (col1_x, y_curr), m2_r)
master.paste(p2_r, (col2_x, y_curr), p2_r)
y_curr += h2 + ROW_GAP

# Row 3
d.text((col1_x, y_curr - 34), '💻 MACBOOK PRO: TIERS 9–11 (THE WIPEOUT & LOCKOUT)', fill=(248, 113, 113, 255), font=f_title)
d.text((col2_x, y_curr - 34), '📱 IPHONE: TIERS 9–11 (BANK RUIN & DEAD BATTERY VOID)', fill=(244, 63, 94, 255), font=f_title)
master.paste(m3_r, (col1_x, y_curr), m3_r)
master.paste(p3_r, (col2_x, y_curr), p3_r)

out_dual = f'{SB_DIR}/falling_dual_track_master_storyboard.png'
brain_dual = f'{BRAIN_DIR}/falling_dual_track_master_storyboard.png'
master.save(out_dual, 'PNG')
master.save(brain_dual, 'PNG')
print(f'✓ Successfully generated and saved Master Dual-Track Storyboard: {out_dual}')

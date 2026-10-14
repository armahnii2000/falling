#!/usr/bin/env python3
"""
render_storyboard_panels.py
Generates a 6-panel cinematic visual storyboard for Falling (Into the Darkness).

Beats:
1. Panel 1: 3:32 AM / The Frozen Night (Phone on desk, 14% battery, isolated bedroom)
2. Panel 2: Motherboard Boot / First Drop (SMT gantry laser aligns, silver chip drops)
3. Panel 3: The Bleed / First Alert (Slack credentials revoked glows through translucent PCB)
4. Panel 4: The SWAP (Full phone screen focus: Sarah's text & Chase $314 balance)
5. Panel 5: Buffer Overflow Tension (Stack reaches red danger limit line, alarm flashing)
6. Panel 6: Titan Fusion / Total Darkness (Tier 11 Obsidian Titan emerges, 100% darkness purity)

Outputs:
- assets/ui/storyboard/falling_storyboard_6_panels.png
- Mirrored to brain directory.
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = "/Users/georgearmah/into-the-darkness"
OUT_DIR = f"{BASE_DIR}/assets/ui/storyboard"
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

# Panel size: 360 x 540 (aspect 2:3)
PW, PH = 360, 540

def make_panel_base(title, subtitle):
    p = Image.new("RGBA", (PW, PH), (10, 13, 18, 255))
    d = ImageDraw.Draw(p)
    # Beveled card border
    d.rounded_rectangle([2, 2, PW-2, PH-2], radius=12, outline=(40, 50, 68, 255), width=1)
    # Header banner
    d.rounded_rectangle([6, 6, PW-6, 44], radius=6, fill=(18, 24, 34, 255))
    d.text((16, 12), title, fill=(0, 240, 255, 255), font=get_font(BOLD_FONT, 11))
    d.text((16, 28), subtitle, fill=(140, 155, 175, 255), font=get_font(MONO_FONT, 9))
    return p, d

# ------------------------------------------------------------------------------
# PANEL 1: 3:32 AM / THE FROZEN NIGHT
# ------------------------------------------------------------------------------
p1, d1 = make_panel_base("BEAT 1: 03:32 AM", "THE FROZEN NIGHT // LEO VANCE")
# Desk surface in darkness
d1.rectangle([20, 160, PW-20, PH-20], fill=(14, 18, 24, 255), outline=(30, 38, 50, 255))
# Phone chassis on desk
d1.rounded_rectangle([PW//2 - 90, 80, PW//2 + 90, PH - 40], radius=24, fill=(5, 7, 10, 255), outline=(60, 75, 95, 255), width=2)
# Screen glow
glow1 = Image.new("RGBA", (PW, PH), (0,0,0,0))
ImageDraw.Draw(glow1).ellipse([(PW//2 - 120, 120), (PW//2 + 120, 360)], fill=(30, 50, 80, 80))
glow1 = glow1.filter(ImageFilter.GaussianBlur(30))
p1 = Image.alpha_composite(p1, glow1)
d1 = ImageDraw.Draw(p1)
# Clock
d1.text((PW//2 - 50, 140), "3:32", fill=(240, 245, 255, 255), font=get_font(BOLD_FONT, 36))
d1.text((PW//2 - 58, 190), "Monday, October 28", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 11))
d1.text((PW//2 - 70, 95), "ApexCell 5G", fill=(110, 125, 140, 200), font=get_font(REG_FONT, 9))
d1.text((PW//2 + 40, 95), "14% 🪫", fill=(255, 80, 80, 255), font=get_font(REG_FONT, 9))
# Narrative caption box
d1.rounded_rectangle([20, PH - 90, PW - 20, PH - 14], radius=8, fill=(16, 20, 28, 240), outline=(45, 58, 75, 255))
d1.text((30, PH - 82), "Leo sits in a silent dark room.", fill=(225, 235, 245, 255), font=get_font(BOLD_FONT, 10))
d1.text((30, PH - 66), "Battery at 14%. The phone lights up.\nHe opens Falling to escape the night.", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 9))

# ------------------------------------------------------------------------------
# PANEL 2: MOTHERBOARD BOOT / FIRST DROP
# ------------------------------------------------------------------------------
p2, d2 = make_panel_base("BEAT 2: THE MOTHERBOARD BOOTS", "SMT GANTRY & FIRST CHIP DROP")
# Motherboard chamber silhouette
d2.rounded_rectangle([30, 60, PW-30, PH-105], radius=14, fill=(12, 17, 24, 255), outline=(55, 75, 95, 255), width=2)
# Copper traces
for y in range(80, PH-120, 24):
    d2.line([(38, y), (70, y)], fill=(212, 175, 55, 160), width=1)
    d2.line([(PW-70, y), (PW-38, y)], fill=(212, 175, 55, 160), width=1)
# Dropper gantry rail
d2.rounded_rectangle([44, 76, PW-44, 88], radius=4, fill=(35, 45, 58, 255), outline=(85, 105, 130, 255))
# SMT nozzle & laser
d2.rectangle([PW//2 - 16, 82, PW//2 + 16, 102], fill=(22, 28, 38, 255), outline=(0, 240, 255, 240))
d2.line([(PW//2, 102), (PW//2, 200)], fill=(0, 240, 255, 200), width=2)
# Dropping Silver Processor Chip #1 (Yellow Mote 32px)
chip_y = 190
d2.rounded_rectangle([PW//2 - 24, chip_y, PW//2 + 24, chip_y + 48], radius=6, fill=(210, 215, 225, 255), outline=(255, 255, 255, 255), width=2)
# Inner yellow square
d2.rectangle([PW//2 - 14, chip_y + 10, PW//2 + 14, chip_y + 38], fill=(250, 204, 21, 255))
d2.text((PW//2 - 5, chip_y + 16), "1", fill=(0, 0, 0, 255), font=get_font(BOLD_FONT, 14))
# Socket bed at bottom
d2.rounded_rectangle([44, PH - 130, PW - 44, PH - 114], radius=4, fill=(25, 30, 40, 255), outline=(212, 175, 55, 200))
# Caption
d2.rounded_rectangle([20, PH - 90, PW - 20, PH - 14], radius=8, fill=(16, 20, 28, 240), outline=(45, 58, 75, 255))
d2.text((30, PH - 82), "Precision SMT head targets the socket.", fill=(225, 235, 245, 255), font=get_font(BOLD_FONT, 10))
d2.text((30, PH - 66), "Physical chips fall with weighted gravity.\nSame tiers fuse on contact.", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 9))

# ------------------------------------------------------------------------------
# PANEL 3: THE BLEED / FIRST NOTIFICATION
# ------------------------------------------------------------------------------
p3, d3 = make_panel_base("BEAT 3: THE BLEED", "SLACK ALERT GLOWS THROUGH PCB")
# Translucent Motherboard with notification glowing behind
d3.rounded_rectangle([30, 60, PW-30, PH-105], radius=14, fill=(14, 18, 26, 210), outline=(55, 75, 95, 255), width=2)
# Glowing Slack Notification beneath the motherboard
d3.rounded_rectangle([42, 130, PW-42, 195], radius=10, fill=(35, 42, 55, 230), outline=(224, 30, 90, 200), width=1)
d3.rectangle([52, 140, 64, 152], fill=(224, 30, 90, 255))
d3.text((70, 140), "SLACK • IT Security", fill=(255, 120, 160, 255), font=get_font(BOLD_FONT, 9))
d3.text((PW-90, 140), "3:28 AM", fill=(140, 155, 175, 200), font=get_font(REG_FONT, 8))
d3.text((52, 158), "Credentials revoked for user l_vance.", fill=(255, 255, 255, 255), font=get_font(REG_FONT, 9))
d3.text((52, 174), "VPN Session Terminated: Code 403.", fill=(160, 175, 195, 220), font=get_font(MONO_FONT, 8))
# Settled chips at bottom
# Chip 2 (Magenta)
d3.rounded_rectangle([PW//2 - 36, PH - 170, PW//2 + 36, PH - 120], radius=6, fill=(210, 215, 225, 255))
d3.rectangle([PW//2 - 24, PH - 162, PW//2 + 24, PH - 128], fill=(236, 72, 153, 255))
d3.text((PW//2 - 6, PH - 154), "2", fill=(255, 255, 255, 255), font=get_font(BOLD_FONT, 14))
# Caption
d3.rounded_rectangle([20, PH - 90, PW - 20, PH - 14], radius=8, fill=(16, 20, 28, 240), outline=(45, 58, 75, 255))
d3.text((30, PH - 82), "The real world invades the puzzle.", fill=(225, 235, 245, 255), font=get_font(BOLD_FONT, 10))
d3.text((30, PH - 66), "Credentials revoked. Career is ending.\nLeo keeps dropping chips to tune out.", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 9))

# ------------------------------------------------------------------------------
# PANEL 4: THE SWAP FOCUS
# ------------------------------------------------------------------------------
p4, d4 = make_panel_base("BEAT 4: THE SWAP", "PHONE FOCUS // UNFILTERED REALITY")
# Full phone lockscreen in focus
d4.rounded_rectangle([30, 60, PW-30, PH-105], radius=18, fill=(15, 20, 30, 255), outline=(0, 240, 255, 200), width=2)
# Status
d4.text((45, 75), "3:32 AM", fill=(240, 245, 255, 255), font=get_font(BOLD_FONT, 16))
d4.text((PW-90, 75), "14% 🪫", fill=(255, 80, 80, 255), font=get_font(REG_FONT, 11))
# Notification 1: Sarah
d4.rounded_rectangle([42, 105, PW-42, 175], radius=10, fill=(28, 35, 48, 255), outline=(52, 199, 89, 200), width=1)
d4.text((54, 115), "MESSAGES • Sarah (Wife)", fill=(52, 199, 89, 255), font=get_font(BOLD_FONT, 10))
d4.text((54, 134), "Leo, please come to bed...", fill=(240, 245, 255, 255), font=get_font(REG_FONT, 10))
d4.text((54, 150), "You haven't slept in two days.", fill=(160, 175, 195, 240), font=get_font(REG_FONT, 9))
# Notification 2: Chase Bank
d4.rounded_rectangle([42, 185, PW-42, 255], radius=10, fill=(28, 35, 48, 255), outline=(59, 130, 246, 200), width=1)
d4.text((54, 195), "CHASE • Account Alert", fill=(59, 130, 246, 255), font=get_font(BOLD_FONT, 10))
d4.text((54, 214), "COBRA deduction: -$1,842.00", fill=(255, 100, 100, 255), font=get_font(REG_FONT, 10))
d4.text((54, 230), "Remaining balance: $314.12", fill=(160, 175, 195, 240), font=get_font(REG_FONT, 9))
# Notification 3: Calendar
d4.rounded_rectangle([42, 265, PW-42, 335], radius=10, fill=(28, 35, 48, 255), outline=(245, 158, 11, 200), width=1)
d4.text((54, 275), "CALENDAR • 9:00 AM Today", fill=(245, 158, 11, 255), font=get_font(BOLD_FONT, 10))
d4.text((54, 294), "Mandatory HR Exit Interview", fill=(240, 245, 255, 255), font=get_font(REG_FONT, 10))
d4.text((54, 310), "Virtual Room 4 · Host: C. Miller", fill=(160, 175, 195, 240), font=get_font(REG_FONT, 9))
# Caption
d4.rounded_rectangle([20, PH - 90, PW - 20, PH - 14], radius=8, fill=(16, 20, 28, 240), outline=(45, 58, 75, 255))
d4.text((30, PH - 82), "SWAP Button cross-fades focus.", fill=(225, 235, 245, 255), font=get_font(BOLD_FONT, 10))
d4.text((30, PH - 66), "Leo confronts his collapsing life.\nNeglect warning: Board still simulates!", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 9))

# ------------------------------------------------------------------------------
# PANEL 5: BUFFER OVERFLOW TENSION
# ------------------------------------------------------------------------------
p5, d5 = make_panel_base("BEAT 5: BUFFER OVERFLOW", "STACK BREACHES DANGER LIMIT")
# Motherboard chamber
d5.rounded_rectangle([30, 60, PW-30, PH-105], radius=14, fill=(14, 18, 24, 255), outline=(255, 60, 75, 255), width=2)
# Glowing Red Danger Line
danger_y = 130
d5.line([(34, danger_y), (PW-34, danger_y)], fill=(255, 50, 70, 255), width=3)
d5.text((50, danger_y - 14), "⚠ VBUS_OVERVOLTAGE // BUFFER OVERFLOW!", fill=(255, 80, 90, 255), font=get_font(MONO_FONT, 8))
# High Stack of processor chips near line
# Tier 7 (Magenta)
d5.rounded_rectangle([PW//2 - 50, 140, PW//2 + 50, 230], radius=8, fill=(210, 215, 225, 255), outline=(255, 255, 255, 255))
d5.rectangle([PW//2 - 34, 154, PW//2 + 34, 216], fill=(236, 40, 130, 255))
d5.text((PW//2 - 8, 172), "7", fill=(255, 255, 255, 255), font=get_font(BOLD_FONT, 20))
# Tier 6 (Ruby) below
d5.rounded_rectangle([PW//2 - 60, 235, PW//2 + 60, 315], radius=8, fill=(210, 215, 225, 255))
d5.rectangle([PW//2 - 42, 247, PW//2 + 42, 303], fill=(190, 18, 60, 255))
d5.text((PW//2 - 8, 262), "6", fill=(255, 255, 255, 255), font=get_font(BOLD_FONT, 20))
# Warning strobe glow
glow5 = Image.new("RGBA", (PW, PH), (0,0,0,0))
ImageDraw.Draw(glow5).rectangle([30, 60, PW-30, PH-105], outline=(255, 50, 70, 180), width=4)
glow5 = glow5.filter(ImageFilter.GaussianBlur(12))
p5 = Image.alpha_composite(p5, glow5)
d5 = ImageDraw.Draw(p5)
# Caption
d5.rounded_rectangle([20, PH - 90, PW - 20, PH - 14], radius=8, fill=(16, 20, 28, 240), outline=(45, 58, 75, 255))
d5.text((30, PH - 82), "Panic rises as density spikes.", fill=(255, 100, 100, 255), font=get_font(BOLD_FONT, 10))
d5.text((30, PH - 66), "Stack stays above danger line > 3 sec $\\to$\nOvervoltage shutdown. Room lights flood.", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 9))

# ------------------------------------------------------------------------------
# PANEL 6: TITAN FUSION / TOTAL DARKNESS
# ------------------------------------------------------------------------------
p6, d6 = make_panel_base("BEAT 6: 100% DARKNESS", "THE TITAN MONOLITH APEX MERGE")
# The chamber goes pitch black obsidian
d6.rounded_rectangle([30, 60, PW-30, PH-105], radius=14, fill=(4, 5, 8, 255), outline=(0, 240, 255, 200), width=2)
# Massive Tier 11 Obsidian Titan Monolith (154px scale)
tx0, ty0, tx1, ty1 = PW//2 - 80, 160, PW//2 + 80, 320
# Light absorption aura
glow6 = Image.new("RGBA", (PW, PH), (0,0,0,0))
ImageDraw.Draw(glow6).ellipse([(tx0-30, ty0-30), (tx1+30, ty1+30)], fill=(0, 240, 255, 70))
glow6 = glow6.filter(ImageFilter.GaussianBlur(24))
p6 = Image.alpha_composite(p6, glow6)
d6 = ImageDraw.Draw(p6)
# Titan body (pure obsidian black with diamond chamfers)
d6.rounded_rectangle([tx0, ty0, tx1, ty1], radius=16, fill=(0, 0, 0, 255), outline=(180, 200, 220, 240), width=2)
d6.text((PW//2 - 24, 215), "11", fill=(255, 255, 255, 255), font=get_font(BOLD_FONT, 38))
# 100% Purity Meter readout
d6.rounded_rectangle([50, 90, PW-50, 124], radius=6, fill=(12, 16, 22, 255), outline=(0, 255, 136, 255))
d6.text((64, 98), "DARKNESS PURITY: 100.0%", fill=(0, 255, 136, 255), font=get_font(BOLD_FONT, 11))
# Caption
d6.rounded_rectangle([20, PH - 90, PW - 20, PH - 14], radius=8, fill=(16, 20, 28, 240), outline=(45, 58, 75, 255))
d6.text((30, PH - 82), "Total light absorption achieved.", fill=(0, 255, 136, 255), font=get_font(BOLD_FONT, 10))
d6.text((30, PH - 66), "The Titan Monolith drinks the room.\nAll notifications fade. Complete silence.", fill=(140, 155, 175, 255), font=get_font(REG_FONT, 9))

# ------------------------------------------------------------------------------
# COMPOSE 6-PANEL STORYBOARD SHEET (3x2 GRID)
# ------------------------------------------------------------------------------
sheet_w = 360 * 3 + 40 * 4 # 1240 px
sheet_h = 540 * 2 + 100 + 40 # 1220 px
sheet = Image.new("RGBA", (sheet_w, sheet_h), (7, 9, 13, 255))
d_s = ImageDraw.Draw(sheet)

# Header
d_s.text((40, 24), "FALLING (INTO THE DARKNESS) — NARRATIVE & GAMEPLAY STORYBOARD", fill=(245, 248, 255, 255), font=ImageFont.truetype(BOLD_FONT, 22))
d_s.text((40, 56), "6-Beat Sequence: 3:32 AM Frozen Night $\\to$ Motherboard Boot $\\to$ The Bleed $\\to$ SWAP $\\to$ Buffer Overflow $\\to$ 100% Titan Darkness", fill=(135, 150, 170, 255), font=ImageFont.truetype(REG_FONT, 12))

panels = [p1, p2, p3, p4, p5, p6]
for idx, panel in enumerate(panels):
    col = idx % 3
    row = idx // 3
    px = 40 + col * (PW + 20)
    py = 95 + row * (PH + 25)
    sheet.paste(panel, (px, py), panel)

out_sb = f"{OUT_DIR}/falling_storyboard_6_panels.png"
sheet.save(out_sb, "PNG")
sheet.save(f"{BRAIN_DIR}/falling_storyboard_6_panels.png", "PNG")
print(f"✓ Saved 6-Panel Storyboard Sheet to {out_sb}")

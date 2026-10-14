#!/usr/bin/env python3
"""
assemble_11_scene_storyboard.py
Assembles all 11 narrative phone scenes into a single high-resolution panoramic showcase.
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/Users/georgearmah/into-the-darkness"
SB_DIR = f"{BASE_DIR}/assets/ui/storyboard"
BRAIN_DIR = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"

s1_path = f"{SB_DIR}/phone_refined_tiers_1_to_4.png"
s2_path = f"{SB_DIR}/phone_refined_tiers_5_to_8.png"
s3_path = f"{SB_DIR}/phone_refined_tiers_9_to_11.png"

img1 = Image.open(s1_path).convert("RGBA")
img2 = Image.open(s2_path).convert("RGBA")
img3 = Image.open(s3_path).convert("RGBA")

# Stack all 3 sheets vertically with clean titles
W = max(img1.width, img2.width, img3.width) + 80
H = img1.height + img2.height + img3.height + 220

panoramic = Image.new("RGBA", (W, H), (10, 13, 18, 255))
d = ImageDraw.Draw(panoramic)

BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
REG_FONT = "/System/Library/Fonts/Helvetica.ttc"
f_title = ImageFont.truetype(BOLD_FONT, 28)
f_sub = ImageFont.truetype(REG_FONT, 14)

d.text((40, 24), "FALLING (INTO THE DARKNESS) — COMPLETE 11-SCENE NARRATIVE STORYBOARD", fill=(245, 248, 255, 255), font=f_title)
d.text((40, 64), "11-Tier Phone Screen Progression: Tracing Leo Vance from Euphoric Hackathon Spark to 3:32 AM Liquidation Wipeout and Blackout Void", fill=(130, 145, 165, 255), font=f_sub)

y = 110
for sheet_img in [img1, img2, img3]:
    panoramic.paste(sheet_img, (40, y), sheet_img)
    y += sheet_img.height + 25

out_path = f"{SB_DIR}/falling_11_scene_storyboard_panoramic.png"
brain_path = f"{BRAIN_DIR}/falling_11_scene_storyboard_panoramic.png"
panoramic.save(out_path, "PNG")
panoramic.save(brain_path, "PNG")
print(f"✓ Saved 11-scene panoramic storyboard to {out_path} and {brain_path}")

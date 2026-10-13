import os
from PIL import Image, ImageDraw, ImageFilter

W = 780
H = 1688
output_dir = '/Users/georgearmah/into-the-darkness/docs/themes_skinned_wireframes'

# 1. Load source arts for material extraction
im_sumi = Image.open('/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/theme1_sumi_translucent_clean.png').convert('RGBA')
im_crt = Image.open('/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/theme2_amber_crt_translucent_clean.png').convert('RGBA')
im_nordic = Image.open('/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/theme3_nordic_translucent_clean.png').convert('RGBA')
im_cyber = Image.open('/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/image4_stitched_pure.jpg').convert('RGBA')

# 2. Extract specific UI component slices
# Sumi:
wax_seal = im_sumi.crop((452, 764, 568, 876)).resize((180, 96), Image.Resampling.LANCZOS)
ink_dropper = im_sumi.crop((478, 224, 546, 510)).resize((44, 180), Image.Resampling.LANCZOS)
gold_monolith = im_sumi.crop((524, 478, 636, 668)).resize((308, 308), Image.Resampling.LANCZOS)
cin_block = im_sumi.crop((414, 522, 484, 598)).resize((56, 56), Image.Resampling.LANCZOS)
lapis_block = im_sumi.crop((452, 596, 522, 668)).resize((84, 84), Image.Resampling.LANCZOS)
ochre_block = im_sumi.crop((366, 590, 436, 668)).resize((28, 28), Image.Resampling.LANCZOS)

# Nordic:
dial_btn = im_nordic.crop((454, 778, 546, 870)).resize((160, 96), Image.Resampling.LANCZOS)
basalt_monolith = im_nordic.crop((572, 396, 658, 664)).resize((308, 308), Image.Resampling.LANCZOS)
terra_block = im_nordic.crop((340, 336, 428, 426)).resize((28, 28), Image.Resampling.LANCZOS)
conc_block = im_nordic.crop((456, 452, 544, 544)).resize((56, 56), Image.Resampling.LANCZOS)
steel_block = im_nordic.crop((456, 574, 544, 662)).resize((112, 112), Image.Resampling.LANCZOS)
cast_block = im_nordic.crop((340, 574, 428, 662)).resize((84, 84), Image.Resampling.LANCZOS)
aluminum_header = im_nordic.crop((226, 68, 774, 172)).resize((672, 80), Image.Resampling.LANCZOS)

# Amber CRT:
keycap_btn = im_crt.crop((436, 754, 564, 856)).resize((180, 96), Image.Resampling.LANCZOS)
crt_monolith = im_crt.crop((520, 318, 638, 538)).resize((308, 308), Image.Resampling.LANCZOS)

# Cyber:
swap_cyber = im_cyber.crop((318, 1204, 448, 1334)).resize((160, 96), Image.Resampling.LANCZOS)
titan_cyber = im_cyber.crop((476, 910, 706, 1162)).resize((308, 308), Image.Resampling.LANCZOS)
b1_cyber = im_cyber.crop((60, 1092, 124, 1162)).resize((28, 28), Image.Resampling.LANCZOS)
b2_cyber = im_cyber.crop((122, 1058, 218, 1162)).resize((56, 56), Image.Resampling.LANCZOS)
b3_cyber = im_cyber.crop((216, 1024, 330, 1162)).resize((84, 84), Image.Resampling.LANCZOS)
b4_cyber = im_cyber.crop((328, 990, 480, 1162)).resize((112, 112), Image.Resampling.LANCZOS)

print("Component texture slices successfully extracted!")

# Import render base from earlier script
from render_skinned_wireframes import (
    render_background_reality, font_bold_sm, font_bold_md, font_reg_sm, font_reg_md, font_titan,
    draw_rounded_rect
)

# 1. THEME 1 (Cyber Obsidian Pro with Real 3D Polymer Slices)
def build_rich_theme1():
    base = render_background_reality(blur_radius=14)
    draw = ImageDraw.Draw(base)

    # Borosilicate glass chamber plate
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 40, fill=(7, 11, 20, 215), outline=(0, 240, 255, 140), width=3)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # Grid & HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 32, fill=(20, 26, 40, 230), outline=(0, 240, 255, 100), width=2)
    draw.text((76, 108), "DARKNESS PURITY", fill=(255, 255, 255, 140), font=font_reg_sm)
    draw.text((76, 144), "84.2% · #050505", fill=(0, 240, 255, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(255, 255, 255, 140), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(255, 255, 255, 255), font=font_bold_md)
    draw.text((70, 260), "24 × 36 GRID · BOROSILICATE PRO GLASS", fill=(0, 240, 255, 180), font=font_reg_sm)

    # Gantry & Laser
    draw_rounded_rect(draw, (90, 300, 690, 308), 4, fill=(40, 50, 70, 255), outline=(0, 240, 255, 160), width=1)
    draw_rounded_rect(draw, (370, 288, 410, 320), 8, fill=(0, 240, 255, 255), outline=(255, 255, 255, 240), width=2)
    draw.line([(389, 320), (389, 1356)], fill=(0, 240, 255, 230), width=3)
    draw.line([(54, 460), (726, 460)], fill=(244, 63, 94, 240), width=3)
    draw.text((450, 428), "CRITICAL DENSITY LIMIT", fill=(244, 63, 94, 240), font=font_reg_sm)

    # Paste rich polymer blocks into exact wireframe slots!
    base.paste(b3_cyber, (348, 344)) # Dropping piece
    base.paste(b1_cyber, (78, 1328))  # Tier 1
    base.paste(b2_cyber, (114, 1300)) # Tier 2
    base.paste(b3_cyber, (178, 1272)) # Tier 3
    base.paste(b4_cyber, (270, 1244)) # Tier 4
    base.paste(titan_cyber, (390, 1048)) # Titan Monolith 11 (308x308)

    # Floor bed
    draw.line([(54, 1356), (726, 1356)], fill=(255, 255, 255, 180), width=4)

    # SWAP & NUDGE
    base.paste(swap_cyber, (230, 1412))
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(10, 21, 37, 255), outline=(0, 240, 255, 80), width=2)
    draw.text((478, 1444), "NUDGE", fill=(56, 189, 248, 240), font=font_reg_sm)
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# 2. THEME 2 (Sumi Ink & Washi with Real Gold Leaf & Mineral Stone Slices)
def build_rich_theme2():
    base = render_background_reality(blur_radius=18)
    draw = ImageDraw.Draw(base)

    # Washi parchment chamber
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 32, fill=(24, 18, 14, 235), outline=(217, 119, 6, 180), width=3)
    # Brass rivets
    for cx, cy in [(54, 240), (702, 240), (54, 1336), (702, 1336)]:
        draw_rounded_rect(ch_draw, (cx, cy, cx+24, cy+24), 6, fill=(180, 83, 9, 255), outline=(251, 191, 36, 255), width=2)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # Top HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 32, fill=(24, 18, 14, 230), outline=(217, 119, 6, 120), width=2)
    draw.text((76, 108), "墨度 SUMI PURITY", fill=(217, 119, 6, 220), font=font_reg_sm)
    draw.text((76, 144), "84.2% (漆黒 #030303)", fill=(245, 158, 11, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(217, 119, 6, 220), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(254, 243, 199, 255), font=font_bold_md)
    draw.text((70, 260), "24 × 36 GRID · WASHI & INKSTONE", fill=(217, 119, 6, 200), font=font_reg_sm)

    # Ebony rail & Dropper
    draw_rounded_rect(draw, (90, 298, 690, 310), 6, fill=(50, 30, 18, 255), outline=(180, 83, 9, 220), width=2)
    base.paste(ink_dropper, (368, 240), ink_dropper)
    draw.line([(389, 380), (389, 1356)], fill=(220, 38, 38, 180), width=2)

    # Calligraphic enso red arc
    draw.arc([60, 430, 720, 490], start=180, end=360, fill=(220, 38, 38, 240), width=6)
    draw.text((450, 428), "CRITICAL LIMIT · 界", fill=(220, 38, 38, 240), font=font_reg_sm)

    # Paste real mineral stone slices!
    base.paste(lapis_block, (348, 344)) # Dropping piece
    base.paste(ochre_block, (78, 1328))  # Tier 1 ochre
    base.paste(cin_block, (114, 1300))   # Tier 2 cinnabar
    base.paste(lapis_block, (178, 1272)) # Tier 3 lapis
    # Tier 4 slate
    draw_rounded_rect(draw, (270, 1244, 382, 1356), 12, fill=(65, 75, 89, 255), outline=(148, 163, 184, 255), width=2)

    # Paste real hammered gold leaf Titan Monolith!
    base.paste(gold_monolith, (390, 1048))

    # Chamber floor
    draw.line([(54, 1356), (726, 1356)], fill=(180, 83, 9, 220), width=4)

    # Paste real wax seal button!
    base.paste(wax_seal, (220, 1412), wax_seal)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(69, 26, 3, 255), outline=(217, 119, 6, 120), width=2)
    draw.text((472, 1444), "NUDGE 押", fill=(253, 230, 138, 230), font=font_reg_sm)
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# 3. THEME 3 (Amber CRT Terminal with Real Phosphor Scanlines & Keycap)
def build_rich_theme3():
    base = render_background_reality(blur_radius=12)
    draw = ImageDraw.Draw(base)

    # Smoked CRT cathode glass
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 48, fill=(12, 7, 2, 235), outline=(245, 158, 11, 200), width=4)
    for sy in range(240, 1360, 4):
        ch_draw.line([(56, sy), (724, sy)], fill=(245, 158, 11, 22), width=1)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 24, fill=(18, 10, 4, 240), outline=(245, 158, 11, 160), width=2)
    draw.text((76, 108), "SYS_PURITY [VT220]", fill=(245, 158, 11, 200), font=font_reg_sm)
    draw.text((76, 144), "84.2% [0x000000]", fill=(251, 191, 36, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(245, 158, 11, 200), font=font_reg_sm)
    draw.text((490, 144), "14,820 PTS", fill=(251, 191, 36, 255), font=font_bold_md)
    draw.text((70, 260), "24 × 36 GRID · P3 AMBER PHOSPHOR CRT", fill=(245, 158, 11, 200), font=font_reg_sm)

    # Gantry & Beam
    draw_rounded_rect(draw, (90, 300, 690, 308), 2, fill=(40, 20, 5, 255), outline=(245, 158, 11, 160), width=2)
    draw_rounded_rect(draw, (370, 288, 410, 320), 4, fill=(245, 158, 11, 255), outline=(251, 191, 36, 255), width=2)
    draw.line([(389, 320), (389, 1356)], fill=(245, 158, 11, 220), width=3)
    for dx in range(54, 726, 16):
        draw.line([(dx, 460), (dx+8, 460)], fill=(245, 158, 11, 255), width=3)
    draw.text((430, 428), "[DANGER_LIMIT: VT220]", fill=(245, 158, 11, 240), font=font_reg_sm)

    # Blocks: Phosphor vector cubes
    def draw_crt_wireframe(b, fill_c, line_c, num_text=""):
        draw_rounded_rect(draw, b, 4, fill=fill_c, outline=line_c, width=3)
        x0, y0, x1, y1 = b
        draw.line([(x0, y0), (x1, y1)], fill=(line_c[0], line_c[1], line_c[2], 80), width=1)
        if num_text:
            draw.text((x0+8, y0+8), num_text, fill=line_c, font=font_reg_sm)

    draw_crt_wireframe((348, 344, 432, 428), (40, 20, 5, 255), (245, 158, 11, 255), "3")
    draw_crt_wireframe((78, 1328, 106, 1356), (30, 15, 5, 255), (217, 119, 6, 255), "1")
    draw_crt_wireframe((114, 1300, 170, 1356), (40, 20, 5, 255), (245, 158, 11, 255), "2")
    draw_crt_wireframe((178, 1272, 262, 1356), (50, 25, 5, 255), (251, 191, 36, 255), "3")
    draw_crt_wireframe((270, 1244, 382, 1356), (60, 30, 5, 255), (251, 191, 36, 255), "4")

    # Paste real CRT phosphor Monolith 11!
    base.paste(crt_monolith, (390, 1048), crt_monolith)

    draw.line([(54, 1356), (726, 1356)], fill=(245, 158, 11, 220), width=4)

    # Paste real mechanical Cherry MX keycap!
    base.paste(keycap_btn, (220, 1412), keycap_btn)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 20, fill=(20, 11, 3, 255), outline=(245, 158, 11, 140), width=2)
    draw.text((472, 1444), "[NUDGE]", fill=(245, 158, 11, 240), font=font_reg_sm)
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(245, 158, 11, 120))
    return base

# 4. THEME 4 (Nordic Brutalism with Real Basalt & Concrete Slices)
def build_rich_theme4():
    base = render_background_reality(blur_radius=14)
    draw = ImageDraw.Draw(base)

    # Concrete pillars
    draw_rounded_rect(draw, (30, 230, 68, 1370), 8, fill=(107, 114, 128, 255), outline=(156, 163, 175, 255), width=2)
    draw_rounded_rect(draw, (712, 230, 750, 1370), 8, fill=(107, 114, 128, 255), outline=(156, 163, 175, 255), width=2)

    # Smoked sapphire plate
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 16, fill=(15, 20, 28, 235), outline=(156, 163, 175, 160), width=3)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # Paste real aluminum header!
    base.paste(aluminum_header, (54, 232), aluminum_header)

    # Gantry & laser
    draw_rounded_rect(draw, (90, 300, 690, 308), 2, fill=(156, 163, 175, 255))
    draw_rounded_rect(draw, (370, 288, 410, 320), 4, fill=(229, 231, 235, 255), outline=(255, 255, 255, 255), width=2)
    draw.line([(389, 320), (389, 1356)], fill=(239, 68, 68, 200), width=2)
    draw.line([(54, 460), (726, 460)], fill=(239, 68, 68, 240), width=3)
    draw.text((450, 428), "CRITICAL LIMIT · ISO", fill=(239, 68, 68, 240), font=font_reg_sm)
    draw.text((70, 290), "24 × 36 GRID · HONED BASALT & SAPPHIRE", fill=(156, 163, 175, 200), font=font_reg_sm)

    # Paste real architectural material slices!
    base.paste(cast_block, (348, 344)) # Dropping piece
    base.paste(terra_block, (78, 1328))  # Tier 1 terracotta
    base.paste(conc_block, (114, 1300))  # Tier 2 concrete
    base.paste(cast_block, (178, 1272))  # Tier 3 cast concrete
    base.paste(steel_block, (270, 1244)) # Tier 4 steel

    # Paste real honed volcanic basalt Titan Monolith!
    base.paste(basalt_monolith, (390, 1048), basalt_monolith)

    draw.line([(54, 1356), (726, 1356)], fill=(156, 163, 175, 220), width=4)

    # Top HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 24, fill=(24, 30, 42, 230), outline=(156, 163, 175, 120), width=2)
    draw.text((76, 108), "BASALT DENSITY · ISO", fill=(156, 163, 175, 200), font=font_reg_sm)
    draw.text((76, 144), "84.2% · #050505", fill=(229, 231, 235, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(156, 163, 175, 200), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(255, 255, 255, 255), font=font_bold_md)

    # Paste real knurled aluminum rotary dial!
    base.paste(dial_btn, (230, 1412), dial_btn)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(31, 41, 55, 255), outline=(156, 163, 175, 80), width=2)
    draw.text((478, 1444), "NUDGE", fill=(156, 163, 175, 240), font=font_reg_sm)
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# 5. THEME 5 (Optical Neon Gels & Bioluminescent Glow)
def build_rich_theme5():
    from render_skinned_wireframes import render_theme5
    return render_theme5()

print("Building rich component-skinned themes...")
r1 = build_rich_theme1()
r1.save(f'{output_dir}/rich_theme1_cyber_obsidian.png')
r1.resize((390, 844), Image.Resampling.LANCZOS).convert('RGB').save(f'{output_dir}/rich_theme1_cyber_obsidian_390.jpg', quality=92)
print("Saved Rich Theme 1")

r2 = build_rich_theme2()
r2.save(f'{output_dir}/rich_theme2_sumi_washi.png')
r2.resize((390, 844), Image.Resampling.LANCZOS).convert('RGB').save(f'{output_dir}/rich_theme2_sumi_washi_390.jpg', quality=92)
print("Saved Rich Theme 2")

r3 = build_rich_theme3()
r3.save(f'{output_dir}/rich_theme3_amber_crt.png')
r3.resize((390, 844), Image.Resampling.LANCZOS).convert('RGB').save(f'{output_dir}/rich_theme3_amber_crt_390.jpg', quality=92)
print("Saved Rich Theme 3")

r4 = build_rich_theme4()
r4.save(f'{output_dir}/rich_theme4_nordic_brutalism.png')
r4.resize((390, 844), Image.Resampling.LANCZOS).convert('RGB').save(f'{output_dir}/rich_theme4_nordic_brutalism_390.jpg', quality=92)
print("Saved Rich Theme 4")

r5 = build_rich_theme5()
r5.save(f'{output_dir}/rich_theme5_neon_ink_gels.png')
r5.resize((390, 844), Image.Resampling.LANCZOS).convert('RGB').save(f'{output_dir}/rich_theme5_neon_ink_gels_390.jpg', quality=92)
print("Saved Rich Theme 5")

# Generate rich panoramic showcase
pw = 390
ph = 844
gap = 40
margin_x = 60
margin_top = 100
margin_bottom = 120
tot_w = margin_x * 2 + 5 * pw + 4 * gap
tot_h = margin_top + ph + margin_bottom

pan = Image.new('RGB', (tot_w, tot_h), (11, 13, 17))
pdraw = ImageDraw.Draw(pan)
pdraw.text((margin_x, 30), 'FALLING — 5 HIGH-FIDELITY SKINNED WIREFRAMES (LOCKED 24 × 36 GRID PARITY)', fill=(240, 243, 246), font=font_bold_sm)
pdraw.text((margin_x, 68), 'Tactile Material Slices Mapped 1:1 into Wireframe Geometry • 45.8% Titan Monolith Locked • Translucent Reality Bleed', fill=(130, 140, 155), font=font_reg_sm)

theme_list = [
    ('THEME 1: CYBER OBSIDIAN', 'Beveled Tactile Polymer • Borosilicate Glass', r1.resize((pw, ph), Image.Resampling.LANCZOS).convert('RGB')),
    ('THEME 2: SUMI INK & WASHI', 'Carved Mineral Stones • 24k Gold Monolith • Wax Seal', r2.resize((pw, ph), Image.Resampling.LANCZOS).convert('RGB')),
    ('THEME 3: AMBER CRT TERMINAL', 'Phosphor Bloom • Vector Wireframe • Cherry MX Key', r3.resize((pw, ph), Image.Resampling.LANCZOS).convert('RGB')),
    ('THEME 4: NORDIC BRUTALISM', 'Honed Basalt & Concrete • Milled Aluminum • Dial', r4.resize((pw, ph), Image.Resampling.LANCZOS).convert('RGB')),
    ('THEME 5: OPTICAL NEON GELS', 'Bioluminescent Gels • Radiant Ambient Rim Glow', r5.resize((pw, ph), Image.Resampling.LANCZOS).convert('RGB')),
]

for idx, (ttitle, tsub, timg) in enumerate(theme_list):
    px = margin_x + idx * (pw + gap)
    py = margin_top
    pan.paste(timg, (px, py))
    pdraw.text((px, py + ph + 20), ttitle, fill=(230, 235, 245), font=font_bold_sm)
    pdraw.text((px, py + ph + 50), tsub, fill=(110, 125, 140), font=font_reg_sm)

pan.save(f'{output_dir}/rich_skinned_wireframes_showcase.webp', quality=95)
print("Rich panoramic showcase generated successfully!")

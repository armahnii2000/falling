import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Canvas dimensions (2x retina for 390x844)
W = 780
H = 1688

output_dir = '/Users/georgearmah/into-the-darkness/docs/themes_skinned_wireframes'
os.makedirs(output_dir, exist_ok=True)

# Try fonts
try:
    font_bold_lg = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 56)
    font_bold_md = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 36)
    font_bold_sm = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 26)
    font_reg_md = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 24)
    font_reg_sm = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 20)
    font_clock = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 120)
    font_titan = ImageFont.truetype('/System/Library/Fonts/SFNSMono.ttf', 84)
except:
    font_bold_lg = font_bold_md = font_bold_sm = font_reg_md = font_reg_sm = font_clock = font_titan = ImageFont.load_default()

def draw_rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def render_background_reality(blur_radius=12):
    # Renders Leo's iPhone lockscreen at 3:32 AM with notifications
    img = Image.new('RGBA', (W, H), (7, 10, 16, 255))
    draw = ImageDraw.Draw(img)

    # Dynamic Island
    draw_rounded_rect(draw, (270, 24, 510, 88), 32, fill=(0, 0, 0, 255))

    # Top Status bar
    draw.text((64, 36), "ApexCell", fill=(200, 205, 215, 200), font=font_reg_sm)
    draw.text((660, 36), "14% 🪫", fill=(239, 68, 68, 220), font=font_reg_sm)

    # Clock 3:32
    draw.text((250, 140), "3:32", fill=(255, 255, 255, 70), font=font_clock)
    draw.text((260, 290), "Monday, October 28", fill=(255, 255, 255, 45), font=font_reg_md)

    # 1. Slack notification
    slack_box = (48, 430, 732, 578)
    draw_rounded_rect(draw, slack_box, 28, fill=(20, 27, 40, 70), outline=(255, 255, 255, 30), width=2)
    # Icon squircle
    draw_rounded_rect(draw, (72, 458, 144, 530), 18, fill=(255, 255, 255, 220))
    draw.text((94, 466), "#", fill=(74, 21, 75, 255), font=font_bold_md)
    # Text
    draw.text((164, 454), "Slack · now", fill=(168, 85, 247, 230), font=font_bold_sm)
    draw.text((164, 494), "Apex Tech Security: Enterprise credentials", fill=(255, 255, 255, 180), font=font_reg_sm)
    draw.text((164, 526), "revoked for user l_vance.", fill=(255, 255, 255, 180), font=font_reg_sm)

    # 2. Messages notification (Wife)
    msg_box = (48, 600, 732, 748)
    draw_rounded_rect(draw, msg_box, 28, fill=(20, 27, 40, 70), outline=(255, 255, 255, 30), width=2)
    # Avatar
    draw_rounded_rect(draw, (72, 628, 144, 700), 36, fill=(30, 41, 59, 240))
    draw.text((92, 640), "👩", fill=(255, 255, 255, 255), font=font_reg_md)
    draw_rounded_rect(draw, (116, 672, 144, 700), 14, fill=(34, 197, 94, 255)) # green badge
    # Text
    draw.text((164, 624), "Sarah Vance (Wife) · 2m ago", fill=(34, 197, 94, 230), font=font_bold_sm)
    draw.text((164, 664), "Leo, please come to bed...", fill=(255, 255, 255, 180), font=font_reg_sm)
    draw.text((164, 696), "You haven't slept in two days.", fill=(255, 255, 255, 180), font=font_reg_sm)

    # Apply authentic glass blur to reality layer
    blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return blurred

print("Base reality layer generator defined.")

def add_noise(img, factor=0.04):
    arr = np.array(img).astype(np.float32)
    noise = (np.random.rand(*arr.shape[:2]) - 0.5) * 255.0 * factor
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def draw_beveled_box(draw, bbox, fill_color, highlight_color, shadow_color, border_color=None, border_w=2, radius=8):
    x0, y0, x1, y1 = bbox
    # Base fill
    draw_rounded_rect(draw, bbox, radius, fill=fill_color)
    # Inner specular highlight (top and left edge)
    draw.line([(x0 + radius, y0 + 1), (x1 - radius, y0 + 1)], fill=highlight_color, width=2)
    draw.line([(x0 + 1, y0 + radius), (x0 + 1, y1 - radius)], fill=highlight_color, width=2)
    # Inner shadow (bottom and right edge)
    draw.line([(x0 + radius, y1 - 2), (x1 - radius, y1 - 2)], fill=shadow_color, width=2)
    draw.line([(x1 - 2, y0 + radius), (x1 - 2, y1 - radius)], fill=shadow_color, width=2)
    if border_color:
        draw_rounded_rect(draw, bbox, radius, outline=border_color, width=border_w)

# ==========================================
# THEME 1: CYBER OBSIDIAN PRO
# ==========================================
def render_theme1():
    base = render_background_reality(blur_radius=14)
    draw = ImageDraw.Draw(base)

    # 1. Chamber Glass (Borosilicate Glass Plate)
    ch_box = (54, 240, 726, 1360)
    # Glass tint overlay
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 40, fill=(7, 11, 20, 215), outline=(0, 240, 255, 120), width=3)
    # Specular rim top
    ch_draw.line([(94, 242), (686, 242)], fill=(255, 255, 255, 180), width=2)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # Chamber grid lines (very faint cyan)
    for gy in range(320, 1360, 48):
        draw.line([(56, gy), (724, gy)], fill=(0, 240, 255, 12), width=1)
    for gx in range(54 + 28, 726, 28):
        draw.line([(gx, 242), (gx, 1358)], fill=(0, 240, 255, 8), width=1)

    # Gantry & Rail
    draw_rounded_rect(draw, (90, 300, 690, 308), 4, fill=(40, 50, 70, 255), outline=(0, 240, 255, 160), width=1)
    # Titanium spigot
    draw_rounded_rect(draw, (370, 288, 410, 320), 8, fill=(0, 240, 255, 255), outline=(255, 255, 255, 240), width=2)
    # Cyan laser hairline with glow
    draw.line([(389, 320), (389, 1356)], fill=(0, 240, 255, 230), width=3)

    # Danger limit
    draw.line([(54, 460), (726, 460)], fill=(244, 63, 94, 240), width=3)
    draw.text((450, 428), "CRITICAL DENSITY LIMIT", fill=(244, 63, 94, 240), font=font_reg_sm)
    draw.text((70, 260), "24 × 36 GRID · BOROSILICATE PRO GLASS", fill=(0, 240, 255, 180), font=font_reg_sm)

    # Dropping block (Tier 3: 84x84)
    draw_beveled_box(draw, (348, 344, 432, 428), (2, 132, 199, 255), (125, 211, 252, 230), (3, 105, 161, 255), border_color=(255, 255, 255, 200), radius=12)

    # Settled blocks
    # Block 1 (Tier 1: 28x28)
    draw_beveled_box(draw, (78, 1328, 106, 1356), (250, 204, 21, 255), (254, 240, 138, 230), (202, 138, 4, 255), radius=6)
    # Block 2 (Tier 2: 56x56)
    draw_beveled_box(draw, (114, 1300, 170, 1356), (244, 63, 94, 255), (254, 205, 211, 230), (190, 18, 60, 255), radius=8)
    # Block 3 (Tier 3: 84x84)
    draw_beveled_box(draw, (178, 1272, 262, 1356), (2, 132, 199, 255), (125, 211, 252, 230), (3, 105, 161, 255), radius=12)
    # Block 4 (Tier 4: 112x112)
    draw_beveled_box(draw, (270, 1244, 382, 1356), (79, 70, 229, 255), (199, 210, 254, 230), (55, 48, 163, 255), radius=14)

    # TITAN MONOLITH 11 (308x308) - Glossy obsidian with metallic chamfer
    titan_box = (390, 1048, 698, 1356)
    draw_beveled_box(draw, titan_box, (4, 7, 12, 255), (0, 240, 255, 240), (0, 100, 130, 255), border_color=(0, 240, 255, 255), border_w=5, radius=24)
    # Specular corner chamfers
    draw.text((505, 1140), "11", fill=(0, 240, 255, 255), font=font_titan)

    # Floor bed
    draw.line([(54, 1356), (726, 1356)], fill=(255, 255, 255, 180), width=4)

    # Top HUD Plate
    draw_rounded_rect(draw, (48, 88, 732, 208), 32, fill=(20, 26, 40, 230), outline=(0, 240, 255, 100), width=2)
    draw.text((76, 108), "DARKNESS PURITY", fill=(255, 255, 255, 140), font=font_reg_sm)
    draw.text((76, 144), "84.2% · #050505", fill=(0, 240, 255, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(255, 255, 255, 140), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(255, 255, 255, 255), font=font_bold_md)

    # Bottom Controls
    # SWAP
    draw_rounded_rect(draw, (190, 1412, 430, 1508), 48, fill=(15, 32, 53, 255), outline=(0, 240, 255, 255), width=3)
    draw.text((254, 1442), "SWAP ⟳", fill=(0, 240, 255, 255), font=font_bold_sm)
    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(10, 21, 37, 255), outline=(0, 240, 255, 80), width=2)
    draw.text((478, 1444), "NUDGE", fill=(56, 189, 248, 240), font=font_reg_sm)

    # Home indicator
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# ==========================================
# THEME 2: SUMI INK & WASHI (ZEN CALLIGRAPHIC VOID)
# ==========================================
def render_theme2():
    base = render_background_reality(blur_radius=18)
    draw = ImageDraw.Draw(base)

    # 1. Chamber Glass (Mulberry Washi Parchment Lantern)
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    # Warm washi parchment fill with fibrous texture
    draw_rounded_rect(ch_draw, ch_box, 32, fill=(24, 18, 14, 235), outline=(217, 119, 6, 180), width=3)
    # Aged brass corner brackets
    for cx, cy in [(54, 240), (702, 240), (54, 1336), (702, 1336)]:
        draw_rounded_rect(ch_draw, (cx, cy, cx+24, cy+24), 6, fill=(180, 83, 9, 255), outline=(251, 191, 36, 255), width=2)
        ch_draw.ellipse([cx+8, cy+8, cx+16, cy+16], fill=(50, 30, 10, 255))
    base = Image.alpha_composite(base, ch_overlay)
    base = add_noise(base, factor=0.03) # Washi paper fiber noise
    draw = ImageDraw.Draw(base)

    # Ebony dropper rail
    draw_rounded_rect(draw, (90, 298, 690, 310), 6, fill=(50, 30, 18, 255), outline=(180, 83, 9, 220), width=2)
    # Glass ink dropper spigot
    draw_rounded_rect(draw, (374, 280, 406, 324), 8, fill=(30, 20, 15, 255), outline=(217, 119, 6, 255), width=2)
    draw.ellipse([384, 324, 396, 338], fill=(15, 10, 8, 255)) # Hanging sumi ink drop
    # Vermilion ink thread
    draw.line([(389, 340), (389, 1356)], fill=(220, 38, 38, 180), width=2)

    # Calligraphic Red Enso Danger Limit Arc
    draw.arc([60, 430, 720, 490], start=180, end=360, fill=(220, 38, 38, 240), width=6)
    draw.text((450, 428), "CRITICAL LIMIT · 界", fill=(220, 38, 38, 240), font=font_reg_sm)
    draw.text((70, 260), "24 × 36 GRID · WASHI & INKSTONE", fill=(217, 119, 6, 200), font=font_reg_sm)

    # Dropping block (Lapis lazuli: 84x84)
    draw_beveled_box(draw, (348, 344, 432, 428), (29, 78, 216, 255), (147, 197, 253, 230), (30, 58, 138, 255), border_color=(245, 158, 11, 200), radius=10)

    # Settled carved mineral pigment stones
    # Block 1 (Yellow Ochre sandstone: 28x28)
    draw_beveled_box(draw, (78, 1328, 106, 1356), (217, 119, 6, 255), (253, 230, 138, 230), (146, 64, 14, 255), radius=6)
    # Block 2 (Cinnabar Vermilion mineral: 56x56)
    draw_beveled_box(draw, (114, 1300, 170, 1356), (220, 38, 38, 255), (254, 205, 211, 230), (153, 27, 27, 255), radius=8)
    # Block 3 (Lapis Lazuli: 84x84)
    draw_beveled_box(draw, (178, 1272, 262, 1356), (29, 78, 216, 255), (147, 197, 253, 230), (30, 58, 138, 255), radius=10)
    # Block 4 (Honed River Slate: 112x112)
    draw_beveled_box(draw, (270, 1244, 382, 1356), (75, 85, 99, 255), (209, 213, 219, 230), (31, 41, 55, 255), radius=12)

    # TITAN MONOLITH 11 (308x308) - Carved charcoal inkstone with hammered 24k Gold Leaf border
    titan_box = (390, 1048, 698, 1356)
    draw_beveled_box(draw, titan_box, (15, 15, 15, 255), (245, 158, 11, 255), (180, 83, 9, 255), border_color=(245, 158, 11, 255), border_w=6, radius=18)
    # Irregular gold leaf trim accent
    for off in range(390, 698, 16):
        draw.line([(off, 1048), (off+8, 1056)], fill=(254, 240, 138, 240), width=2)
    draw.text((505, 1140), "11", fill=(245, 158, 11, 255), font=font_titan)

    # Chamber floor
    draw.line([(54, 1356), (726, 1356)], fill=(180, 83, 9, 220), width=4)

    # Top HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 32, fill=(24, 18, 14, 230), outline=(217, 119, 6, 120), width=2)
    draw.text((76, 108), "墨度 SUMI PURITY", fill=(217, 119, 6, 220), font=font_reg_sm)
    draw.text((76, 144), "84.2% (漆黒 #030303)", fill=(245, 158, 11, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(217, 119, 6, 220), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(254, 243, 199, 255), font=font_bold_md)

    # Cinnabar Wax Seal SWAP Button
    seal_box = (190, 1412, 430, 1508)
    draw_rounded_rect(draw, seal_box, 48, fill=(153, 27, 27, 255), outline=(220, 38, 38, 255), width=3)
    draw.text((246, 1442), "SWAP 換", fill=(254, 240, 138, 255), font=font_bold_sm)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(69, 26, 3, 255), outline=(217, 119, 6, 120), width=2)
    draw.text((472, 1444), "NUDGE 押", fill=(253, 230, 138, 230), font=font_reg_sm)

    # Home indicator
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# ==========================================
# THEME 3: AMBER CRT TERMINAL (1980s VINTAGE)
# ==========================================
def render_theme3():
    base = render_background_reality(blur_radius=12)
    draw = ImageDraw.Draw(base)

    # 1. Chamber (Curved Smoked Cathode CRT Glass)
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 48, fill=(12, 7, 2, 235), outline=(245, 158, 11, 200), width=4)
    # Raster scanlines across the chamber
    for sy in range(240, 1360, 4):
        ch_draw.line([(56, sy), (724, sy)], fill=(245, 158, 11, 18), width=1)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # Bracketed track
    draw_rounded_rect(draw, (90, 300, 690, 308), 2, fill=(40, 20, 5, 255), outline=(245, 158, 11, 160), width=2)
    draw_rounded_rect(draw, (370, 288, 410, 320), 4, fill=(245, 158, 11, 255), outline=(251, 191, 36, 255), width=2)
    # Pulsing amber scanline beam
    draw.line([(389, 320), (389, 1356)], fill=(245, 158, 11, 220), width=3)

    # Dashed danger line
    for dx in range(54, 726, 16):
        draw.line([(dx, 460), (dx+8, 460)], fill=(245, 158, 11, 255), width=3)
    draw.text((430, 428), "[DANGER_LIMIT: VT220]", fill=(245, 158, 11, 240), font=font_reg_sm)
    draw.text((70, 260), "24 × 36 GRID · P3 AMBER PHOSPHOR CRT", fill=(245, 158, 11, 200), font=font_reg_sm)

    # Vector wireframe blocks
    def draw_crt_wireframe(b, fill_c, line_c, num_text=""):
        draw_rounded_rect(draw, b, 4, fill=fill_c, outline=line_c, width=3)
        # Inner vector grid
        x0, y0, x1, y1 = b
        draw.line([(x0, y0), (x1, y1)], fill=(line_c[0], line_c[1], line_c[2], 60), width=1)
        if num_text:
            draw.text((x0+8, y0+8), num_text, fill=line_c, font=font_reg_sm)

    draw_crt_wireframe((348, 344, 432, 428), (40, 20, 5, 255), (245, 158, 11, 255), "3")
    draw_crt_wireframe((78, 1328, 106, 1356), (30, 15, 5, 255), (217, 119, 6, 255), "1")
    draw_crt_wireframe((114, 1300, 170, 1356), (40, 20, 5, 255), (245, 158, 11, 255), "2")
    draw_crt_wireframe((178, 1272, 262, 1356), (50, 25, 5, 255), (251, 191, 36, 255), "3")
    draw_crt_wireframe((270, 1244, 382, 1356), (60, 30, 5, 255), (251, 191, 36, 255), "4")

    # TITAN MONOLITH 11 (308x308) - Glowing phosphor wireframe chassis
    titan_box = (390, 1048, 698, 1356)
    draw_rounded_rect(draw, titan_box, 16, fill=(20, 10, 3, 255), outline=(245, 158, 11, 255), width=6)
    # Inner phosphor grid lines
    for ty in range(1048+32, 1356, 32):
        draw.line([(392, ty), (696, ty)], fill=(245, 158, 11, 80), width=1)
    for tx in range(390+32, 698, 32):
        draw.line([(tx, 1050), (tx, 1354)], fill=(245, 158, 11, 80), width=1)
    draw.text((505, 1140), "11", fill=(251, 191, 36, 255), font=font_titan)

    # Floor line
    draw.line([(54, 1356), (726, 1356)], fill=(245, 158, 11, 220), width=4)

    # HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 24, fill=(18, 10, 4, 240), outline=(245, 158, 11, 160), width=2)
    draw.text((76, 108), "SYS_PURITY [VT220]", fill=(245, 158, 11, 200), font=font_reg_sm)
    draw.text((76, 144), "84.2% [0x000000]", fill=(251, 191, 36, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(245, 158, 11, 200), font=font_reg_sm)
    draw.text((490, 144), "14,820 PTS", fill=(251, 191, 36, 255), font=font_bold_md)

    # Mechanical Cherry MX Keycap SWAP Button
    draw_rounded_rect(draw, (190, 1412, 430, 1508), 20, fill=(30, 18, 5, 255), outline=(245, 158, 11, 255), width=3)
    # Keycap bevel slope
    draw_rounded_rect(draw, (202, 1422, 418, 1498), 12, fill=(45, 25, 8, 255))
    draw.text((236, 1444), "[SWAP_KEY]", fill=(251, 191, 36, 255), font=font_bold_sm)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 20, fill=(20, 11, 3, 255), outline=(245, 158, 11, 140), width=2)
    draw.text((472, 1444), "[NUDGE]", fill=(245, 158, 11, 240), font=font_reg_sm)

    # Home indicator
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(245, 158, 11, 120))
    return base

# ==========================================
# THEME 4: NORDIC BRUTALISM & HONED BASALT
# ==========================================
def render_theme4():
    base = render_background_reality(blur_radius=14)
    draw = ImageDraw.Draw(base)

    # 1. Chamber: Concrete pillars flanking smoked sapphire plate
    # Side Concrete Pillars
    draw_rounded_rect(draw, (30, 230, 68, 1370), 8, fill=(107, 114, 128, 255), outline=(156, 163, 175, 255), width=2)
    draw_rounded_rect(draw, (712, 230, 750, 1370), 8, fill=(107, 114, 128, 255), outline=(156, 163, 175, 255), width=2)

    # Floating smoked sapphire plate
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 16, fill=(15, 20, 28, 235), outline=(156, 163, 175, 160), width=3)
    base = Image.alpha_composite(base, ch_overlay)
    base = add_noise(base, factor=0.02)
    draw = ImageDraw.Draw(base)

    # Top Milled Bead-Blasted Aluminum Header
    draw_rounded_rect(draw, (54, 232, 726, 280), 8, fill=(156, 163, 175, 255), outline=(229, 231, 235, 255), width=2)
    # Recessed red LED hazard indicator strip
    draw_rounded_rect(draw, (90, 272, 690, 278), 2, fill=(239, 68, 68, 255))
    # Rolling score odometer in aluminum header
    draw_rounded_rect(draw, (530, 242, 706, 270), 6, fill=(20, 20, 20, 255))
    draw.text((560, 244), "14,820", fill=(255, 255, 255, 255), font=font_bold_sm)

    # Dropper gantry & laser
    draw_rounded_rect(draw, (90, 300, 690, 308), 2, fill=(156, 163, 175, 255))
    draw_rounded_rect(draw, (370, 288, 410, 320), 4, fill=(229, 231, 235, 255), outline=(255, 255, 255, 255), width=2)
    draw.line([(389, 320), (389, 1356)], fill=(239, 68, 68, 200), width=2)

    # Danger line
    draw.line([(54, 460), (726, 460)], fill=(239, 68, 68, 240), width=3)
    draw.text((450, 428), "CRITICAL LIMIT · ISO", fill=(239, 68, 68, 240), font=font_reg_sm)
    draw.text((70, 290), "24 × 36 GRID · HONED BASALT & SAPPHIRE", fill=(156, 163, 175, 200), font=font_reg_sm)

    # Dropping block (Cast concrete: 84x84)
    draw_beveled_box(draw, (348, 344, 432, 428), (107, 114, 128, 255), (209, 213, 219, 230), (55, 65, 81, 255), border_color=(229, 231, 235, 200), radius=6)

    # Settled architectural materials
    # Block 1 (Terracotta brick: 28x28)
    draw_beveled_box(draw, (78, 1328, 106, 1356), (194, 65, 12, 255), (254, 215, 170, 230), (124, 45, 18, 255), radius=4)
    # Block 2 (Pitted gray concrete: 56x56)
    draw_beveled_box(draw, (114, 1300, 170, 1356), (107, 114, 128, 255), (209, 213, 219, 230), (55, 65, 81, 255), radius=6)
    # Block 3 (Cast concrete slab: 84x84)
    draw_beveled_box(draw, (178, 1272, 262, 1356), (156, 163, 175, 255), (243, 244, 246, 230), (107, 114, 128, 255), radius=8)
    # Block 4 (Brushed stainless steel: 112x112)
    draw_beveled_box(draw, (270, 1244, 382, 1356), (209, 213, 219, 255), (255, 255, 255, 255), (156, 163, 175, 255), radius=10)

    # TITAN MONOLITH 11 (308x308) - Honed volcanic basalt with diamond-beveled specular rims
    titan_box = (390, 1048, 698, 1356)
    draw_beveled_box(draw, titan_box, (10, 12, 16, 255), (229, 231, 235, 255), (75, 85, 99, 255), border_color=(229, 231, 235, 255), border_w=5, radius=12)
    draw.text((505, 1140), "11", fill=(255, 255, 255, 255), font=font_titan)

    # Floor bed
    draw.line([(54, 1356), (726, 1356)], fill=(156, 163, 175, 220), width=4)

    # Top HUD Plate
    draw_rounded_rect(draw, (48, 88, 732, 208), 24, fill=(24, 30, 42, 230), outline=(156, 163, 175, 120), width=2)
    draw.text((76, 108), "BASALT DENSITY · ISO", fill=(156, 163, 175, 200), font=font_reg_sm)
    draw.text((76, 144), "84.2% · #050505", fill=(229, 231, 235, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(156, 163, 175, 200), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(255, 255, 255, 255), font=font_bold_md)

    # Knurled Aluminum Rotary Dial SWAP Button
    draw_rounded_rect(draw, (190, 1412, 430, 1508), 48, fill=(55, 65, 81, 255), outline=(156, 163, 175, 255), width=3)
    # Knurled grip pattern
    for kx in range(210, 410, 8):
        draw.line([(kx, 1418), (kx, 1502)], fill=(75, 85, 99, 120), width=1)
    draw.text((254, 1442), "SWAP ⦿", fill=(243, 244, 246, 255), font=font_bold_sm)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(31, 41, 55, 255), outline=(156, 163, 175, 80), width=2)
    draw.text((478, 1444), "NUDGE", fill=(156, 163, 175, 240), font=font_reg_sm)

    # Home indicator
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# ==========================================
# THEME 5: OPTICAL NEON GELS & INK CONTRAST
# ==========================================
def render_theme5():
    base = render_background_reality(blur_radius=16)
    draw = ImageDraw.Draw(base)

    # 1. Chamber: Dark translucent optical dye gel chamber
    ch_box = (54, 240, 726, 1360)
    ch_overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(ch_overlay)
    draw_rounded_rect(ch_draw, ch_box, 40, fill=(10, 4, 20, 230), outline=(255, 0, 127, 180), width=3)
    base = Image.alpha_composite(base, ch_overlay)
    draw = ImageDraw.Draw(base)

    # Rail & Spigot
    draw_rounded_rect(draw, (90, 300, 690, 308), 4, fill=(40, 10, 50, 255), outline=(255, 0, 127, 180), width=1)
    draw_rounded_rect(draw, (370, 288, 410, 320), 8, fill=(0, 240, 255, 255), outline=(255, 0, 127, 255), width=2)
    draw.line([(389, 320), (389, 1356)], fill=(0, 240, 255, 255), width=3)

    # Danger limit
    draw.line([(54, 460), (726, 460)], fill=(255, 0, 127, 240), width=3)
    draw.text((450, 428), "CRITICAL LIMIT · GEL", fill=(255, 0, 127, 240), font=font_reg_sm)
    draw.text((70, 260), "24 × 36 GRID · BIOLUMINESCENT DYE GELS", fill=(255, 0, 127, 200), font=font_reg_sm)

    # Luminous dye gel blocks with radiant inner glow
    def draw_neon_gel_box(b, fill_c, glow_c):
        # Outer glow
        draw_rounded_rect(draw, b, 12, fill=fill_c, outline=glow_c, width=3)
        # Inner highlight
        x0, y0, x1, y1 = b
        draw_rounded_rect(draw, (x0+4, y0+4, x1-4, y1-4), 8, fill=fill_c, outline=(255, 255, 255, 140), width=1)

    draw_neon_gel_box((348, 344, 432, 428), (0, 240, 255, 255), (125, 211, 252, 255))
    draw_neon_gel_box((78, 1328, 106, 1356), (255, 215, 0, 255), (254, 240, 138, 255))
    draw_neon_gel_box((114, 1300, 170, 1356), (255, 0, 127, 255), (254, 205, 211, 255))
    draw_neon_gel_box((178, 1272, 262, 1356), (0, 240, 255, 255), (125, 211, 252, 255))
    draw_neon_gel_box((270, 1244, 382, 1356), (0, 230, 118, 255), (187, 247, 208, 255))

    # TITAN MONOLITH 11 (308x308) - Deep obsidian ink block with radiant neon cyan rim
    titan_box = (390, 1048, 698, 1356)
    draw_beveled_box(draw, titan_box, (5, 5, 8, 255), (0, 240, 255, 255), (150, 0, 80, 255), border_color=(0, 240, 255, 255), border_w=6, radius=24)
    draw.text((505, 1140), "11", fill=(0, 240, 255, 255), font=font_titan)

    # Floor bed
    draw.line([(54, 1356), (726, 1356)], fill=(255, 0, 127, 220), width=4)

    # Top HUD
    draw_rounded_rect(draw, (48, 88, 732, 208), 32, fill=(26, 10, 38, 230), outline=(255, 0, 127, 120), width=2)
    draw.text((76, 108), "GEL PURITY · HADAL", fill=(255, 0, 127, 220), font=font_reg_sm)
    draw.text((76, 144), "84.2% PURITY", fill=(0, 240, 255, 255), font=font_bold_md)
    draw.text((490, 108), "DENSITY SCORE", fill=(255, 0, 127, 220), font=font_reg_sm)
    draw.text((490, 144), "14,820", fill=(255, 255, 255, 255), font=font_bold_md)

    # Dual-tone Neon Pill SWAP Button
    draw_rounded_rect(draw, (190, 1412, 430, 1508), 48, fill=(26, 10, 38, 255), outline=(255, 0, 127, 255), width=3)
    draw.text((220, 1442), "FLIP TO PHONE", fill=(255, 0, 127, 255), font=font_bold_sm)

    # NUDGE
    draw_rounded_rect(draw, (450, 1412, 590, 1508), 48, fill=(16, 5, 26, 255), outline=(255, 0, 127, 80), width=2)
    draw.text((478, 1444), "NUDGE", fill=(255, 128, 223, 240), font=font_reg_sm)

    # Home indicator
    draw_rounded_rect(draw, (250, 1648, 530, 1658), 5, fill=(255, 255, 255, 80))
    return base

# Render all 5 themes
print("Rendering all 5 skinned wireframe themes...")
t1 = render_theme1()
t1.save(f'{output_dir}/skinned_theme1_cyber_obsidian.png')
t1_390 = t1.resize((390, 844), Image.Resampling.LANCZOS)
t1_390.convert("RGB").save(f'{output_dir}/skinned_theme1_cyber_obsidian_390.jpg', quality=90)
print("Rendered Theme 1 (Cyber Obsidian Pro)")

t2 = render_theme2()
t2.save(f'{output_dir}/skinned_theme2_sumi_washi.png')
t2_390 = t2.resize((390, 844), Image.Resampling.LANCZOS)
t2_390.convert("RGB").save(f'{output_dir}/skinned_theme2_sumi_washi_390.jpg', quality=90)
print("Rendered Theme 2 (Sumi Ink & Washi)")

t3 = render_theme3()
t3.save(f'{output_dir}/skinned_theme3_amber_crt.png')
t3_390 = t3.resize((390, 844), Image.Resampling.LANCZOS)
t3_390.convert("RGB").save(f'{output_dir}/skinned_theme3_amber_crt_390.jpg', quality=90)
print("Rendered Theme 3 (Amber CRT Terminal)")

t4 = render_theme4()
t4.save(f'{output_dir}/skinned_theme4_nordic_brutalism.png')
t4_390 = t4.resize((390, 844), Image.Resampling.LANCZOS)
t4_390.convert("RGB").save(f'{output_dir}/skinned_theme4_nordic_brutalism_390.jpg', quality=90)
print("Rendered Theme 4 (Nordic Brutalism)")

t5 = render_theme5()
t5.save(f'{output_dir}/skinned_theme5_neon_ink_gels.png')
t5_390 = t5.resize((390, 844), Image.Resampling.LANCZOS)
t5_390.convert("RGB").save(f'{output_dir}/skinned_theme5_neon_ink_gels_390.jpg', quality=90)
print("Rendered Theme 5 (Optical Neon Gels)")

# Also create panoramic showcase of the skinned wireframes
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
pdraw.text((margin_x, 30), 'FALLING — 5 COMPONENT-SKINNED WIREFRAMES (1:1 GEOMETRY & ART LOCK)', fill=(240, 243, 246), font=font_bold_sm)
pdraw.text((margin_x, 68), 'Strict 24 × 36 Chamber Grid • 45.8% Titan Monolith Parity • Translucent Component Skinning', fill=(130, 140, 155), font=font_reg_sm)

theme_list = [
    ('THEME 1: CYBER OBSIDIAN', 'Beveled Polymer • Borosilicate Glass', t1_390),
    ('THEME 2: SUMI INK & WASHI', 'Mineral Pigment Stones • 24k Gold Monolith', t2_390),
    ('THEME 3: AMBER CRT TERMINAL', 'Phosphor Bloom • Vector Wireframe Blocks', t3_390),
    ('THEME 4: NORDIC BRUTALISM', 'Basalt & Concrete • Bead-Blasted Aluminum', t4_390),
    ('THEME 5: OPTICAL NEON GELS', 'Luminous Dye Gels • Ambient Rim Glow', t5_390),
]

for idx, (ttitle, tsub, timg) in enumerate(theme_list):
    px = margin_x + idx * (pw + gap)
    py = margin_top
    pan.paste(timg.convert("RGB"), (px, py))
    pdraw.text((px, py + ph + 20), ttitle, fill=(230, 235, 245), font=font_bold_sm)
    pdraw.text((px, py + ph + 50), tsub, fill=(110, 125, 140), font=font_reg_sm)

pan.save(f'{output_dir}/skinned_wireframes_5_showcase.webp', quality=95)
print("Panoramic showcase generated successfully!")

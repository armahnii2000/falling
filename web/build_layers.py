import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

def main():
    base_dir = "/Users/georgearmah/into-the-darkness/web/layers"
    scratch_dir = "/Users/georgearmah/into-the-darkness/scratch"
    artifact_dir = "/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(scratch_dir, exist_ok=True)

    # 1. LAYER 1: Phone Screen
    phone_src = os.path.join(artifact_dir, "layer1_phone_screen_1791559707803.jpg")
    im_phone = Image.open(phone_src).convert("RGBA")
    w, h = im_phone.size
    
    layer1_path = os.path.join(base_dir, "layer1_phone_screen.png")
    im_phone.save(layer1_path, "PNG")
    print(f"Saved Layer 1: {layer1_path}")

    # 2. LAYER 2: Frosted / Translucent Glass
    # A. Floating Chamber Plate
    glass_ref_path = os.path.join(artifact_dir, "layer2_frosted_glass_frontal_1791559888008.jpg")
    im_glass_ref = Image.open(glass_ref_path).convert("RGBA")
    arr_glass = np.array(im_glass_ref, dtype=np.float32)
    
    # Extract chamber mask and specular highlights
    brightness = np.max(arr_glass[:, :, :3], axis=2)
    chamber_mask = (brightness > 16).astype(np.float32)
    chamber_mask_u8 = (chamber_mask * 255).astype(np.uint8)
    chamber_mask_img = Image.fromarray(chamber_mask_u8).filter(ImageFilter.GaussianBlur(radius=2))
    
    # Specular rim highlights (crystal beveled border)
    rim_rgb = np.clip((arr_glass[:, :, :3] - 30.0) * 1.6, 0, 255).astype(np.uint8)
    rim_alpha = np.clip(np.max(rim_rgb, axis=2).astype(np.float32) * 1.3, 0, 255).astype(np.uint8)
    # Inside the body of the glass plate, create a smooth frosted smoked translucent fill
    inner_body = (brightness > 20) & (np.max(rim_rgb, axis=2) < 180)
    
    glass_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    # Body: smoked translucent (alpha ~ 90 / 255 = 35% opacity)
    glass_rgba[chamber_mask > 0.5, 0] = 30
    glass_rgba[chamber_mask > 0.5, 1] = 40
    glass_rgba[chamber_mask > 0.5, 2] = 55
    glass_rgba[chamber_mask > 0.5, 3] = 90
    
    # Rim highlights: additive specular crystal edges
    specular_mask = rim_alpha > 30
    glass_rgba[specular_mask, :3] = np.maximum(glass_rgba[specular_mask, :3], rim_rgb[specular_mask])
    glass_rgba[specular_mask, 3] = np.maximum(glass_rgba[specular_mask, 3], rim_alpha[specular_mask])
    
    layer2_chamber = Image.fromarray(glass_rgba)
    layer2_chamber_path = os.path.join(base_dir, "layer2_frosted_glass_chamber.png")
    layer2_chamber.save(layer2_chamber_path, "PNG")
    print(f"Saved Layer 2 Chamber: {layer2_chamber_path}")

    # B. Fullscreen Frosted Glass Sheet
    # Subtle inner bevel border with translucent smoked frost
    full_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    # Screen inner region (inside titanium bezel)
    screen_mask = np.zeros((h, w), dtype=np.float32)
    # Fill phone screen area: x ~ 48..720, y ~ 60..1316 with rounded corners
    draw_screen = Image.new("L", (w, h), 0)
    draw_d = ImageDraw.Draw(draw_screen)
    draw_d.rounded_rectangle([46, 56, 722, 1320], radius=85, fill=255)
    screen_mask_arr = np.array(draw_screen, dtype=np.float32) / 255.0
    
    full_rgba[:, :, 0] = 20
    full_rgba[:, :, 1] = 28
    full_rgba[:, :, 2] = 42
    full_rgba[:, :, 3] = (screen_mask_arr * 105).astype(np.uint8)
    
    layer2_full = Image.fromarray(full_rgba)
    layer2_full_path = os.path.join(base_dir, "layer2_frosted_glass_fullbleed.png")
    layer2_full.save(layer2_full_path, "PNG")
    print(f"Saved Layer 2 Full: {layer2_full_path}")

    # 3. LAYER 3: The Game Board (Completely transparent background)
    game_ref_path = os.path.join(artifact_dir, "layer3_game_board_isolated_1791559846627.jpg")
    im_game_ref = Image.open(game_ref_path).convert("RGB")
    arr_game = np.array(im_game_ref, dtype=np.float32)
    
    bg_color = np.array([45.0, 52.0, 70.0], dtype=np.float32)
    dist = np.sqrt(np.sum((arr_game - bg_color)**2, axis=2))
    
    # Smooth alpha feathering
    game_alpha = np.clip((dist - 7.0) / 16.0, 0.0, 1.0)
    
    # Un-premultiply background color to remove slate tint on edges
    alpha_3d = game_alpha[:, :, np.newaxis]
    rgb_clean = np.where(alpha_3d > 0.01, (arr_game - bg_color * (1.0 - alpha_3d)) / np.maximum(alpha_3d, 0.01), arr_game)
    rgb_clean = np.clip(rgb_clean, 0, 255).astype(np.uint8)
    alpha_u8 = (game_alpha * 255).astype(np.uint8)
    
    layer3_game = Image.fromarray(np.dstack([rgb_clean, alpha_u8]))
    layer3_path = os.path.join(base_dir, "layer3_game_board.png")
    layer3_game.save(layer3_path, "PNG")
    print(f"Saved Layer 3 Game Board: {layer3_path}")

    # 4. STITCHED MOCKUPS
    # Optical frosted effect: The region underneath the glass receives a Gaussian blur + frost tint
    def make_frosted_phone(im_phone, mask_img, blur_radius=7, tint_color=(20, 30, 48, 80)):
        blurred = im_phone.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        tint_layer = Image.new("RGBA", (w, h), tint_color)
        frosted = Image.alpha_composite(blurred, tint_layer)
        
        # Paste frosted version only inside mask
        out = im_phone.copy()
        out.paste(frosted, (0, 0), mask_img)
        return out

    # Mockup A: Floating Chamber Stitched
    frosted_phone_chamber = make_frosted_phone(im_phone, chamber_mask_img, blur_radius=6, tint_color=(15, 25, 40, 75))
    # Add glass rim & crystal highlights
    mockup_chamber = Image.alpha_composite(frosted_phone_chamber, layer2_chamber)
    # Overlay transparent game board
    mockup_chamber = Image.alpha_composite(mockup_chamber, layer3_game)
    mockup_chamber_path = os.path.join(base_dir, "mockup_stitched_floating_chamber.png")
    mockup_chamber.save(mockup_chamber_path, "PNG")
    # Also save JPG version in artifacts directory for instant user viewing
    artifact_chamber_jpg = os.path.join(artifact_dir, "mockup_stitched_floating_chamber.jpg")
    mockup_chamber.convert("RGB").save(artifact_chamber_jpg, "JPEG", quality=95)
    print(f"Saved Mockup Chamber: {mockup_chamber_path}")

    # Mockup B: Full-screen Glass Stitched
    frosted_phone_full = make_frosted_phone(im_phone, draw_screen, blur_radius=6, tint_color=(15, 22, 38, 85))
    mockup_full = Image.alpha_composite(frosted_phone_full, layer2_full)
    mockup_full = Image.alpha_composite(mockup_full, layer3_game)
    mockup_full_path = os.path.join(base_dir, "mockup_stitched_fullscreen.png")
    mockup_full.save(mockup_full_path, "PNG")
    # Also save JPG version in artifacts directory
    artifact_full_jpg = os.path.join(artifact_dir, "mockup_stitched_fullscreen.jpg")
    mockup_full.convert("RGB").save(artifact_full_jpg, "JPEG", quality=95)
    print(f"Saved Mockup Full: {mockup_full_path}")

    # Also save a 4-in-1 Side-by-Side Sheet
    # Shows: [Layer 1 Phone Alone] [Layer 2 Glass Alone] [Layer 3 Game Board Alone] [Stitched Composite]
    sheet_w = w * 4
    sheet_h = h
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (12, 14, 20, 255))
    
    # Layer 1
    sheet.paste(im_phone, (0, 0))
    # Layer 2 (on a dark slate card so the crystal edges and frost are visible)
    card_bg = Image.new("RGBA", (w, h), (22, 28, 38, 255))
    l2_on_card = Image.alpha_composite(card_bg, layer2_chamber)
    sheet.paste(l2_on_card, (w, 0))
    # Layer 3 (on a dark slate card so the transparent game board is visible)
    l3_on_card = Image.alpha_composite(card_bg, layer3_game)
    sheet.paste(l3_on_card, (w * 2, 0))
    # Stitched Mockup
    sheet.paste(mockup_chamber, (w * 3, 0))
    
    sheet_path = os.path.join(base_dir, "layers_side_by_side_comparison.png")
    sheet.save(sheet_path, "PNG")
    artifact_sheet_jpg = os.path.join(artifact_dir, "layers_side_by_side_comparison.jpg")
    sheet.convert("RGB").save(artifact_sheet_jpg, "JPEG", quality=92)
    print(f"Saved Comparison Sheet: {sheet_path}")

if __name__ == "__main__":
    main()

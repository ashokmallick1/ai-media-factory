import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/NirmalaB.ttf" if bold else "C:/Windows/Fonts/Nirmala.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()

STUDIO_META = {
    "entertainment": {
        "studio_name": "MO GAON COMEDY STUDIO",
        "studio_odia": "ମୋ ଗାଁ କମେଡି ଷ୍ଟୁଡିଓ",
        "border_color": (252, 163, 17, 240), # Vibrant Amber
        "avatar_bg": (230, 57, 70),          # Crimson
        "avatar_text": "Bikram Baboo",
        "role_default": "Village Comedy & Sitcoms",
        "tag": "EPISODIC COMEDY SKETCH"
    },
    "kids": {
        "studio_name": "LITTLE FRIENDS CARTOON STUDIO",
        "studio_odia": "ଛୋଟ ପିଲାଙ୍କ ଆନନ୍ଦ ଶିକ୍ଷା",
        "border_color": (78, 205, 196, 240), # Turquoise
        "avatar_bg": (255, 107, 107),        # Coral
        "avatar_text": "Gulu Owl",
        "role_default": "Preschool Rhymes & Moral Tales",
        "tag": "PRESCHOOL LEARNING & RHYMES"
    },
    "education": {
        "studio_name": "AI EXPLAINER ACADEMY",
        "studio_odia": "ଏଆଇ ଜ୍ଞାନ ବିଜ୍ଞାନ ଶିକ୍ଷା",
        "border_color": (59, 130, 246, 240), # Tech Blue
        "avatar_bg": (14, 165, 233),         # Sky Blue
        "avatar_text": "AI Explainer",
        "role_default": "60-Second Deep Dives",
        "tag": "TECH TUTORIAL & AI REASONING"
    },
    "podcast": {
        "studio_name": "AI FRONTIER PODCAST STUDIO",
        "studio_odia": "ଆର୍ଟିଫିସିଆଲ ଇଣ୍ଟେଲିଜେନ୍ସ ପଡକାଷ୍ଟ",
        "border_color": (168, 85, 247, 240), # Purple
        "avatar_bg": (217, 70, 239),         # Fuchsia
        "avatar_text": "Alex & Priya",
        "role_default": "Bilingual AI Frontier Discussion",
        "tag": "MULTI-SPEAKER VIRTUAL PODCAST"
    },
    "news": {
        "studio_name": "ODISHA FACTUAL NEWSROOM",
        "studio_odia": "ଓଡ଼ିଶା ତଥ୍ୟ ଖବର ପ୍ରସାରଣ",
        "border_color": (239, 68, 68, 240),  # Red Broadcast
        "avatar_bg": (185, 28, 28),          # Deep Red
        "avatar_text": "News Desk",
        "role_default": "Fact-Checked Regional Citations",
        "tag": "FACTUAL BREAKING REPORT"
    },
    "marketing": {
        "studio_name": "BHASHAAI BRAND LAB",
        "studio_odia": "ଭାଷାଏଆଇ ମାର୍କେଟିଂ ଷ୍ଟୁଡିଓ",
        "border_color": (245, 158, 11, 240), # Gold
        "avatar_bg": (249, 115, 22),         # Neon Orange
        "avatar_text": "BhashaVoice",
        "role_default": "Instant Indic Speech Cloning",
        "tag": "KINETIC PROMO & BRAND AD"
    }
}

def generate_scene_card(
    output_path: str,
    character_name: str,
    studio_type: str = "entertainment",
    scene_heading: str = "",
    target_language: str = "or"
) -> str:
    """
    Renders an elegant glassmorphism character & studio spotlight card
    as an RGBA PNG with alpha transparency to be composited by FFmpeg.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    card_w, card_h = 760, 480
    img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    meta = STUDIO_META.get(studio_type.lower(), STUDIO_META["entertainment"])

    # Rounded rectangle card backdrop (deep slate glassmorphism)
    r = 28
    draw.rounded_rectangle(
        [(0, 0), (card_w - 1, card_h - 1)],
        radius=r,
        fill=(18, 22, 36, 215), # 85% opacity dark indigo/slate
        outline=meta["border_color"],
        width=3
    )

    # Top Studio Ribbon Header
    draw.rounded_rectangle(
        [(15, 15), (card_w - 16, 68)],
        radius=14,
        fill=(255, 255, 255, 18),
        outline=(255, 255, 255, 40),
        width=1
    )

    font_ribbon = get_font(20, bold=True)
    studio_title = meta["studio_name"]
    draw.text((card_w // 2, 42), studio_title, font=font_ribbon, fill=(255, 255, 255, 240), anchor="mm")

    # Character Avatar Circle
    avatar_r = 65
    cx, cy = card_w // 2, 175
    draw.ellipse(
        [(cx - avatar_r, cy - avatar_r), (cx + avatar_r, cy + avatar_r)],
        fill=meta["avatar_bg"],
        outline=(255, 255, 255, 200),
        width=3
    )

    # Initial or Symbol in Avatar
    font_initial = get_font(46, bold=True)
    char_display = character_name.strip() if character_name else meta["avatar_text"]
    initial = char_display[0].upper() if char_display else "A"
    draw.text((cx, cy + 2), initial, font=font_initial, fill=(255, 255, 255, 255), anchor="mm")

    # Character Name
    font_name = get_font(34, bold=True)
    draw.text((card_w // 2, 275), char_display, font=font_name, fill=(252, 211, 77, 255), anchor="mm")

    # Role / Studio Badge
    font_role = get_font(21, bold=False)
    role_text = meta["role_default"]
    draw.text((card_w // 2, 318), role_text, font=font_role, fill=(226, 232, 240, 220), anchor="mm")

    # Scene Topic / Dynamic Indicator Bar
    draw.rounded_rectangle(
        [(40, 360), (card_w - 41, 440)],
        radius=16,
        fill=(255, 255, 255, 12),
        outline=(255, 255, 255, 30),
        width=1
    )

    font_scene = get_font(22, bold=False)
    display_heading = scene_heading if scene_heading else meta["tag"]
    if len(display_heading) > 48:
        display_heading = display_heading[:45] + "..."
    draw.text((card_w // 2, 400), f"▶  {display_heading}", font=font_scene, fill=(241, 245, 249, 235), anchor="mm")

    img.save(output_path, "PNG")
    return output_path

if __name__ == "__main__":
    test_out = "./storage/test_card.png"
    generate_scene_card(test_out, "Bikram Baboo", "entertainment", "Village Square Arrival")
    print(f"Generated test card at {test_out}")

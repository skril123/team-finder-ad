import io
import random
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from core.constants import AVATAR_FONT_SIZE, AVATAR_SIZE

AVATAR_BACKGROUND_COLORS = ["#4F46E5", "#0F766E", "#BE123C", "#7C3AED", "#0369A1", "#15803D"]


def avatar_upload_path(instance, filename):
    return f"avatars/{uuid.uuid4()}.png"


def build_initial_avatar(name):
    background = random.choice(AVATAR_BACKGROUND_COLORS)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), background)
    draw = ImageDraw.Draw(image)
    initial = (name[:1] or "?").upper()
    font = get_avatar_font()

    try:
        bbox = draw.textbbox((0, 0), initial, font=font)
        x = (AVATAR_SIZE - (bbox[2] - bbox[0])) / 2
        y = (AVATAR_SIZE - (bbox[3] - bbox[1])) / 2 - 8
        draw.text((x, y), initial, fill="white", font=font)
    except UnicodeEncodeError:
        draw.text((104, 84), "?", fill="white", font=ImageFont.load_default())

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


def get_avatar_font():
    font_candidates = [
        settings.BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for font_path in font_candidates:
        try:
            return ImageFont.truetype(str(font_path), AVATAR_FONT_SIZE)
        except OSError:
            continue
    return ImageFont.load_default()

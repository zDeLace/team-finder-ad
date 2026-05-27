import io
import random

from PIL import Image, ImageDraw, ImageFont

from django.core.files.base import ContentFile

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 100

FONT_PATH_PRIMARY = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_SECONDARY = "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"

COLOR_BLUE = "#4A90D9"
COLOR_MEDIUM_VIOLET = "#7B68EE"
COLOR_GREEN = "#5BA85B"
COLOR_ORANGE = "#D9844A"
COLOR_CRIMSON = "#C06080"
COLOR_TEAL = "#4AABB8"
COLOR_BROWN = "#8B7355"
COLOR_DARK_BLUE = "#6A5ACD"

AVATAR_COLORS = [
    COLOR_BLUE,
    COLOR_MEDIUM_VIOLET,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_CRIMSON,
    COLOR_TEAL,
    COLOR_BROWN,
    COLOR_DARK_BLUE,
]


def generate_avatar(letter: str) -> ContentFile:
    letter = letter.upper()
    color = random.choice(AVATAR_COLORS)

    img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH_PRIMARY, size=AVATAR_FONT_SIZE)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype(FONT_PATH_SECONDARY, size=AVATAR_FONT_SIZE)
        except (IOError, OSError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (AVATAR_SIZE - text_width) // 2 - bbox[0]
    y = (AVATAR_SIZE - text_height) // 2 - bbox[1]

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f"avatar_{letter}.png")

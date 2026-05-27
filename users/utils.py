import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


AVATAR_COLORS = [
    "#4A90D9",
    "#7B68EE",
    "#5BA85B",
    "#D9844A",
    "#C06080",
    "#4AABB8",
    "#8B7355",
    "#6A5ACD",
]


def generate_avatar(letter: str) -> ContentFile:
    size = 200
    letter = letter.upper()

    color = random.choice(AVATAR_COLORS)

    img = Image.new("RGB", (size, size), color=color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=100
            )
    except (IOError, OSError):
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", size=100
                )
        except (IOError, OSError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f"avatar_{letter}.png")

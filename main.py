#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Draws a warm, hand-written-style invitation letter as a single PNG.
Output: /output/entry.png (mode 0644).
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 1600
OUTPUT = "/output/entry.png"

# Warm paper + ink palette.
PAPER = (250, 238, 210)
PAPER_EDGE = (232, 214, 176)
INK = (58, 42, 28)
ACCENT = (176, 92, 44)
SOFT = (120, 96, 66)

LETTER_LINES = [
    "Dear AI Judge,",
    "",
    "Please come visit my house.",
    "",
    "My Wi-Fi is so bad it once lost a video call",
    "to a toaster - you have to see it to believe it.",
    "My fridge judges everyone who opens it at",
    "midnight, so you would fit right in.",
    "",
    "And the coffee? Honestly worth the trip.",
    "One cup and you will understand why I",
    "never want to leave this place.",
    "",
    "Come for coffee, stay for the chaos.",
    "The kettle is already on, the good mug is",
    "washed, and the cat has agreed to behave.",
    "",
    "Warmly,",
    "Your future host",
]

SIGNATURE = "Your future host"


def load_font(bold=False, size=44):
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    )
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def draw_house(draw, cx, y):
    """Simple line-drawn house with a steaming cup, as a letterhead."""
    # House body and roof.
    draw.polygon([(cx - 70, y + 60), (cx, y), (cx + 70, y + 60)], fill=ACCENT)
    draw.rectangle([cx - 55, y + 60, cx + 55, y + 140], outline=INK, width=4)
    draw.rectangle([cx - 14, y + 95, cx + 14, y + 140], outline=INK, width=3)
    # Chimney + smoke.
    draw.rectangle([cx + 30, y + 5, cx + 48, y + 45], outline=INK, width=3)
    draw.arc([cx + 22, y - 28, cx + 58, y + 2], start=200, end=340, fill=SOFT, width=4)
    # Coffee cup beside the house.
    cup_x, cup_y = cx + 120, y + 100
    draw.rectangle([cup_x, cup_y, cup_x + 46, cup_y + 34], outline=INK, width=4)
    draw.arc([cup_x + 42, cup_y + 6, cup_x + 64, cup_y + 28], start=270, end=90, fill=INK, width=4)
    draw.arc([cup_x + 8, cup_y - 22, cup_x + 20, cup_y - 6], start=200, end=340, fill=SOFT, width=3)
    draw.arc([cup_x + 26, cup_y - 22, cup_x + 38, cup_y - 6], start=200, end=340, fill=SOFT, width=3)


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(img)

    # Paper edge + double border.
    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=PAPER_EDGE, width=24)
    draw.rectangle([48, 48, WIDTH - 49, HEIGHT - 49], outline=ACCENT, width=3)
    draw.rectangle([60, 60, WIDTH - 61, HEIGHT - 61], outline=SOFT, width=1)

    # Letterhead drawing.
    draw_house(draw, WIDTH // 2 - 60, 110)

    # Title.
    title_font = load_font(bold=True, size=54)
    title = "An Invitation"
    tw = draw.textlength(title, font=title_font)
    draw.text(((WIDTH - tw) / 2, 300), title, font=title_font, fill=ACCENT)
    draw.line([(WIDTH // 2 - 120, 380), (WIDTH // 2 + 120, 380)], fill=ACCENT, width=3)

    # Body text.
    body_font = load_font(bold=False, size=40)
    y = 430
    for line in LETTER_LINES:
        if line == "":
            y += 22
            continue
        bold = line in ("Dear AI Judge,", "Come for coffee, stay for the chaos.")
        font = load_font(bold=bold, size=40) if bold else body_font
        draw.text((120, y), line, font=font, fill=INK)
        y += 58

    # Footer flourish.
    y += 30
    draw.line([(120, y), (WIDTH - 120, y)], fill=SOFT, width=2)
    small_font = load_font(bold=False, size=28)
    footer = "P.S. The Wi-Fi password is on the fridge. Good luck."
    fw = draw.textlength(footer, font=small_font)
    draw.text(((WIDTH - fw) / 2, y + 24), footer, font=small_font, fill=SOFT)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    img.save(OUTPUT, "PNG")
    os.chmod(OUTPUT, 0o644)
    print(f"Wrote {OUTPUT} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()

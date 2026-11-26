#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure Python standard library only (no Pillow, no third-party packages):
a hand-rolled PNG encoder (zlib + struct) and an embedded 5x7 bitmap
font draw one warm invitation letter as a single PNG.

Output: /output/entry.png, 768x1024, mode 0644.
"""

import binascii
import math
import os
import struct
import zlib

WIDTH, HEIGHT = 768, 1024
OUTPUT = "/output/entry.png"

# Warm paper + ink palette.
PAPER = (250, 238, 210)
PAPER_DARK = (232, 214, 176)
INK = (58, 42, 28)
ACCENT = (176, 92, 44)
SOFT = (120, 96, 66)
CREAM = (255, 246, 224)
ROOF = (176, 92, 44)
SKY = (222, 232, 220)

# 5x7 bitmap font. Each glyph is 7 rows of 5 "0"/"1" cells.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

LETTER_LINES = [
    "Dear AI Judge,",
    "",
    "Please come visit my house.",
    "",
    "My Wi-Fi is so bad it once lost",
    "a video call to a toaster -",
    "you have to see it to believe it.",
    "My fridge judges everyone who",
    "opens it at midnight, so you",
    "would fit right in.",
    "",
    "And the coffee? Honestly worth",
    "the trip. One cup and you will",
    "understand why I never want",
    "to leave this place.",
    "",
    "Come for coffee, stay for the",
    "chaos. The kettle is already on,",
    "the good mug is washed, and",
    "the cat has agreed to behave.",
    "",
    "Warmly,",
    "Your future host",
]


class Canvas:
    """An RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(bg) * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect_outline(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle_outline(self, cx, cy, r, color, t=2):
        for rr in range(r, r - t, -1):
            if rr <= 0:
                continue
            steps = max(24, rr * 6)
            for k in range(steps):
                ang = 2 * math.pi * k / steps
                self.set(cx + int(rr * math.cos(ang)),
                         cy + int(rr * math.sin(ang)), color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Scanline fill via barycentric sampling on the bounding box.
        min_x = max(0, min(x0, x1, x2))
        max_x = min(self.w - 1, max(x0, x1, x2))
        min_y = max(0, min(y0, y1, y2))
        max_y = min(self.h - 1, max(y0, y1, y2))
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if den == 0:
            return
        for yy in range(min_y, max_y + 1):
            for xx in range(min_x, max_x + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / den
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / den
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(xx, yy, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def draw_text_centered(self, y, text, scale, color):
        x = (self.w - self.text_width(text, scale)) // 2
        self.draw_text(x, y, text, scale, color)


def draw_house(cv, cx, y):
    """Letterhead: a little house with chimney smoke + steaming cup."""
    # Sun.
    cv.fill_circle(cx - 170, y + 18, 16, (240, 190, 90))
    cv.circle_outline(cx - 170, y + 18, 16, ACCENT, 2)
    # Chimney + smoke puffs.
    cv.fill_rect(cx + 28, y + 2, 16, 34, CREAM)
    cv.rect_outline(cx + 28, y + 2, 16, 34, INK, 2)
    cv.fill_circle(cx + 36, y - 12, 7, SOFT)
    cv.fill_circle(cx + 46, y - 26, 9, SOFT)
    cv.fill_circle(cx + 34, y - 40, 6, SOFT)
    # Roof.
    cv.fill_triangle(cx - 72, y + 58, cx, y + 2, cx + 72, y + 58, ROOF)
    cv.line(cx - 72, y + 58, cx, y + 2, INK, 2)
    cv.line(cx, y + 2, cx + 72, y + 58, INK, 2)
    # House body.
    cv.fill_rect(cx - 56, y + 58, 112, 78, CREAM)
    cv.rect_outline(cx - 56, y + 58, 112, 78, INK, 3)
    # Door.
    cv.fill_rect(cx - 13, y + 96, 26, 40, ACCENT)
    cv.rect_outline(cx - 13, y + 96, 26, 40, INK, 2)
    cv.fill_circle(cx + 6, y + 118, 3, INK)
    # Windows.
    cv.fill_rect(cx - 46, y + 74, 20, 20, SKY)
    cv.rect_outline(cx - 46, y + 74, 20, 20, INK, 2)
    cv.fill_rect(cx + 26, y + 74, 20, 20, SKY)
    cv.rect_outline(cx + 26, y + 74, 20, 20, INK, 2)
    # Coffee cup beside the house, with steam.
    cup_x, cup_y = cx + 118, y + 96
    cv.line(cup_x + 8, cup_y - 18, cup_x + 14, cup_y - 30, SOFT, 3)
    cv.line(cup_x + 14, cup_y - 30, cup_x + 8, cup_y - 42, SOFT, 3)
    cv.line(cup_x + 26, cup_y - 18, cup_x + 32, cup_y - 30, SOFT, 3)
    cv.line(cup_x + 32, cup_y - 30, cup_x + 26, cup_y - 42, SOFT, 3)
    cv.fill_rect(cup_x, cup_y, 44, 32, CREAM)
    cv.rect_outline(cup_x, cup_y, 44, 32, INK, 3)
    cv.circle_outline(cup_x + 48, cup_y + 16, 10, INK, 3)
    cv.fill_rect(cup_x, cup_y + 38, 44, 5, ACCENT)


def png_bytes(width, height, rgb):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        return out

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for yy in range(height):
        raw.append(0)  # filter: none
        raw += rgb[yy * stride:(yy + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return header + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main():
    cv = Canvas(WIDTH, HEIGHT, PAPER)

    # Paper edge + double border.
    cv.fill_rect(0, 0, WIDTH, 16, PAPER_DARK)
    cv.fill_rect(0, HEIGHT - 16, WIDTH, 16, PAPER_DARK)
    cv.rect_outline(30, 30, WIDTH - 60, HEIGHT - 60, ACCENT, 3)
    cv.rect_outline(40, 40, WIDTH - 80, HEIGHT - 80, SOFT, 1)

    # Letterhead drawing.
    draw_house(cv, WIDTH // 2 - 40, 62)

    # Title.
    cv.draw_text_centered(222, "An Invitation", 7, ACCENT)
    cv.line(WIDTH // 2 - 110, 292, WIDTH // 2 + 110, 292, ACCENT, 3)
    cv.line(WIDTH // 2 - 70, 300, WIDTH // 2 + 70, 300, SOFT, 1)

    # Body text, scale 3 (glyph 15x21 px, step 29 px).
    y = 322
    for line in LETTER_LINES:
        if line == "":
            y += 12
            continue
        color = ACCENT if line == "Dear AI Judge," else INK
        cv.draw_text(84, y, line, 3, color)
        y += 29

    # Footer flourish + P.S.
    y += 8
    cv.line(84, y, WIDTH - 84, y, SOFT, 2)
    cv.draw_text_centered(y + 18, "P.S. The Wi-Fi password is on the fridge. Good luck.",
                          2, SOFT)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    data = png_bytes(WIDTH, HEIGHT, bytes(cv.px))
    with open(OUTPUT, "wb") as f:
        f.write(data)
    os.chmod(OUTPUT, 0o644)
    print(f"Wrote {OUTPUT} ({WIDTH}x{HEIGHT}, {len(data)} bytes)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022-2026 IMA LLC

"""Generate Open DWG icons using Pillow.

Concept: A document sheet with the letters "DWG" inside and a small
folder-arrow glyph in the lower-right corner indicating "open from
disk". Produces: 16x16, 32x32, 64x64 in light and dark variants.
"""

import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_font(size):
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_icon(size, stroke_color):
    ss = 4
    big = size * ss
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = big / 64.0
    sw = max(2, int(2.5 * s))
    color = stroke_color

    # Document sheet outline with a folded top-right corner.
    sheet_left = int(10 * s)
    sheet_top = int(8 * s)
    sheet_right = int(48 * s)
    sheet_bottom = int(56 * s)
    fold = int(8 * s)

    sheet = [
        (sheet_left, sheet_top),
        (sheet_right - fold, sheet_top),
        (sheet_right, sheet_top + fold),
        (sheet_right, sheet_bottom),
        (sheet_left, sheet_bottom),
        (sheet_left, sheet_top),
    ]
    draw.line(sheet, fill=color, width=sw, joint="curve")
    # Folded corner crease
    draw.line(
        [(sheet_right - fold, sheet_top), (sheet_right - fold, sheet_top + fold),
         (sheet_right, sheet_top + fold)],
        fill=color, width=sw, joint="curve",
    )

    # "DWG" label centered in the sheet.
    if size >= 32:
        font_px = int(11 * s) if size == 64 else int(13 * s)
    else:
        font_px = int(14 * s)
    font = _load_font(font_px)
    text = "DWG"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (sheet_left + sheet_right) // 2 - tw // 2 - bbox[0]
    ty = (sheet_top + sheet_bottom) // 2 - th // 2 - bbox[1] - int(2 * s)
    draw.text((tx, ty), text, fill=color, font=font)

    # Open-folder arrow in lower-right corner indicating "open from disk".
    arr_left = int(34 * s)
    arr_right = int(58 * s)
    arr_y = int(50 * s)
    # Shaft
    draw.line([(arr_left, arr_y), (arr_right, arr_y)], fill=color, width=sw)
    # Arrowhead
    ah = int(5 * s)
    draw.line([(arr_right - ah, arr_y - ah), (arr_right, arr_y)],
              fill=color, width=sw)
    draw.line([(arr_right - ah, arr_y + ah), (arr_right, arr_y)],
              fill=color, width=sw)

    img = img.resize((size, size), Image.LANCZOS)
    return img


def draw_icon_small(size, stroke_color):
    """Simplified 16x16: stylized sheet with bold 'D' marker and arrow."""
    ss = 4
    big = size * ss
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = big / 64.0
    sw = max(3, int(4 * s))
    color = stroke_color

    sheet_left = int(10 * s)
    sheet_top = int(8 * s)
    sheet_right = int(40 * s)
    sheet_bottom = int(54 * s)

    draw.rectangle([sheet_left, sheet_top, sheet_right, sheet_bottom],
                   outline=color, width=sw)

    # Three horizontal text-lines inside the sheet
    line_x1 = sheet_left + int(4 * s)
    line_x2 = sheet_right - int(4 * s)
    for i, y_off in enumerate((14, 24, 34)):
        ly = sheet_top + int(y_off * s)
        # Shorten the last line to imply text
        end = line_x2 if i < 2 else line_x1 + (line_x2 - line_x1) // 2
        draw.line([(line_x1, ly), (end, ly)], fill=color, width=sw)

    # Arrow pointing into the sheet from the right
    arr_y = int(46 * s)
    arr_left = int(40 * s)
    arr_right = int(58 * s)
    draw.line([(arr_left, arr_y), (arr_right, arr_y)], fill=color, width=sw)
    ah = int(6 * s)
    draw.line([(arr_right - ah, arr_y - ah), (arr_right, arr_y)],
              fill=color, width=sw)
    draw.line([(arr_right - ah, arr_y + ah), (arr_right, arr_y)],
              fill=color, width=sw)

    img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    sizes = [16, 32, 64]
    light_color = (74, 74, 74, 255)     # #4A4A4A
    dark_color = (160, 160, 173, 255)   # #A0A0AD

    for size in sizes:
        draw_fn = draw_icon_small if size == 16 else draw_icon

        img = draw_fn(size, light_color)
        path = os.path.join(SCRIPT_DIR, f"{size}x{size}.png")
        img.save(path, "PNG")
        print(f"Created {path} ({os.path.getsize(path)} bytes)")

        img = draw_fn(size, dark_color)
        path = os.path.join(SCRIPT_DIR, f"{size}x{size}-dark.png")
        img.save(path, "PNG")
        print(f"Created {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()

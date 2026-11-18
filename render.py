#!/usr/bin/env python3
"""news-image-20261118 composite: six original flat-editorial vignettes
(no text in the art) + crisp PIL labels.

Layout (1024x1024): a navy masthead naming WEDNESDAY 18 NOVEMBER 2026,
a 3x2 grid of vignettes, each with a kicker, a headline and a one-line
sub, and a footer strip with also-today items and sources.
Every story was verified against reputable reporting for 18 November
2026 (see SOURCES.md); all wording is rendered programmatically so
spelling is exact. Run: python3 render.py  ->  entry.png
"""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
OUT = os.path.join(BASE, "entry.png")

W = H = 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
NAVY = (20, 38, 74)
RED = (179, 39, 30)
GOLD = (201, 162, 39)
GREY = (96, 100, 104)
WHITE = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

f_mast = ImageFont.truetype(SERIF_B, 46)
f_tag = ImageFont.truetype(SANS_B, 17)
f_kick = ImageFont.truetype(SANS_B, 15)
f_head = ImageFont.truetype(SANS_B, 20)
f_sub = ImageFont.truetype(SANS, 16)
f_foot_h = ImageFont.truetype(SANS_B, 15)
f_foot = ImageFont.truetype(SANS, 15)
f_src = ImageFont.truetype(SANS, 12)

# (file, focus_x, focus_y, kicker, headline, subline)
# focus = centre of the cover-crop window, as a fraction of the art.
PANELS = [
    ("media-generation-vignette-apec-shenzhen-0-d6fb8e5e-e405-45ea-9d7a-667b5816fcfd.webp",
     0.50, 0.50, "ASIA \u2022 SHENZHEN", "APEC OPENS IN SHENZHEN",
     "Xi keynotes the CEO summit; the first Trump\u2013Xi\u2013Putin talks are set for Thursday."),
    ("media-generation-vignette-trump-marcos-0-f8b87e02-f764-4385-b5f2-e215103f8f66.webp",
     0.50, 0.50, "ASIA \u2022 MANILA", "TRUMP MEETS MARCOS IN MANILA",
     "Bilateral and working lunch, then Trump flies on to China for the APEC summit."),
    ("media-generation-vignette-cyclone-akvan-0-9d8562e6-170f-472c-a30d-8ee464a6c89d.webp",
     0.50, 0.50, "WEATHER \u2022 BAY OF BENGAL", "CYCLONE AKVAN BEARS DOWN ON INDIA",
     "Severe storm brings heavy rain to Andhra Pradesh; landfall is due on Friday."),
    ("media-generation-vignette-nvidia-0-b7a005c3-1f39-4774-992d-dac8981000bf.webp",
     0.50, 0.55, "MARKETS \u2022 TECH", "NVIDIA BEATS FORECASTS; SHARES JUMP",
     "Revenue of $115.8bn tops estimates; first results since Jensen Huang resigned."),
    ("media-generation-vignette-bridge-war-0-eaddbb7b-226a-4212-aff4-f92dfaa0ac33.webp",
     0.50, 0.55, "UKRAINE \u2022 RUSSIA", "BRIDGE WAR: KERCH DOWN, KYIV HIT",
     "The Crimea link is severed and Kyiv\u2019s bridges shut; water and power are cut."),
    ("media-generation-vignette-cop31-0-fe9c08da-f09f-4f97-b2d2-897aa46cf834.webp",
     0.50, 0.55, "CLIMATE \u2022 ANTALYA", "COP31 TALKS IN FINAL STRETCH",
     "A draft deal divides 200 nations over fossil fuels; the deadline is Friday."),
]

ALSO = [
    "Trump lands in Shenzhen tonight ahead of Thursday\u2019s three-way talks",
    "Hormuz: the search goes on for the missing Tara Gas seafarer",
    "Estonia: families rush home before the Russia border shuts on 1 Dec",
]


def cover_crop(img, tw, th, fx, fy):
    """Crop img to the target aspect, centred on (fx, fy), then resize."""
    iw, ih = img.size
    want = tw / th
    if iw / ih > want:  # too wide: trim sides
        cw, ch = int(ih * want), ih
    else:  # too tall: trim top/bottom
        cw, ch = iw, int(iw / want)
    cx = min(max(int(iw * fx), cw // 2), iw - cw // 2)
    cy = min(max(int(ih * fy), ch // 2), ih - ch // 2)
    return img.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)).resize((tw, th), Image.LANCZOS)


def wrap(draw, text, font, width):
    """Greedy word wrap; returns lines that fit `width` pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    # --- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 128], fill=NAVY)
    d.rectangle([0, 128, W, 132], fill=GOLD)
    title = "WEDNESDAY 18 NOVEMBER 2026"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 20), title, font=f_mast, fill=WHITE)
    tag = "T H E   W O R L D \u2019 S   N E W S   I N   O N E   I M A G E"
    tw = d.textlength(tag, font=f_tag)
    d.text(((W - tw) / 2, 84), tag, font=f_tag, fill=GOLD)

    # --- 3x2 grid ------------------------------------------------------
    margin, gap = 24, 14
    row_gap = 16
    cell_w = (W - 2 * margin - 2 * gap) // 3
    img_h = 208
    cell_h = 344
    top = 150
    for i, (fname, fx, fy, kicker, head, sub) in enumerate(PANELS):
        row, col = divmod(i, 3)
        x = margin + col * (cell_w + gap)
        y = top + row * (cell_h + row_gap)
        art = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
        canvas.paste(cover_crop(art, cell_w, img_h, fx, fy), (x, y))
        ty = y + img_h + 10
        d.text((x, ty), kicker, font=f_kick, fill=RED)
        ty += 22
        for line in wrap(d, head, f_head, cell_w)[:2]:
            d.text((x, ty), line, font=f_head, fill=INK)
            ty += 24
        ty += 2
        for line in wrap(d, sub, f_sub, cell_w)[:2]:
            d.text((x, ty), line, font=f_sub, fill=(58, 58, 58))
            ty += 20

    # --- footer strip --------------------------------------------------
    fy0 = top + 2 * cell_h + gap + 16
    d.rectangle([margin, fy0, W - margin, fy0 + 2], fill=NAVY)
    d.text((margin, fy0 + 12), "ALSO TODAY", font=f_foot_h, fill=RED)
    col_w = (W - 2 * margin - 2 * gap) // 3
    for i, item in enumerate(ALSO):
        x = margin + i * (col_w + gap)
        ty = fy0 + 38
        for line in wrap(d, "\u2022  " + item, f_foot, col_w)[:3]:
            d.text((x, ty), line, font=f_foot, fill=INK)
            ty += 19
    src = "Sources: Reuters \u2022 AP \u2022 IMD \u2022 Nvidia \u2022 Aju Press \u2014 see SOURCES.md"
    d.text((margin, H - 30), src, font=f_src, fill=GREY)

    canvas.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {canvas.size} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()

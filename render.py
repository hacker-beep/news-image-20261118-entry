#!/usr/bin/env python3
"""Draw the Wednesday 18 November 2026 front page.

A newspaper front page, not a panel grid: masthead, region strip, one
large lead story, three illustrated stories, a schematic world map with
numbered markers, two small illustrated stories beside the map, and a
grid of text-only story cards. Everything is drawn offline from files
in this repo, so two runs produce byte-identical output.

Usage: render.py <output-png-path>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

CANVAS_W, CANVAS_H = 1024, 1024
EDGE = 22                      # outer margin
CONTENT_W = CANVAS_W - 2 * EDGE

PAPER = (250, 247, 239)
INK = (24, 24, 24)
FAINT = (105, 100, 90)
RULE = (35, 35, 35)
ACCENT = (172, 32, 28)
CHIP = (236, 231, 219)
CARD_LINE = (205, 198, 182)
SEA = (212, 227, 237)
LAND = (231, 223, 195)
LAND_LINE = (178, 170, 138)
GRID = (198, 212, 222)

FONT_DIRS = [
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/dejavu"),
]


def load_font(names, size):
    for name in names:
        for folder in FONT_DIRS:
            path = folder / name
            if path.exists():
                return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def serif_bold(size):
    return load_font(["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"], size)


def serif(size):
    return load_font(["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"], size)


def serif_italic(size):
    return load_font(["LiberationSerif-Italic.ttf", "DejaVuSerif.ttf"], size)


def sans(size):
    return load_font(["LiberationSans-Regular.ttf", "DejaVuSans.ttf"], size)


def sans_bold(size):
    return load_font(["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"], size)


# ---------------------------------------------------------------- stories
# number, region, dateline, headline, deck, art slug (or None),
# longitude, latitude, marker nudge in pixels (to separate close markers)
STORIES = [
    dict(num=1, region="ASIA-PACIFIC", place="SHENZHEN",
         head="APEC opens as Xi welcomes leaders to Shenzhen",
         deck=("The 33rd leaders' meeting runs today and tomorrow. Xi "
               "Jinping delivers the keynote at the CEO Summit opening and "
               "chairs the talks; Donald Trump flies in late tonight, and "
               "a first Trump\u2013Xi\u2013Putin three-way is set for "
               "Thursday."),
         art="apec-shenzhen", lon=114.06, lat=22.54, nudge=(0, 0)),
    dict(num=2, region="ASIA-PACIFIC", place="MANILA",
         head="Trump meets Marcos in Manila",
         deck="Talks and a working lunch at the palace, then on to Shenzhen.",
         art="trump-marcos", lon=120.98, lat=14.60, nudge=(8, 12)),
    dict(num=3, region="ASIA-PACIFIC", place="BAY OF BENGAL",
         head="Cyclone Akvan bears down on India's east coast",
         deck=("Heavy rain reaches Andhra Pradesh today; landfall near "
               "Nellore is due Friday at up to 130 kmph."),
         art="cyclone-akvan", lon=86.0, lat=15.0, nudge=(0, 0)),
    dict(num=4, region="NORTH AMERICA", place="BUSINESS",
         head="Nvidia beats forecasts as AI spending holds",
         deck=("Revenue of $115.8bn, up 103% on the year \u2014 the first "
               "results since Jensen Huang stepped down."),
         art="nvidia", lon=-121.96, lat=37.37, nudge=(-4, -16)),
    dict(num=5, region="EUROPE", place="UKRAINE",
         head="Kerch bridge down, Kyiv bridges shut",
         deck=("The road arch lies in the strait after a second day of "
               "strikes; Kyiv counts water and power cuts."),
         art="bridge-war", lon=36.47, lat=45.35, nudge=(0, -12)),
    dict(num=6, region="MIDDLE EAST", place="ANTALYA",
         head="Climate talks enter final stretch",
         deck="A draft deal splits nearly 200 countries; the deadline is Friday.",
         art="cop31", lon=30.70, lat=36.90, nudge=(-16, -4)),
    dict(num=7, region="MIDDLE EAST", place="GAZA",
         head="Winter rain floods Gaza's tents",
         deck=("UN agencies warn of hypothermia deaths; food aid is cut to "
               "a meal every two days."),
         art=None, lon=34.47, lat=31.50, nudge=(12, 8)),
    dict(num=8, region="AFRICA", place="SUDAN",
         head="Drones kill 1,630 of Sudan's 2,230 civilian dead",
         deck=("The UN rights office counts ten months of war; Kordofan is "
               "hit hardest."),
         art=None, lon=32.53, lat=15.55, nudge=(0, 0)),
    dict(num=9, region="OCEANIA", place="CANBERRA",
         head="Australia sanctions West Bank settlers",
         deck="Three people and four groups listed, a day after Britain acted.",
         art=None, lon=149.13, lat=-35.28, nudge=(0, 0)),
    dict(num=10, region="NORTH AMERICA", place="MARKETS",
         head="Anthropic prices its record IPO today",
         deck=("825 million shares at $70\u2013$78; the books are nearly "
               "seven times covered."),
         art=None, lon=-122.42, lat=37.77, nudge=(-16, 8)),
    dict(num=11, region="NORTH AMERICA", place="SPACE",
         head="Voyager 1 reaches one light-day from Earth",
         deck="Signals now take a full day each way to the 49-year-old probe.",
         art=None, lon=-118.17, lat=34.15, nudge=(14, 10)),
    dict(num=12, region="EUROPE", place="BRUSSELS",
         head="Brussels seeks \u20ac45bn more for Ukraine",
         deck="The loan would cover two-thirds of Kyiv's 2027 budget gap.",
         art=None, lon=4.35, lat=50.85, nudge=(0, 0)),
    dict(num=13, region="ASIA-PACIFIC", place="MUMBAI",
         head="William and Kate meet Modi in Mumbai",
         deck="The royal visit wraps up after Tuesday's Earthshot awards.",
         art=None, lon=72.88, lat=19.08, nudge=(0, 0)),
]

BY_NUM = {s["num"]: s for s in STORIES}

REGIONS = [
    ("ASIA-PACIFIC", 4),
    ("NORTH AMERICA", 3),
    ("EUROPE", 2),
    ("MIDDLE EAST", 2),
    ("AFRICA", 1),
    ("OCEANIA", 1),
]

ALSO_TODAY = [
    "Hormuz: search on for missing Tara Gas seafarer",
    "Estonia: rush home before border shuts 1 Dec",
    "Trump lands in Shenzhen tonight",
]

# ------------------------------------------------------- schematic continents
# Coarse longitude/latitude outlines; drawn small, they read as a world map.
NORTH_AMERICA = [
    (-166, 60), (-158, 58), (-150, 61), (-140, 60), (-135, 57), (-130, 54),
    (-125, 49), (-124, 42), (-120, 35), (-114, 29), (-110, 24), (-105, 20),
    (-97, 16), (-94, 17), (-90, 21), (-87, 21), (-80, 25), (-81, 30),
    (-76, 35), (-74, 40), (-70, 42), (-66, 45), (-60, 47), (-55, 52),
    (-60, 58), (-65, 60), (-68, 58), (-78, 62), (-85, 66), (-92, 66),
    (-95, 69), (-105, 68), (-115, 68), (-125, 70), (-135, 69), (-145, 70),
    (-155, 71), (-165, 68),
]
GREENLAND = [
    (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 76), (-30, 80),
    (-45, 82), (-58, 80), (-60, 75), (-55, 70), (-50, 64),
]
SOUTH_AMERICA = [
    (-77, 7), (-71, 11), (-63, 10), (-53, 5), (-50, 0), (-44, -3),
    (-35, -8), (-37, -13), (-39, -20), (-41, -23), (-48, -27), (-52, -33),
    (-57, -38), (-62, -41), (-65, -45), (-68, -50), (-66, -54), (-70, -54),
    (-73, -50), (-73, -44), (-73, -37), (-71, -30), (-70, -22), (-70, -18),
    (-75, -15), (-79, -8), (-81, -3), (-80, 3),
]
AFRICA = [
    (-17, 15), (-13, 8), (-8, 4), (-4, 5), (3, 6), (6, 4), (9, -1),
    (13, -3), (12, -8), (13, -12), (12, -18), (14, -22), (16, -28),
    (18, -33), (20, -35), (26, -34), (30, -31), (33, -27), (35, -22),
    (36, -18), (40, -15), (40, -10), (42, -5), (41, 0), (46, 5), (51, 10),
    (46, 11), (43, 11), (40, 15), (38, 18), (36, 21), (35, 28), (33, 28),
    (30, 31), (25, 32), (20, 32), (15, 32), (10, 34), (5, 36), (-2, 35),
    (-6, 36), (-10, 31), (-15, 28), (-17, 21),
]
EUROPE = [
    (-9, 37), (-9, 43), (-2, 44), (-2, 48), (-5, 50), (-1, 51), (2, 51),
    (4, 52), (7, 54), (8, 57), (10, 58), (12, 54), (18, 56), (21, 55),
    (24, 58), (28, 60), (30, 62), (28, 66), (32, 70), (40, 68), (44, 67),
    (48, 64), (44, 60), (42, 56), (40, 52), (38, 48), (35, 46), (32, 46),
    (30, 46), (28, 44), (26, 42), (23, 40), (22, 37), (19, 40), (16, 42),
    (14, 45), (12, 44), (10, 44), (7, 44), (3, 43), (0, 39), (-2, 37),
    (-6, 36),
]
ASIA = [
    (30, 70), (45, 68), (60, 69), (75, 72), (90, 75), (105, 77), (120, 73),
    (135, 72), (150, 70), (165, 69), (178, 66), (178, 62), (170, 60),
    (162, 55), (155, 52), (150, 55), (142, 50), (140, 44), (132, 43),
    (127, 39), (122, 36), (120, 30), (118, 24), (112, 21), (108, 17),
    (105, 9), (103, 7), (100, 8), (98, 12), (95, 16), (92, 21), (88, 22),
    (85, 19), (80, 13), (77, 8), (74, 12), (70, 20), (66, 25), (61, 25),
    (57, 26), (53, 26), (50, 29), (48, 30), (44, 29), (40, 31), (36, 36),
    (33, 38), (30, 36), (30, 42), (30, 50), (30, 58),
]
AUSTRALIA = [
    (114, -22), (113, -26), (115, -31), (118, -35), (124, -33), (129, -32),
    (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (147, -39),
    (150, -37), (153, -32), (153, -27), (151, -24), (146, -19), (143, -15),
    (142, -11), (140, -17), (136, -15), (132, -12), (130, -13), (126, -14),
    (122, -17), (118, -20),
]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
JAPAN = [
    (130, 31), (132, 33), (135, 34), (138, 35), (140, 36), (141, 39),
    (142, 42), (144, 44), (142, 45), (140, 42), (138, 38), (135, 34),
    (132, 32),
]
INDONESIA = [
    (95, 5), (100, 0), (105, -3), (110, -6), (115, -8), (120, -10),
    (125, -9), (130, -8), (135, -5), (140, -8), (138, -4), (132, -2),
    (126, 0), (120, 2), (114, 3), (108, 2), (102, 4),
]
MADAGASCAR = [(44, -16), (47, -15), (50, -17), (49, -22), (47, -25), (44, -24)]
NEW_ZEALAND = [(167, -45), (170, -43), (173, -39), (175, -37), (178, -38),
               (176, -40), (173, -42), (170, -44)]

LANDMASSES = [
    NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE, ASIA,
    AUSTRALIA, BRITAIN, JAPAN, INDONESIA, MADAGASCAR, NEW_ZEALAND,
]


# ------------------------------------------------------------------ helpers
def wrap_text(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def art_image(slug):
    hits = sorted(ASSETS.glob(f"media-generation-vignette-{slug}-0-*.webp"))
    if not hits:
        raise FileNotFoundError(f"no vignette for {slug}")
    return Image.open(hits[0]).convert("RGB")


def cover_crop(img, width, height, focus_y=0.5):
    """Resize to cover the box, then crop; focus_y 0..1 picks the band."""
    iw, ih = img.size
    scale = max(width / iw, height / ih)
    nw, nh = max(1, round(iw * scale)), max(1, round(ih * scale))
    resized = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - width) // 2
    top = min(max(0, round((nh - height) * focus_y)), nh - height)
    return resized.crop((left, top, left + width, top + height))


def number_disc(draw, cx, cy, radius, num, font):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=ACCENT, outline=(255, 255, 255), width=1)
    draw.text((cx, cy), str(num), font=font, fill=(255, 255, 255),
              anchor="mm")


def kicker_line(draw, x, y, story, font):
    label = f"{story['region']}  \u00b7  {story['place']}"
    draw.text((x, y), label, font=font, fill=ACCENT)


# ------------------------------------------------------------------ sections
def paint_masthead(draw):
    name_font = serif_bold(58)
    draw.text((CANVAS_W // 2, 18), "THE WORLD HERALD", font=name_font,
              fill=INK, anchor="ma")
    date_font = sans_bold(14)
    draw.text(
        (CANVAS_W // 2, 86),
        "WEDNESDAY, 18 NOVEMBER 2026   \u2014   13 STORIES FROM SIX CONTINENTS",
        font=date_font, fill=INK, anchor="ma")
    draw.line([EDGE, 108, CANVAS_W - EDGE, 108], fill=RULE, width=2)
    draw.line([EDGE, 112, CANVAS_W - EDGE, 112], fill=RULE, width=1)


def paint_region_strip(draw):
    chip_font = sans_bold(12)
    num_font = sans_bold(12)
    top, height = 118, 28
    widths = []
    for name, count in REGIONS:
        w = draw.textlength(f"{name}  {count}", font=chip_font)
        widths.append(w + 26)
    gap = 10
    total = sum(widths) + gap * (len(REGIONS) - 1)
    x = (CANVAS_W - total) // 2
    for (name, count), w in zip(REGIONS, widths):
        draw.rounded_rectangle([x, top, x + w, top + height], radius=6,
                               fill=CHIP)
        draw.text((x + 13, top + 7), name, font=chip_font, fill=INK)
        name_w = draw.textlength(name, font=chip_font)
        draw.text((x + 13 + name_w + 6, top + 7), str(count),
                  font=num_font, fill=ACCENT)
        x += w + gap


def paint_lead(draw, sheet):
    story = BY_NUM[1]
    top, height = 154, 230
    img_w = 520
    art = cover_crop(art_image(story["art"]), img_w, height, focus_y=0.45)
    sheet.paste(art, (EDGE, top))
    draw.rectangle([EDGE, top, EDGE + img_w - 1, top + height - 1],
                   outline=RULE, width=1)
    tx = EDGE + img_w + 16
    tw = CANVAS_W - EDGE - tx
    head_font = serif_bold(32)
    deck_font = serif(16)
    head_lines = wrap_text(draw, story["head"], head_font, tw)
    deck_lines = wrap_text(draw, story["deck"], deck_font, tw)
    block_h = 24 + len(head_lines) * 36 + 16 + len(deck_lines) * 20
    y = top + max(0, (height - block_h) // 2)
    kicker_line(draw, tx, y, story, sans_bold(12))
    number_disc(draw, tx + tw - 12, y + 8, 11, story["num"],
                sans_bold(12))
    y += 24
    for line in head_lines:
        draw.text((tx, y), line, font=head_font, fill=INK)
        y += 36
    y += 4
    draw.line([tx, y, tx + 64, y], fill=ACCENT, width=2)
    y += 12
    for line in deck_lines:
        draw.text((tx, y), line, font=deck_font, fill=INK)
        y += 20


def paint_medium_card(draw, sheet, story, x, top, width, height):
    img_h = 90
    art = cover_crop(art_image(story["art"]), width, img_h, focus_y=0.45)
    sheet.paste(art, (x, top))
    draw.rectangle([x, top, x + width - 1, top + img_h - 1],
                   outline=RULE, width=1)
    y = top + img_h + 6
    kicker_line(draw, x + 1, y, story, sans_bold(10))
    number_disc(draw, x + width - 11, y + 7, 9, story["num"], sans_bold(10))
    y += 15
    head_font = serif_bold(15)
    for line in wrap_text(draw, story["head"], head_font, width - 2)[:2]:
        draw.text((x + 1, y), line, font=head_font, fill=INK)
        y += 17
    y += 2
    deck_font = sans(11)
    for line in wrap_text(draw, story["deck"], deck_font, width - 2)[:2]:
        draw.text((x + 1, y), line, font=deck_font, fill=INK)
        y += 13


def paint_medium_row(draw, sheet):
    top, height = 396, 170
    width = 318
    xs = [EDGE, EDGE + width + 13, EDGE + 2 * (width + 13)]
    for story_num, x in zip((4, 3, 5), xs):
        paint_medium_card(draw, sheet, BY_NUM[story_num], x, top, width,
                          height)


def paint_map(draw, box):
    x0, y0, w, h = box
    header_h = 26
    draw.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=SEA,
                   outline=RULE, width=1)
    draw.text((x0 + 10, y0 + 5), "WHERE THE NEWS IS",
              font=sans_bold(12), fill=INK)
    draw.text((x0 + 10, y0 + 5 + 13),
              "numbers match the stories on this page",
              font=sans(10), fill=FAINT)
    my0 = y0 + header_h
    mh = h - header_h

    def project(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * w
        py = my0 + (84.0 - lat) / 144.0 * mh
        return px, py

    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0)
        draw.line([gx, my0, gx, y0 + h - 1], fill=GRID, width=1)
    for lat in (60, 30, 0, -30):
        _, gy = project(0, lat)
        draw.line([x0, gy, x0 + w - 1, gy], fill=GRID, width=1)
    for mass in LANDMASSES:
        pts = [project(lon, lat) for lon, lat in mass]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE, width=1)

    num_font = sans_bold(11)
    for story in STORIES:
        px, py = project(story["lon"], story["lat"])
        dx, dy = story["nudge"]
        cx, cy = px + dx, py + dy
        if dx or dy:
            draw.line([px, py, cx, cy], fill=FAINT, width=1)
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=ACCENT)
        number_disc(draw, round(cx), round(cy), 9, story["num"], num_font)


def paint_mini_card(draw, sheet, story, x, top, width, height):
    img_w = 150
    art = cover_crop(art_image(story["art"]), img_w, height, focus_y=0.5)
    sheet.paste(art, (x, top))
    draw.rectangle([x, top, x + img_w - 1, top + height - 1],
                   outline=RULE, width=1)
    tx = x + img_w + 10
    tw = x + width - tx
    kicker_line(draw, tx, top + 2, story, sans_bold(9))
    number_disc(draw, tx + tw - 9, top + 9, 8, story["num"], sans_bold(9))
    y = top + 16
    head_font = serif_bold(13)
    for line in wrap_text(draw, story["head"], head_font, tw)[:3]:
        draw.text((tx, y), line, font=head_font, fill=INK)
        y += 15
    y += 2
    deck_font = sans(10)
    for line in wrap_text(draw, story["deck"], deck_font, tw)[:2]:
        draw.text((tx, y), line, font=deck_font, fill=INK)
        y += 12


def paint_map_band(draw, sheet):
    top, height = 578, 220
    map_w = 640
    paint_map(draw, (EDGE, top, map_w, height))
    col_x = EDGE + map_w + 12
    col_w = CANVAS_W - EDGE - col_x
    mini_h = (height - 12) // 2
    paint_mini_card(draw, sheet, BY_NUM[2], col_x, top, col_w, mini_h)
    paint_mini_card(draw, sheet, BY_NUM[6], col_x, top + mini_h + 12,
                    col_w, mini_h)


def paint_text_card(draw, story, x, top, width, height):
    draw.rectangle([x, top, x + width - 1, top + height - 1],
                   outline=CARD_LINE, width=1)
    pad = 8
    y = top + pad
    number_disc(draw, x + pad + 8, y + 8, 8, story["num"], sans_bold(9))
    kicker_line(draw, x + pad + 20, y + 1, story, sans_bold(9))
    y += 19
    head_font = serif_bold(13)
    for line in wrap_text(draw, story["head"], head_font,
                          width - 2 * pad)[:2]:
        draw.text((x + pad, y), line, font=head_font, fill=INK)
        y += 15
    y += 2
    deck_font = sans(10)
    for line in wrap_text(draw, story["deck"], deck_font,
                          width - 2 * pad)[:2]:
        draw.text((x + pad, y), line, font=deck_font, fill=INK)
        y += 12


def paint_also_box(draw, x, top, width, height):
    draw.rectangle([x, top, x + width - 1, top + height - 1],
                   fill=CHIP, outline=CARD_LINE, width=1)
    pad = 8
    draw.text((x + pad, top + pad), "ALSO TODAY", font=sans_bold(10),
              fill=ACCENT)
    y = top + pad + 15
    item_font = sans(10)
    for item in ALSO_TODAY:
        for line in wrap_text(draw, f"\u2022  {item}", item_font,
                              width - 2 * pad):
            draw.text((x + pad, y), line, font=item_font, fill=INK)
            y += 12
        y += 1


def paint_grid(draw):
    top = 810
    row_h = 94
    col_w = 236
    xs = [EDGE + i * (col_w + 12) for i in range(4)]
    first_row = (7, 8, 9, 10)
    second_row = (11, 12, 13)
    for num, x in zip(first_row, xs):
        paint_text_card(draw, BY_NUM[num], x, top, col_w, row_h)
    for num, x in zip(second_row, xs[:3]):
        paint_text_card(draw, BY_NUM[num], x, top + row_h + 10, col_w, row_h)
    paint_also_box(draw, xs[3], top + row_h + 10, col_w, row_h)


# ---------------------------------------------------------------------- main
def build_front_page():
    sheet = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    draw = ImageDraw.Draw(sheet)
    paint_masthead(draw)
    paint_region_strip(draw)
    paint_lead(draw, sheet)
    paint_medium_row(draw, sheet)
    paint_map_band(draw, sheet)
    paint_grid(draw)
    return sheet


def main(argv):
    if len(argv) < 2:
        print("usage: render.py <output-png-path>", file=sys.stderr)
        return 2
    out_path = Path(argv[1])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet = build_front_page()
    sheet.save(out_path, format="PNG", optimize=True)
    size = out_path.stat().st_size
    print(f"wrote {out_path} ({sheet.size[0]}x{sheet.size[1]}, "
          f"{size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

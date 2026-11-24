#!/usr/bin/env python3
"""The World in One Page -- Tuesday, 24 November 2026.

Draws a newspaper front page summing up the day's world news and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Pure stdlib + Pillow, no network, no file reads, fully deterministic:
the same run always writes the same bytes.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (248, 244, 233)
INK = (26, 26, 26)
MUTED = (90, 83, 72)
RED = (163, 22, 33)
GREEN = (18, 110, 58)
RULE = (26, 26, 26)
PANEL = (240, 234, 219)
PANEL_EDGE = (180, 172, 150)

FONT_PATHS = {
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def font(name, size):
    path = FONT_PATHS[name]
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size=size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, max_width, fill=INK, spacing=5,
               max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, max_width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError("text overflows: %r needs %d lines, max %d"
                         % (text[:40], len(lines), max_lines))
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def centered(draw, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rule(draw, y, x0=None, x1=None, width=2):
    x0 = MARGIN if x0 is None else x0
    x1 = W - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)
    return y + width


def draw_masthead(draw):
    title = font("serif_bold", 60)
    centered(draw, 26, "THE WORLD IN ONE PAGE", title)
    date_f = font("sans_bold", 26)
    centered(draw, 102, "TUESDAY, 24 NOVEMBER 2026", date_f, fill=RED)
    sub_f = font("sans", 13)
    centered(draw, 140,
             "THE DAY'S WORLD NEWS  -  ONE PAGE, EVERY STORY THAT MATTERED",
             sub_f, fill=MUTED)
    rule(draw, 164)


def draw_lead(draw):
    x = MARGIN
    y = 182
    kicker = font("sans_bold", 16)
    draw.text((x, y), "LEAD STORY  -  TECHNOLOGY & MARKETS", font=kicker,
              fill=RED)
    y += 26
    head = font("serif_bold", 38)
    y = text_block(draw, x, y,
                   "Huang is back at Nvidia -\nshares soar 31.5% in a day",
                   head, 620, spacing=4, max_lines=2)
    y += 8
    body = font("sans", 19)
    y = text_block(
        draw, x, y,
        "Eleven days after resigning over a scandal, Jensen Huang was "
        "reinstated as chief executive on Monday. Nvidia shares jumped "
        "31.5% - their biggest one-day gain in 23 years - restoring "
        "almost $1 trillion in value. The S&P 500 rose 4.7% and the "
        "Nasdaq 6.5%, and Asian markets rallied on Tuesday.",
        body, 620, spacing=6, max_lines=5)
    # Right-hand numbers panel.
    px0, py0, px1, py1 = 692, 182, W - MARGIN, 440
    draw.rectangle([px0, py0, px1, py1], fill=PANEL, outline=PANEL_EDGE,
                   width=2)
    cx = px0 + 18
    lab = font("sans_bold", 14)
    draw.text((cx, py0 + 12), "THE DAY IN NUMBERS", font=lab, fill=MUTED)
    big = font("sans_bold", 52)
    draw.text((cx, py0 + 38), "+31.5%", font=big, fill=GREEN)
    cap = font("sans", 15)
    draw.text((cx, py0 + 98), "Nvidia shares, Monday", font=cap, fill=INK)
    draw.text((cx, py0 + 118), "Biggest one-day gain in 23 years;",
              font=cap, fill=INK)
    draw.text((cx, py0 + 138), "almost $1 trillion restored.",
              font=cap, fill=INK)
    rule(draw, py0 + 166, x0=px0 + 18, x1=px1 - 18, width=1)
    draw.text((cx, py0 + 176), "ASIAN MARKETS, TUESDAY", font=lab,
              fill=MUTED)
    bar_f = font("sans", 14)
    bars = [("Nikkei", "+4.5%", 4.5), ("Kospi", "+7.5%", 7.5),
            ("Taiwan", "+9.1%", 9.1)]
    by = py0 + 198
    for name, val, pct in bars:
        draw.text((cx, by), name, font=bar_f, fill=INK)
        bx0 = cx + 62
        bw = int(150 * pct / 10.0)
        draw.rectangle([bx0, by + 2, bx0 + bw, by + 14], fill=GREEN)
        draw.text((bx0 + bw + 6, by), val, font=bar_f, fill=GREEN)
        by += 19
    rule(draw, 456)


GRID = [
    ("TRADE",
     "US blacklists chip firm\nin Nvidia scandal",
     "Washington put Singapore-based Megaspeed on its export blacklist, "
     "accusing it of diverting AI chips to China. Singapore said it will "
     "keep investigating."),
    ("MIDDLE EAST",
     "Israeli strike kills\nthree in Gaza",
     "An airstrike hit near a police outpost in Khan Younis in southern "
     "Gaza on Tuesday, medics said. At least three Palestinians were "
     "killed, including a UN aid worker."),
    ("CYBERWAR",
     "US suspects Iran in\ntanker cyberattacks",
     "Washington is investigating whether Iran is behind dozens of "
     "cyberattacks on energy tankers, the Wall Street Journal reported. "
     "As many as 50 ships may have been hit."),
    ("UKRAINE",
     "Odesa still dark after\ngrid strikes",
     "Russian strikes have left Odesa without power, heat and water, with "
     "about 240,000 people without heating. Kyiv says Moscow hits lines "
     "again as soon as they are repaired."),
    ("ASIA",
     "Magnitude 5.3 quake\nhits Nepal",
     "An earthquake struck Koshi province in eastern Nepal on Tuesday, "
     "the European-Mediterranean Seismological Centre said."),
    ("SPACE",
     "China to launch\nShenzhou-24",
     "China will launch its Shenzhou-24 spacecraft on Wednesday carrying "
     "a Pakistani astronaut - the first foreigner to board China's space "
     "station."),
]


def draw_grid(draw):
    col_w = (CW - 24) // 2  # 464
    row_h = 128
    y0 = 472
    kicker = font("sans_bold", 14)
    head = font("serif_bold", 23)
    body = font("sans", 15)
    for i, (kick, headline, text) in enumerate(GRID):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (col_w + 24)
        y = y0 + row * row_h
        draw.text((x, y), kick, font=kicker, fill=RED)
        y += 22
        y = text_block(draw, x, y, headline, head, col_w, spacing=2,
                       max_lines=2)
        y += 3
        text_block(draw, x, y, text, body, col_w, spacing=3, max_lines=3)
    rule(draw, y0 + 3 * row_h + 4)


BRIEFS = [
    "Indonesia charges a former police chief with treason over alleged "
    "wiretapping aimed at President Prabowo.",
    "Mexico says alleged drug lord \u201cEl Chapo Isidro\u201d will be tried "
    "at home despite a US extradition request.",
    "Spain: polls put the right on course to oust Prime Minister S\u00e1nchez "
    "in Sunday\u2019s election.",
]


def draw_briefs(draw):
    y = 866
    head = font("sans_bold", 16)
    draw.text((MARGIN, y), "IN BRIEF", font=head, fill=RED)
    y += 26
    body = font("sans", 16)
    for item in BRIEFS:
        draw.text((MARGIN, y), "\u2022", font=body, fill=RED)
        y = text_block(draw, MARGIN + 20, y, item, body, CW - 20,
                       spacing=3, max_lines=1)
        y += 2
    rule(draw, 968)
    foot = font("sans", 13)
    centered(draw, 978,
             "All events of Tuesday, 24 November 2026  -  Sources: Reuters, "
             "NPR, The Wall Street Journal, Xinhua",
             foot, fill=MUTED)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw)
    draw_grid(draw)
    draw_briefs(draw)

    img.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes)" % (out_path, size))
    if size > 1048576:
        print("ERROR: output exceeds 1 MiB", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

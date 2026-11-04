"""
Erzeugt assets/qr-poster.png - ein Bild im Handy-Hochformat (1080x1920) mit
QR-Code zur Downloadseite, grafisch an index.html angelehnt.

Benoetigt: pip install qrcode pillow
Aufruf:    python tools/make-qr-poster.py
"""

from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- Konfiguration

URL = "https://lethe-bremen.github.io/LED.11IGN.A60/"

W, H = 1080, 1920

NAVY = (20, 56, 104)
NAVY_DARK = (14, 40, 71)
MAGENTA = (182, 31, 82)
WHITE = (255, 255, 255)
KICKER = (168, 188, 214)
MUTED = (185, 198, 216)

BAR_H = 160          # weisse Logoleiste
BAND_BOTTOM = 760    # Unterkante des Schiff-Bands

ROOT = Path(__file__).resolve().parent.parent
SHIP = ROOT / "assets" / "hero-ship.jpg"
LOGO = ROOT / "assets" / "lethe-logo.jpg"
OUT = ROOT / "assets" / "qr-poster.png"

FONTS = Path("C:/Windows/Fonts")


def font(name, size):
    for candidate in (name, {"segoeuib.ttf": "arialbd.ttf",
                             "segoeui.ttf": "arial.ttf",
                             "seguisb.ttf": "arialbd.ttf"}.get(name, "arial.ttf")):
        path = FONTS / candidate
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


BOLD = lambda s: font("segoeuib.ttf", s)
SEMI = lambda s: font("seguisb.ttf", s)
REG = lambda s: font("segoeui.ttf", s)


def center(draw, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)


def tracked(draw, x, y, text, fnt, fill, tracking):
    """Text mit Sperrsatz - PIL kann das nicht von sich aus."""
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def tracked_center(draw, y, text, fnt, fill, tracking):
    width = sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking
    tracked(draw, (W - width) / 2, y, text, fnt, fill, tracking)


# ---------------------------------------------------------------- Hintergrund

# Der Bereich unter dem Band ist einfarbig - das Schiff-Band blendet per
# Verlauf genau in diesen Ton aus, so entsteht keine sichtbare Kante.
poster = Image.new("RGB", (W, H), NAVY_DARK)

# Schiff-Band: auf Breite skalieren, mittig auf Bandhoehe beschneiden
band_h = BAND_BOTTOM - BAR_H
ship = Image.open(SHIP).convert("RGB")
scale = W / ship.width
ship = ship.resize((W, round(ship.height * scale)), Image.LANCZOS)
top = max(0, (ship.height - band_h) // 2)
ship = ship.crop((0, top, W, min(top + band_h, ship.height)))
if ship.height < band_h:
    ship = ship.resize((W, band_h), Image.LANCZOS)

# Navy-Verlauf darueber: oben nur leicht getoent, damit das Schiff wirkt,
# nach unten bis auf volle Deckung - dadurch geht das Band nahtlos in die
# einfarbige Flaeche ueber, auf der Headline und QR-Code stehen.
overlay = Image.new("RGBA", (1, band_h))
for i in range(band_h):
    t = i / max(band_h - 1, 1)
    alpha = round(255 * min(1.0, 0.28 + 0.72 * t ** 2.2))
    col = tuple(round(NAVY[c] + (NAVY_DARK[c] - NAVY[c]) * t) for c in range(3))
    overlay.putpixel((0, i), col + (alpha,))
ship = Image.alpha_composite(ship.convert("RGBA"), overlay.resize((W, band_h)))
poster.paste(ship.convert("RGB"), (0, BAR_H))

draw = ImageDraw.Draw(poster)

# ---------------------------------------------------------------- Logoleiste

draw.rectangle([0, 0, W, BAR_H], fill=WHITE)

logo = Image.open(LOGO).convert("RGB")
logo_h = 68
logo = logo.resize((round(logo.width * logo_h / logo.height), logo_h), Image.LANCZOS)
poster.paste(logo, (64, (BAR_H - logo_h) // 2))

# Badge oben rechts - traegt seit dem Umbenennen die Typbezeichnung
badge_font = BOLD(30)
badge_text = "LED.11IGN.A60"
badge_tracking = 3
badge_w = sum(draw.textlength(c, font=badge_font) + badge_tracking for c in badge_text) - badge_tracking
pad_x, pad_y = 30, 16
bx1 = W - 64
bx0 = bx1 - (badge_w + 2 * pad_x)
by0 = (BAR_H - (28 + 2 * pad_y)) // 2
by1 = by0 + 28 + 2 * pad_y
draw.rounded_rectangle([bx0, by0, bx1, by1], radius=(by1 - by0) // 2, outline=MAGENTA, width=3)
tracked(draw, bx0 + pad_x, by0 + pad_y - 4, badge_text, badge_font, MAGENTA, badge_tracking)

# ---------------------------------------------------------------- Headline

tracked_center(draw, 812, "DOCUMENTS FOR DOWNLOAD", BOLD(26), KICKER, 4)
center(draw, 862, "A-60 Sliding Door System", BOLD(66), WHITE)
center(draw, 962, "Single-leaf sliding fire door", REG(38), (219, 228, 240))
draw.rectangle([(W - 130) / 2, 1040, (W + 130) / 2, 1047], fill=MAGENTA)

# ---------------------------------------------------------------- QR-Code

center(draw, 1082, "Scan for certificates, drawings & manual", SEMI(32), KICKER)

CARD = 590
QR_TARGET = 540      # Richtwert; die echte Groesse wird darunter glattgerechnet

# Erst die Modulanzahl ermitteln, dann eine ganzzahlige Boxgroesse waehlen.
# Wuerde man das fertige Bild auf eine Zielbreite skalieren, kaemen bei
# krummem Faktor unterschiedlich breite Module heraus - genau das laesst
# QR-Codes an schlechtem Licht scheitern. border=4 ist die Ruhezone laut Norm.
probe = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4)
probe.add_data(URL)
probe.make(fit=True)
modules = probe.modules_count + 2 * probe.border
box = max(1, round(QR_TARGET / modules))

qr = qrcode.QRCode(
    version=probe.version,
    error_correction=qrcode.constants.ERROR_CORRECT_Q,
    box_size=box,
    border=4,
)
qr.add_data(URL)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="#0e2847", back_color="white").convert("RGB")

cx = (W - CARD) // 2
cy = 1130
draw.rounded_rectangle([cx, cy, cx + CARD, cy + CARD], radius=28, fill=WHITE)
poster.paste(qr_img, (cx + (CARD - qr_img.width) // 2, cy + (CARD - qr_img.height) // 2))
print(f"QR: {modules} Module x {box} px = {qr_img.width} px, Version {qr.version}")

# ---------------------------------------------------------------- Fusszeile

center(draw, cy + CARD + 42, "lethe-bremen.github.io/LED.11IGN.A60", SEMI(32), WHITE)
center(draw, H - 74, "Lethe Exterior Doors GmbH  ·  Bremen, Germany  ·  lethe-bremen.de",
       REG(25), MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
poster.save(OUT, optimize=True)
print(f"{OUT}  ({OUT.stat().st_size / 1024:.0f} KB, {W}x{H})")

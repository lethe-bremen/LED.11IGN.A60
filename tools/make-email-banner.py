"""
Erzeugt assets/email-banner.png - ein Banner fuer den Mailversand, im Layout
von index.html. Datei ist 1200x560, eingebunden wird sie mit width="600":
doppelte Aufloesung, damit sie auf Retina-Displays scharf bleibt.

Benoetigt: pip install qrcode pillow
Aufruf:    python tools/make-email-banner.py
"""

from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- Konfiguration

URL = "https://lethe-bremen.github.io/LED.11IGN.A60/"
URL_TEXT = "lethe-bremen.github.io/LED.11IGN.A60"

W, H = 1200, 560
BAR_H = 120          # weisse Logoleiste
PAD = 56             # Seitenrand

NAVY = (20, 56, 104)
NAVY_DARK = (14, 40, 71)
MAGENTA = (182, 31, 82)
WHITE = (255, 255, 255)
KICKER = (168, 188, 214)

ROOT = Path(__file__).resolve().parent.parent
SHIP = ROOT / "assets" / "hero-ship.jpg"
LOGO = ROOT / "assets" / "lethe-logo.jpg"
OUT = ROOT / "assets" / "email-banner.png"

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


def tracked(draw, x, y, text, fnt, fill, tracking):
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def tracked_width(draw, text, fnt, tracking):
    return sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking


# ---------------------------------------------------------------- Hintergrund

banner = Image.new("RGB", (W, H), NAVY_DARK)

band_h = H - BAR_H
ship = Image.open(SHIP).convert("RGB")
ship = ship.resize((W, round(ship.height * W / ship.width)), Image.LANCZOS)

# Ausschnitt so legen, dass die Yacht komplett im Band steht
top = max(0, min(round(ship.height * 0.52) - band_h // 2, ship.height - band_h))
ship = ship.crop((0, top, W, top + band_h))

# Waagerechter Navy-Verlauf: links deckend fuer den Text, nach rechts
# durchlaessiger, damit das Schiff sichtbar wird
overlay = Image.new("RGBA", (W, 1))
for x in range(W):
    t = x / (W - 1)
    alpha = round(255 * (0.93 - 0.38 * t ** 1.3))
    col = tuple(round(NAVY_DARK[c] + (NAVY[c] - NAVY_DARK[c]) * t) for c in range(3))
    overlay.putpixel((x, 0), col + (alpha,))
ship = Image.alpha_composite(ship.convert("RGBA"), overlay.resize((W, band_h)))
banner.paste(ship.convert("RGB"), (0, BAR_H))

draw = ImageDraw.Draw(banner)

# ---------------------------------------------------------------- Logoleiste

draw.rectangle([0, 0, W, BAR_H], fill=WHITE)

logo = Image.open(LOGO).convert("RGB")
logo_h = 56
logo = logo.resize((round(logo.width * logo_h / logo.height), logo_h), Image.LANCZOS)
banner.paste(logo, (PAD, (BAR_H - logo_h) // 2))

badge_font, badge_text, badge_tr = BOLD(26), "LED.11IGN.A60", 3
bw = tracked_width(draw, badge_text, badge_font, badge_tr)
px, py = 26, 14
bx1, by0 = W - PAD, (BAR_H - (26 + 2 * py)) // 2
bx0, by1 = bx1 - (bw + 2 * px), by0 + 26 + 2 * py
draw.rounded_rectangle([bx0, by0, bx1, by1], radius=(by1 - by0) // 2, outline=MAGENTA, width=3)
tracked(draw, bx0 + px, by0 + py - 4, badge_text, badge_font, MAGENTA, badge_tr)

# ---------------------------------------------------------------- QR-Code

CARD, QR_TARGET = 340, 300

probe = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4)
probe.add_data(URL)
probe.make(fit=True)
modules = probe.modules_count + 2 * probe.border
box = max(1, round(QR_TARGET / modules))

qr = qrcode.QRCode(version=probe.version,
                   error_correction=qrcode.constants.ERROR_CORRECT_Q,
                   box_size=box, border=4)
qr.add_data(URL)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="#0e2847", back_color="white").convert("RGB")

cx = W - PAD - CARD
cy = BAR_H + (band_h - CARD) // 2
draw.rounded_rectangle([cx, cy, cx + CARD, cy + CARD], radius=20, fill=WHITE)
banner.paste(qr_img, (cx + (CARD - qr_img.width) // 2, cy + (CARD - qr_img.height) // 2))

# ---------------------------------------------------------------- Text links

draw.text((PAD, 248), "A-60 Sliding Door System", font=BOLD(48), fill=WHITE)
draw.rectangle([PAD, 318, PAD + 90, 323], fill=MAGENTA)
draw.text((PAD, 340), "Certificates · Drawings · Manual · Photos", font=REG(24), fill=KICKER)
draw.text((PAD, 398), URL_TEXT, font=SEMI(30), fill=WHITE)

OUT.parent.mkdir(parents=True, exist_ok=True)
banner.save(OUT, optimize=True)
print(f"{OUT}  ({OUT.stat().st_size / 1024:.0f} KB, {W}x{H}, Anzeige mit width=\"{W // 2}\")")
print(f"QR: {modules} Module x {box} px = {qr_img.width} px "
      f"(auf {W // 2} px Anzeigebreite: {qr_img.width // 2} px)")

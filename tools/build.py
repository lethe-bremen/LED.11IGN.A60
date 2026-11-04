#!/usr/bin/env python3
"""
Baut die Seite aus den Ordnern.

    python tools/build.py             baut nach _site/
    python tools/build.py --verify URL  prueft nach dem Veroeffentlichen, ob die
                                        Live-Seite den neuen Stand ausliefert

Quellen
    index.template.html   Rahmen der Seite (Kopf, Begruessung, Impressum, Stil)
    documents.json        Verzeichnis der Dokumente (Titel, Beschreibung, Dateimuster)
    files/                Dokumente; neue Version einfach dazulegen
    files/media/          Fotos (jpg/png/webp) und Videos (mp4/webm); alles dort erscheint
    assets/               Logo, Icons, Poster, Banner

Ergebnis in _site/ (wird von GitHub veroeffentlicht, nicht eingecheckt).
Bei einem Fehler wird nichts veroeffentlicht und die bisherige Seite bleibt online.

Benoetigt: pip install -r requirements.txt   (pillow, pypdf)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urljoin

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
TEMPLATE = ROOT / "index.template.html"
MANIFEST = ROOT / "documents.json"
FILES = ROOT / "files"
MEDIA = FILES / "media"
ASSETS = ROOT / "assets"

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXT = {".mp4", ".m4v", ".webm"}
IGNORE_NAMES = {"thumbs.db", "desktop.ini", ".ds_store"}
TYPE_CLASS = {"dwg": "dwg", "dxf": "dwg", "xlsm": "xlsm", "xlsx": "xlsm", "xls": "xlsm"}

PHOTO_MAX_PX = 2000          # lange Kante, darueber wird verkleinert
PHOTO_BIG_BYTES = 700 * 1024  # darueber wird neu komprimiert
PHOTO_QUALITY = 85
HARD_LIMIT = 95 * 1024 * 1024   # GitHub lehnt Dateien ab 100 MB ab
WARN_BYTES = 25 * 1024 * 1024   # ab hier ist die Datei fuer Handys eine Zumutung
SITE_WARN = 700 * 1024 * 1024   # Pages-Grenze liegt bei 1 GB

VERSION_RE = r"[Vv]?\d+(?:\.\d+)*"
DOWNLOAD_SVG = (
    '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M8 1.5v9"/><path d="M4.5 7.5 8 11l3.5-3.5"/><path d="M2 13.5h12"/></svg>'
)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

errors: list[str] = []
warnings: list[str] = []


# --------------------------------------------------------------------------- Ausgabe

def say(msg: str = "") -> None:
    print(msg, flush=True)


def fail(msg: str) -> None:
    errors.append(msg)
    say(f"::error::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"FEHLER:  {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    say(f"::warning::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"Hinweis: {msg}")


# --------------------------------------------------------------------------- Helfer

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def natural_key(name: str):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", name.lower())]


def fmt_size(n: int) -> str:
    kb = n / 1024
    return f"{kb:.0f} KB" if kb < 1000 else f"{kb / 1024:.1f} MB"


def file_hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def version_key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v))


def version_vars(v: str) -> dict[str, str]:
    digits = v.lstrip("Vv")
    number = str(int(re.match(r"\d+", digits).group())) if digits else ""
    return {"v": v, "V": f"V{digits}" if digits else "", "n": number}


def fill(template: str, v: str) -> str:
    out = template
    for key, val in version_vars(v).items():
        out = out.replace("{" + key + "}", val)
    return out


def pattern_to_regex(pattern: str) -> re.Pattern:
    parts = pattern.split("{v}")
    if len(parts) > 2:
        raise ValueError("'{v}' darf im Muster nur einmal vorkommen")
    if len(parts) == 1:
        return re.compile(re.escape(pattern))
    return re.compile(re.escape(parts[0]) + f"(?P<v>{VERSION_RE})" + re.escape(parts[1]))


def usable(path: Path) -> bool:
    n = path.name
    return path.is_file() and not n.startswith((".", "~$")) and n.lower() not in IGNORE_NAMES


def today() -> str:
    try:
        from zoneinfo import ZoneInfo
        d = dt.datetime.now(ZoneInfo("Europe/Berlin"))
    except Exception:
        d = dt.datetime.now()
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def pdf_pages(path: Path) -> int | None:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except ImportError:
        warn("pypdf fehlt, Seitenzahlen werden nicht angezeigt (pip install pypdf)")
    except Exception as e:  # beschaedigte oder verschluesselte PDF
        warn(f"{path.name}: Seitenzahl nicht lesbar ({type(e).__name__})")
    return None


# --------------------------------------------------------------------------- Dokumente

def item_html(name: str, desc: str, meta: list[str], href: str, ext: str) -> str:
    cls = TYPE_CLASS.get(ext)
    tile = f'<span class="type {cls}">' if cls else '<span class="type">'
    return (
        '      <li class="item">\n'
        f"        {tile}{esc(ext.upper())}</span>\n"
        '        <div class="body">\n'
        "          <div>\n"
        f'            <p class="name">{esc(name)}</p>\n'
        + (f'            <p class="desc">{esc(desc)}</p>\n' if desc else "")
        + f'            <p class="meta">{" &middot; ".join(esc(m) for m in meta)}</p>\n'
        "          </div>\n"
        f'          <a class="dl" href="{href}" download>\n'
        f"            {DOWNLOAD_SVG}\n"
        "            Download\n"
        "          </a>\n"
        "        </div>\n"
        "      </li>\n"
    )


def section_html(title: str, note: str, items: list[str]) -> str:
    return (
        "<section>\n"
        '  <div class="wrap">\n'
        f"    <h2>{esc(title)}</h2>\n"
        + (f'    <p class="section-note">{esc(note)}</p>\n' if note else "")
        + '\n    <ul class="list">\n'
        + "\n".join(items)
        + "    </ul>\n"
        "  </div>\n"
        "</section>\n"
    )


def publish_file(src: Path) -> str:
    """Kopiert die Datei an dieselbe Stelle unter _site und liefert den Link samt Cache-Stempel."""
    rel = src.relative_to(ROOT)
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"{quote(rel.as_posix())}?v={file_hash(src)}"


def build_documents(manifest: dict) -> str:
    candidates = sorted((p for p in FILES.iterdir() if usable(p)), key=lambda p: natural_key(p.name))
    claimed: set[str] = set()
    blocks: list[str] = []
    groups: dict[str, dict[tuple, list[str]]] = {}   # 'group' -> Version -> Dateien

    for section in manifest.get("sections", []):
        rendered: list[str] = []
        for item in section.get("items", []):
            pattern = item.get("pattern", "")
            if not pattern or not item.get("desc"):
                fail(f"Abschnitt '{section.get('title')}': jeder Eintrag braucht 'pattern' und 'desc'")
                continue
            try:
                rx = pattern_to_regex(pattern)
            except ValueError as e:
                fail(f"{pattern}: {e}")
                continue

            hits = []
            for p in candidates:
                m = rx.fullmatch(p.name)
                if m:
                    v = m.groupdict().get("v") or ""
                    hits.append((version_key(v), p.name, v, p))
            if not hits:
                fail(f"Keine Datei in files/ passt zu '{pattern}' (Eintrag: {item.get('desc')[:50]}...)")
                continue

            hits.sort(key=lambda h: (h[0], h[1]))
            _, _, version, chosen = hits[-1]
            claimed.update(h[3].name for h in hits)
            if item.get("group"):
                groups.setdefault(item["group"], {}).setdefault(version_key(version), []).append(chosen.name)
            for old in hits[:-1]:
                say(f"  {old[3].name}: durch {chosen.name} abgeloest, wird nicht veroeffentlicht")

            ext = chosen.suffix.lstrip(".").lower()
            meta = [ext.upper()]
            if ext == "pdf":
                pages = pdf_pages(chosen)
                if pages:
                    meta.append(f"{pages} page" + ("" if pages == 1 else "s"))
            meta.append(fmt_size(chosen.stat().st_size))
            if item.get("extra"):
                meta.append(item["extra"])

            name = fill(item["name"], version) if item.get("name") else chosen.name
            desc = fill(item["desc"], version)
            rendered.append(item_html(name, desc, meta, publish_file(chosen), ext))
            say(f"  {chosen.name}")

        if rendered:
            blocks.append(section_html(section.get("title", ""), section.get("note", ""), rendered))

    # Zusammengehoerige Dateien (z. B. Zeichnung als PDF und DWG) sollen denselben Stand haben.
    for group, versions in groups.items():
        if len(versions) > 1:
            parts = "; ".join(" + ".join(names) for names in versions.values())
            warn(f"'{group}': die Dateien haben unterschiedliche Staende ({parts})")

    # Alles, was zu keinem Muster passt, erscheint unter "Further documents".
    extra_files = [p for p in candidates if p.name not in claimed]
    if extra_files:
        further = manifest.get("further", {})
        rendered = []
        for p in extra_files:
            ext = p.suffix.lstrip(".").lower() or "file"
            meta = [ext.upper()]
            if ext == "pdf" and (pages := pdf_pages(p)):
                meta.append(f"{pages} page" + ("" if pages == 1 else "s"))
            meta.append(fmt_size(p.stat().st_size))
            rendered.append(item_html(p.name, "", meta, publish_file(p), ext))
            warn(f"files/{p.name} steht in keinem Eintrag von documents.json - wird unter "
                 f"'{further.get('title', 'Further documents')}' ohne Beschreibung gezeigt")
        blocks.append(section_html(further.get("title", "Further documents"), further.get("note", ""), rendered))

    return "\n".join(blocks)


# --------------------------------------------------------------------------- Medien

def process_photo(src: Path, dst: Path) -> None:
    """Verkleinert nur, wenn noetig; entfernt dabei GPS-Daten und dreht nach EXIF."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        warn("Pillow fehlt, Fotos werden unveraendert uebernommen (pip install pillow)")
        shutil.copy2(src, dst)
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(src) as im:
            fmt = (im.format or "").upper()
            if fmt != "JPEG":
                shutil.copy2(src, dst)
                if src.stat().st_size > PHOTO_BIG_BYTES:
                    warn(f"{src.name}: {fmt or 'Bild'} mit {fmt_size(src.stat().st_size)}, bitte als JPEG ablegen")
                return
            exif = im.getexif()
            has_gps = bool(exif.get_ifd(0x8825))
            rotated = exif.get(0x0112, 1) not in (1, None)
            too_big = max(im.size) > PHOTO_MAX_PX or src.stat().st_size > PHOTO_BIG_BYTES
            if not (has_gps or rotated or too_big):
                shutil.copy2(src, dst)
                return
            icc = im.info.get("icc_profile")
            img = ImageOps.exif_transpose(im).convert("RGB")
            img.thumbnail((PHOTO_MAX_PX, PHOTO_MAX_PX), Image.LANCZOS)
            img.save(dst, "JPEG", quality=PHOTO_QUALITY, optimize=True, progressive=True,
                     **({"icc_profile": icc} if icc else {}))
    except Exception as e:
        fail(f"files/media/{src.name}: Bild nicht lesbar ({type(e).__name__}: {e})")
        return

    if not has_gps and not rotated and dst.stat().st_size >= src.stat().st_size:
        shutil.copy2(src, dst)  # Neu-Komprimierung hat nichts gebracht
        return
    why = "GPS-Daten entfernt" if has_gps else "verkleinert"
    say(f"  {src.name}: {why} ({fmt_size(src.stat().st_size)} -> {fmt_size(dst.stat().st_size)})")


def build_media(manifest: dict) -> tuple[str, str]:
    if not MEDIA.is_dir():
        return "", ""
    photos, videos = [], []
    for p in sorted((p for p in MEDIA.iterdir() if usable(p)), key=lambda p: natural_key(p.name)):
        ext = p.suffix.lower()
        if ext in PHOTO_EXT:
            photos.append(p)
        elif ext in VIDEO_EXT:
            videos.append(p)
        else:
            warn(f"files/media/{p.name}: Dateityp {ext or '(keiner)'} wird nicht eingebunden "
                 f"(erlaubt: jpg, png, webp, mp4, webm)")

    alt_tpl = manifest.get("media", {}).get("photo_alt", "Photo {n}")
    photo_items = []
    for i, p in enumerate(photos, 1):
        dst = OUT / "files" / "media" / p.name
        process_photo(p, dst)
        if not dst.exists():
            continue
        href = f"files/media/{quote(p.name)}?v={file_hash(dst)}"
        photo_items.append(
            f'      <li><a href="{href}" target="_blank" rel="noopener">'
            f'<img src="{href}" alt="{esc(alt_tpl.replace("{n}", str(i)))}" loading="lazy"></a></li>'
        )

    video_items = []
    for i, p in enumerate(videos, 1):
        size = p.stat().st_size
        if size > WARN_BYTES:
            warn(f"files/media/{p.name}: {fmt_size(size)} ist fuer Handys am Messestand sehr gross")
        href = publish_file(p)
        video_items.append(
            "      <li><figure>\n"
            f'        <div class="frame"><video controls preload="metadata" playsinline src="{href}"></video></div>\n'
            f"        <figcaption>Video {i} &middot; {fmt_size(size)}</figcaption>\n"
            "      </figure></li>"
        )

    say(f"  {len(photos)} Foto(s), {len(videos)} Video(s)")
    photo_html = '<ul class="grid">\n' + "\n".join(photo_items) + "\n    </ul>" if photo_items else ""
    video_html = '<ul class="videos">\n' + "\n".join(video_items) + "\n    </ul>" if video_items else ""
    return photo_html, video_html


# --------------------------------------------------------------------------- Bau

def build() -> int:
    for needed in (TEMPLATE, MANIFEST, FILES):
        if not needed.exists():
            fail(f"{needed.relative_to(ROOT)} fehlt")
    if errors:
        return 1
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"documents.json ist kein gueltiges JSON: {e} (meist ein fehlendes Komma oder Anfuehrungszeichen)")
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    for marker in ("DOCS", "PHOTOS", "VIDEOS", "UPDATED", "ID"):
        if f"<!--BUILD:{marker}-->" not in template:
            fail(f"index.template.html: Marke <!--BUILD:{marker}--> fehlt")
    if errors:
        return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    say("Dokumente:")
    docs = build_documents(manifest)
    say("Medien:")
    photos, videos = build_media(manifest)
    if errors:
        shutil.rmtree(OUT, ignore_errors=True)   # keinen halben Stand liegen lassen
        say(f"\n{len(errors)} Fehler - es wird nichts veroeffentlicht.")
        return 1

    if ASSETS.is_dir():
        shutil.copytree(ASSETS, OUT / "assets")

    digest = hashlib.sha1()
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            digest.update(f.relative_to(OUT).as_posix().encode())
            digest.update(f.read_bytes())
    build_id = digest.hexdigest()[:10]

    page = (template
            .replace("<!--BUILD:DOCS-->", docs)
            .replace("<!--BUILD:PHOTOS-->", photos)
            .replace("<!--BUILD:VIDEOS-->", videos)
            .replace("<!--BUILD:UPDATED-->", f"Last updated {today()}.")
            .replace("<!--BUILD:ID-->", f"<!-- build:{build_id} -->"))
    (OUT / "index.html").write_text(page, encoding="utf-8")

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    for f in OUT.rglob("*"):
        if f.is_file() and f.stat().st_size > HARD_LIMIT:
            fail(f"{f.relative_to(OUT)} ist groesser als 95 MB - GitHub nimmt das nicht an")
    if total > SITE_WARN:
        warn(f"Seite ist {fmt_size(total)} gross, die Grenze von GitHub Pages liegt bei 1 GB")
    if errors:
        return 1

    say(f"\nFertig: _site/ mit {sum(1 for f in OUT.rglob('*') if f.is_file())} Dateien, "
        f"{fmt_size(total)}, Stand-ID {build_id}.")
    if warnings:
        say(f"{len(warnings)} Hinweis(e) siehe oben.")
    return 0


# --------------------------------------------------------------------------- Pruefung der Live-Seite

def verify(base: str) -> int:
    """Wartet, bis die Live-Seite den frisch gebauten Stand zeigt, und prueft alle Links."""
    local = OUT / "index.html"
    if not local.exists():
        say("_site/index.html fehlt - erst bauen.")
        return 1
    page = local.read_text(encoding="utf-8")
    m = re.search(r"<!-- build:(\w+) -->", page)
    build_id = m.group(1) if m else None
    refs = sorted({html.unescape(r) for r in re.findall(r'(?:href|src)="((?:files|assets)/[^"]+)"', page)})
    base = base if base.endswith("/") else base + "/"
    ua = {"User-Agent": "Mozilla/5.0 (build-verify)"}

    def fetch(url: str, method: str = "GET"):
        req = urllib.request.Request(url, headers=ua, method=method)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, (r.read().decode("utf-8", "replace") if method == "GET" else "")

    problems: list[str] = []
    for attempt in range(1, 10):
        problems = []
        try:
            _, live = fetch(f"{base}?_={int(time.time())}")
            if build_id and f"build:{build_id}" not in live:
                problems.append(f"Live-Seite zeigt noch nicht den Stand {build_id}")
        except (urllib.error.URLError, TimeoutError) as e:
            problems.append(f"Startseite nicht abrufbar: {e}")
        if not problems:
            for ref in refs:
                try:
                    status, _ = fetch(urljoin(base, ref), "HEAD")
                    if status != 200:
                        problems.append(f"{ref}: HTTP {status}")
                except urllib.error.HTTPError as e:
                    problems.append(f"{ref}: HTTP {e.code}")
                except (urllib.error.URLError, TimeoutError) as e:
                    problems.append(f"{ref}: {e}")
        if not problems:
            say(f"Live-Seite ok: Stand {build_id}, {len(refs)} Links erreichbar.")
            return 0
        say(f"Versuch {attempt}: {len(problems)} Problem(e), erneut in 15 s ...")
        time.sleep(15)

    for p in problems:
        fail(p)
    return 1


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", metavar="URL", help="Live-Seite nach dem Veroeffentlichen pruefen")
    args = ap.parse_args()
    return verify(args.verify) if args.verify else build()


if __name__ == "__main__":
    sys.exit(main())

# LED.11IGN.A60 — Downloadseite

Temporäre Download-Seite für die Messe. Eine einzelne `index.html` ohne Build-Schritt,
ohne Framework, ohne externe Abhängigkeiten und ohne Tracking. Seitensprache: Englisch.

**Live-URL:** https://lethe-bremen.github.io/LED.11IGN.A60/

## Aufbau

```
index.html                   Die komplette Seite (HTML + CSS in einer Datei)
files/                       Alle Download-Dokumente (PDF, DWG, XLSM)
files/media/                 Fotos und Videos

assets/lethe-logo.jpg        Logo für die Kopfleiste
assets/hero-ship.jpg         Hintergrundbild der Begrüßung
assets/favicon.svg           Browser-Tab-Symbol
assets/apple-touch-icon.png  Icon für den iPhone-Home-Bildschirm
assets/qr-poster.png         QR-Poster im Handy-Hochformat
assets/email-banner.png      Banner für den Mailversand

tools/                       Skripte für Poster, Banner und Icon
EMAIL.md                     Vorlagen und Hinweise für den Mailversand
```

## Was noch ausgefüllt werden muss

In `index.html` sind die anzupassenden Stellen mit `PLACEHOLDER` kommentiert:

| Stelle | Was |
|---|---|
| Begrüßung | Überschrift und Begrüßungstext |

Suche in der Datei einfach nach `PLACEHOLDER`.

Das Impressum im Fußbereich ist mit den Angaben von lethe-bremen.de vollständig
befüllt (Geschäftsführung, HRB 33947, USt-ID, Kontakt, OS-Plattform).

## Hintergrundbild der Begrüßung

`assets/hero-ship.jpg` ist die auf 1400 px verkleinerte und als JPEG gespeicherte
`Schiff.png` (2055 KB → 194 KB). Darüber liegt ein Navy-Verlauf, damit der Text
lesbar bleibt — die Regeln stehen in `.hero` und `.hero::before`.

Anderes Motiv einsetzen: Datei nach `assets/hero-ship.jpg` legen, fertig. Ist das
neue Bild heller, den Verlauf in `.hero::before` kräftiger stellen — die drei
`rgba(...)`-Werte haben am Ende die Deckkraft (z. B. `.78` → `.88`).

## Neue Datei hinzufügen

### Variante A — direkt auf github.com (ohne Git)

1. Repository öffnen: https://github.com/lethe-bremen/LED.11IGN.A60
2. In den Ordner `files` wechseln
3. **Add file → Upload files**, Datei per Drag & Drop ablegen, **Commit changes**
4. Zurück im Repo-Root auf `index.html` klicken, Stift-Symbol (**Edit**)
5. Einen vorhandenen `<li class="item">…</li>`-Block kopieren und anpassen:
   Dateiname, Beschreibung, Größe und den `href` auf `files/DEINE-DATEI.pdf`
6. **Commit changes**

Nach ca. 1 Minute ist die Änderung live.

### Variante B — lokal mit Git

```bash
git pull
# Datei nach files/ kopieren, index.html anpassen
git add .
git commit -m "Neues Datenblatt ergänzt"
git push
```

### Vorlage für einen neuen Eintrag

```html
<li class="item">
  <span class="type">PDF</span>
  <div class="body">
    <div>
      <p class="name">DATEINAME.pdf</p>
      <p class="desc">Short description of the contents.</p>
      <p class="meta">PDF &middot; 12 pages &middot; 800 KB</p>
    </div>
    <a class="dl" href="files/DATEINAME.pdf" download>
      <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 1.5v9"/><path d="M4.5 7.5 8 11l3.5-3.5"/><path d="M2 13.5h12"/></svg>
      Download
    </a>
  </div>
</li>
```

Für die farbigen Typ-Kacheln: `<span class="type">` (blau, PDF),
`<span class="type dwg">` (magenta, CAD), `<span class="type xlsm">` (grün, Excel).

### Vorlage für ein neues Foto

Im Block `<ul class="grid">` ergänzen:

```html
<li><a href="files/media/DATEINAME.jpg" target="_blank" rel="noopener"><img src="files/media/DATEINAME.jpg" alt="Short image description" loading="lazy"></a></li>
```

### Vorlage für ein neues Video

Im Block `<ul class="videos">` ergänzen. Der `<div class="frame">` ist wichtig —
er begrenzt die Höhe, sonst füllt ein Hochformat-Clip den ganzen Handybildschirm:

```html
<li><figure>
  <div class="frame"><video controls preload="metadata" playsinline src="files/media/DATEINAME.mp4"></video></div>
  <figcaption>Video 4 &middot; 2,5 MB</figcaption>
</figure></li>
```

### Dateinamen

Keine Leerzeichen, keine Klammern und keine Umlaute — die stehen später in der URL.
Punkte und Bindestriche sind unproblematisch (`LED.STS.A60.UseMan.06.pdf` ist in Ordnung).

Grenzen von GitHub Pages: max. 100 MB pro Datei, ca. 1 GB pro Repository,
100 GB Traffic pro Monat. Für eine Messe reicht das mit großem Abstand.

## Seite wieder offline nehmen

### Nur Pages abschalten, Repo behalten

1. https://github.com/lethe-bremen/LED.11IGN.A60/settings/pages
2. Unter **Build and deployment → Source** auf **None** stellen

Oder per CLI:

```bash
gh api -X DELETE repos/lethe-bremen/LED.11IGN.A60/pages
```

Die URL liefert danach 404, die Dateien bleiben im Repo erhalten.

### Repo auf privat stellen (Pages wird dadurch inaktiv)

```bash
gh repo edit lethe-bremen/LED.11IGN.A60 --visibility private --accept-visibility-change-consequences
```

### Alles löschen

```bash
gh repo delete lethe-bremen/LED.11IGN.A60 --yes
```

Das ist endgültig. Vorher sicherstellen, dass die Originaldateien noch lokal liegen
(hier: `C:\Users\a.kruse\Desktop\CLAUDE.WORKFILE\Messedownload`).

## QR-Code

Fertiges Bild im Handy-Hochformat: **`assets/qr-poster.png`** (1080 × 1920).
Erzeugt von `tools/make-qr-poster.py`.

Der QR-Code zeigt auf https://lethe-bremen.github.io/LED.11IGN.A60/ — die URL ändert sich nicht,
solange Organisation und Repo-Name gleich bleiben. Inhalte lassen sich also beliebig nachpflegen,
ohne einen gedruckten QR-Code zu entwerten. **Wird das Repo umbenannt oder verschoben, ist die
alte Adresse sofort tot** (GitHub leitet bei Pages nicht weiter) und alle gedruckten Codes
müssen ersetzt werden. Dagegen hilft nur eine eigene Subdomain, siehe [EMAIL.md](EMAIL.md).

Neu erzeugen (z. B. nach Textänderung oder für eine andere Messe):

```bash
pip install qrcode pillow
python tools/make-qr-poster.py
```

Fehlerkorrektur steht auf Stufe Q (25 %), die Ruhezone auf die genormten 4 Module.
Die Modulgröße wird auf einen ganzzahligen Pixelwert gerundet — ein nachträgliches
Skalieren des fertigen Bildes würde ungleich breite Module erzeugen und den Code
bei schlechtem Licht unzuverlässig machen. Aus demselben Grund liegt der Code auf
weißer Fläche und nicht auf dem Schiffsbild.

Für großformatigen Druck (Aufsteller, Roll-up) in `tools/make-qr-poster.py` oben
`W, H` hochsetzen — die Maße sind relativ dazu nicht automatisch, die Y-Werte im
Skript müssten dann mitwachsen. Sag Bescheid, wenn du eine Druckvariante brauchst.

## Banner für den Mailversand

`assets/email-banner.png` (1200 × 560, Anzeige mit `width="600"`), erzeugt von
`tools/make-email-banner.py`. Fertige Textbausteine, HTML-Schnipsel und die
Fallstricke beim Mailversand stehen in **[EMAIL.md](EMAIL.md)**.

```bash
python tools/make-email-banner.py
```

Wichtig bei beiden Skripten: Ändert sich die Adresse der Seite, muss oben die
Konstante `URL` angepasst und die Grafik neu erzeugt werden — sonst zeigt der
QR-Code weiter auf die alte Adresse.

## Icon für den iPhone-Home-Bildschirm

Im Safari über das Teilen-Menü → **Zum Home-Bildschirm** lässt sich die Seite wie eine
App ablegen. Das Icon ist `assets/apple-touch-icon.png` (180 × 180, Nachtblau-Verlauf mit
Schiff und magentafarbener Linie), der Name darunter steht in `index.html`
(`apple-mobile-web-app-title`, aktuell „Lethe A-60").

Bewusst **ohne** Manifest, Vollbildmodus und Service Worker: Im Vollbildmodus öffnen sich
PDFs ohne Zurück-Knopf, und zwischengespeicherte Dokumente wären nach einem Tausch
veraltet. So bleibt es eine normale Seite in Safari.

Neu erzeugen:

```bash
pip install pillow numpy
python tools/make-app-icon.py
```

Die Silhouette kommt aus `tools/ship-icon-source.png`. Mit `--report-set ORDNER` entsteht
zusätzlich dieselbe Grafik auf dem dunklen Grund der Berichts-App (180, 192, 512 und
512 maskable). Ein bereits angelegtes Icon aktualisiert sich nicht von selbst — zum
Testen auf dem iPhone erst löschen, dann neu anlegen.

## Hinweis zur Sichtbarkeit

Das Repository ist öffentlich: alle Dateien sind ohne Login abrufbar. Die Seite trägt
`noindex, nofollow`, was seriöse Suchmaschinen von der Indexierung abhält — ein
Zugriffsschutz ist das jedoch nicht.

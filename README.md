# LED.11IGN.A60 — Downloadseite

Temporäre Download-Seite für die Messe. Statisches HTML ohne Framework, ohne externe
Abhängigkeiten und ohne Tracking, Seitensprache Englisch. Die Seite wird bei jedem Upload
automatisch aus den Ordnern gebaut (siehe [Dokumente und Medien tauschen](#dokumente-und-medien-tauschen)).

**Live-URL:** https://lethe-bremen.github.io/LED.11IGN.A60/

## Aufbau

```
index.template.html          Rahmen der Seite (Kopf, Begrüßung, Impressum, Stil)
documents.json               Verzeichnis der Dokumente (Titel, Beschreibung, Dateimuster)
files/                       Alle Download-Dokumente (PDF, DWG, XLSM)
files/media/                 Fotos und Videos, alles dort erscheint in der Galerie

assets/lethe-logo.jpg        Logo für die Kopfleiste
assets/hero-ship.jpg         Hintergrundbild der Begrüßung
assets/favicon.svg           Browser-Tab-Symbol
assets/apple-touch-icon.png  Icon für den iPhone-Home-Bildschirm
assets/qr-poster.png         QR-Poster im Handy-Hochformat
assets/email-banner.png      Banner für den Mailversand

.github/workflows/pages.yml  Baut und veröffentlicht die Seite bei jedem Upload
tools/build.py               Der Bau: Ordner -> fertige Seite (_site/, nicht im Repo)
tools/make-*.py              Skripte für Poster, Banner und Icon
requirements.txt             Python-Pakete für den Bau (pillow, pypdf)
EMAIL.md                     Vorlagen und Hinweise für den Mailversand
```

## Was noch ausgefüllt werden muss

In `index.template.html` sind die anzupassenden Stellen mit `PLACEHOLDER` kommentiert:

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

## Dokumente und Medien tauschen

Die Seite baut sich selbst. Nach jedem Upload auf GitHub läuft automatisch
`tools/build.py`: Es liest `files/`, `files/media/` und `documents.json`, erzeugt die
Seite, prüft sie, veröffentlicht sie und kontrolliert danach, ob die Live-Seite den neuen
Stand zeigt und alle Links funktionieren. HTML muss dafür nicht angefasst werden.

### Neue Version eines Dokuments

1. https://github.com/lethe-bremen/LED.11IGN.A60/upload/main/files öffnen
2. Datei per Drag & Drop ablegen, mit der **nächsthöheren Versionsnummer** im Namen,
   z. B. `LED.11IGN.A60.CuDrwg.V2.pdf`
3. **Commit changes**

Nach etwa 2 Minuten zeigt die Seite die neue Datei samt Größe und Seitenzahl. Die alte
Version (`…V1.pdf`) wird nicht mehr verlinkt und nicht mehr veröffentlicht. Sie darf im
Ordner liegen bleiben; zum Aufräumen die Datei auf github.com öffnen → Papierkorb-Symbol.

- **PDF und DWG gehören zusammen:** beide hochladen. Liegt nur von einer Datei eine neue
  Version vor, gibt der Bau einen Hinweis (gelbe Meldung im Actions-Log).
- **Gleicher Dateiname:** Eine Datei mit exakt demselben Namen ersetzt die alte. Jeder Link
  trägt einen Stempel (`?v=…`), damit Handys nicht die alte Fassung aus dem
  Zwischenspeicher zeigen.

### Neues Dokument, das es noch nicht gibt

1. Datei wie oben in `files` hochladen
2. `documents.json` öffnen → Stift-Symbol → einen vorhandenen Block kopieren und anpassen:

   ```json
   {
     "pattern": "LED.11IGN.A60.DataSheet.{v}.pdf",
     "desc": "Short description of the contents."
   }
   ```
3. **Commit changes**

Ohne Schritt 2 erscheint die Datei trotzdem, dann unter „Further documents“ und ohne
Beschreibung.

| Feld | Bedeutung |
|---|---|
| `pattern` | Dateiname. `{v}` steht für die Versionsnummer (`V2`, `03`, `1.2` …); gibt es mehrere Dateien, gewinnt die höchste. Ohne `{v}` ist es ein fester Name. |
| `desc` | Beschreibung (englisch, steht auf der Seite). Darin sind `{v}` (wie im Dateinamen), `{V}` (mit vorangestelltem V) und `{n}` (reine Zahl ohne führende Nullen) möglich. |
| `name` | Optional. Angezeigter Titel, sonst der Dateiname. Auch hier `{v}`, `{V}`, `{n}`. |
| `extra` | Optional. Zusatz in der grauen Zeile, z. B. `valid until 12 Apr 2031`. |
| `group` | Optional. Einträge mit gleichem Gruppennamen sollen denselben Stand haben, sonst gibt es einen Hinweis. |

In JSON steht zwischen den Einträgen ein Komma, nach dem letzten nicht. Schlägt der Bau
daran fehl, nennt das Actions-Log die Zeile.

Überschriften und Abschnittstexte („Approvals“, „Technical documents“ …) stehen ebenfalls
in `documents.json`.

### Fotos und Videos

Ablegen in `files/media`: https://github.com/lethe-bremen/LED.11IGN.A60/upload/main/files/media

Alles dort erscheint automatisch, sortiert nach Dateiname (Fotos: jpg, png, webp; Videos:
mp4, webm). Löschen auf github.com nimmt es wieder von der Seite. Zum Bestimmen der
Reihenfolge Nummern im Namen verwenden (`…-Foto-07.jpg`).

- **Fotos** werden vom Bau aufbereitet, wenn nötig: länger als 2000 px oder größer als
  700 KB wird verkleinert, die Handy-Drehung korrigiert und **GPS-Daten werden entfernt**.
  Fotos direkt vom Handy können also unbearbeitet hochgeladen werden.
- **Videos** werden nicht umgerechnet. Ab 25 MB gibt es einen Hinweis, denn am Messestand
  lädt das über Mobilfunk sehr langsam. Ein Video bitte vorher auf Handygröße bringen.
- Der Upload im Browser nimmt höchstens 25 MB pro Datei an. Größeres geht nur per Git.

### Kontrolle

Im Repo auf den Reiter **Actions**: Ein grüner Haken heißt, die Seite ist veröffentlicht
und die Live-Seite wurde geprüft. Bei einem roten Kreuz ist **nichts verändert worden**,
die bisherige Seite bleibt online, und das Log nennt den Grund. Je nach Benachrichtigungs-
einstellungen des Kontos schickt GitHub dazu auch eine E-Mail.

Startet nach einem Upload nichts (kein neuer Eintrag unter Actions), lässt sich der Bau von
Hand anstoßen: **Actions → Seite bauen und veroeffentlichen → Run workflow**.

| Situation | Folge |
|---|---|
| Für einen Eintrag in `documents.json` gibt es keine Datei | Abbruch, alte Seite bleibt |
| `documents.json` ist kaputt (Komma, Anführungszeichen) | Abbruch |
| Bild nicht lesbar, Datei über 95 MB | Abbruch |
| Datei in `files/` steht in keinem Eintrag | Hinweis, erscheint unter „Further documents“ |
| PDF und DWG haben unterschiedliche Stände | Hinweis |
| Video über 25 MB, unbekannter Typ in `files/media` | Hinweis |

Wartezeit beachten: GitHub liefert Seiten bis zu 10 Minuten aus dem Zwischenspeicher. Nach
einem Tausch sehen Handys den neuen Stand daher nach spätestens etwa 12 Minuten. Ein
Tausch kurz vor einer Präsentation ist riskant.

### Lokal mit Git

```bash
git pull
# Dateien nach files/ kopieren, bei Bedarf documents.json anpassen
pip install -r requirements.txt
python tools/build.py                  # baut die Vorschau nach _site/
python -m http.server -d _site 8000    # ansehen unter http://localhost:8000
git add -A
git commit -m "Zeichnung auf V2"
git push
```

### Rahmen der Seite ändern

Begrüßung, Impressum und Gestaltung stehen in `index.template.html`. Die Marken
`<!--BUILD:…-->` darin nicht löschen: dort setzt der Bau Dokumente, Fotos, Videos, das
Datum „Last updated“ und die Stand-ID ein.

### Dateinamen

Keine Leerzeichen, keine Klammern und keine Umlaute, die stehen später in der URL.
Punkte und Bindestriche sind unproblematisch (`LED.STS.A60.UseMan.06.pdf` ist in Ordnung).

Grenzen von GitHub Pages: max. 100 MB pro Datei, ca. 1 GB pro Repository,
100 GB Traffic pro Monat. Für eine Messe reicht das mit großem Abstand.

### Veröffentlicht ist veröffentlicht

Das Repo ist öffentlich und Git vergisst nichts. Eine ersetzte oder gelöschte Datei ist
von der Seite weg, bleibt aber im Verlauf des Repos abrufbar. Das gilt auch für die
frühere Zeichnung V0. Für überholte Versionen ist das unkritisch. Muss etwas wirklich
zurückgezogen werden (falsches oder vertrauliches Dokument), reicht Löschen nicht: dann
muss der Verlauf bereinigt werden. Das nicht selbst versuchen, sondern melden.

## Seite wieder offline nehmen

### Nur Pages abschalten, Repo behalten

In den Pages-Einstellungen (https://github.com/lethe-bremen/LED.11IGN.A60/settings/pages)
die Veröffentlichung zurückziehen. Oder per CLI:

```bash
gh api -X DELETE repos/lethe-bremen/LED.11IGN.A60/pages
```

Die URL liefert danach 404, die Dateien bleiben im Repo erhalten.

Wieder veröffentlichen:

```bash
gh api -X POST repos/lethe-bremen/LED.11IGN.A60/pages -f build_type=workflow
```

Danach unter **Actions → Seite bauen und veroeffentlichen → Run workflow** starten.

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
Schiff und magentafarbener Linie), der Name darunter steht in `index.template.html`
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

# Versand per Mail

## Die eine Regel

**Der Link muss immer als Text in der Mail stehen.** Outlook und Gmail blockieren
externe Bilder standardmäßig — der Empfänger sieht dann statt des Banners einen
grauen Kasten. Wer das Banner als einzigen Träger des Links benutzt, verschickt bei
einem großen Teil der Empfänger eine Mail ohne erkennbaren Link.

Das Banner ist die Zugabe, nicht der Träger.

## Banner

`assets/email-banner.png` — 1200 × 560 px, eingebunden mit `width="600"`.
Die doppelte Auflösung sorgt dafür, dass es auf Retina- und 4K-Displays scharf bleibt.

Erzeugt von `tools/make-email-banner.py`, siehe README.

Enthält Logo, Typbezeichnung, Kurzinhalt, die URL im Klartext und den QR-Code.
Der QR ist bei 600 px Anzeigebreite etwa 143 px groß — vom Monitor aus scannbar,
aber nicht aus der Entfernung. Wer einen QR zum Ausdrucken oder Aufstellen braucht,
nimmt `assets/qr-poster.png`.

### Zwei Wege, das Banner einzubinden

**A — Inline einbetten (empfohlen).** In Outlook *Einfügen → Bilder → Dieses Gerät*
und `email-banner.png` auswählen. Das Bild reist als Anhang mit und wird nicht
blockiert. Danach das Bild markieren und über *Link einfügen* auf die Seite legen.
Nachteil: jede Mail wird ~300 KB größer.

**B — Vom Server laden.** Kleinere Mail, aber Blockierung durch den Mailclient.
Dafür der HTML-Baustein unten.

## HTML-Baustein

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"
       style="width:600px;max-width:100%;border-collapse:collapse;">
  <tr>
    <td style="padding:0 0 18px 0;">
      <a href="https://lethe-bremen.github.io/LED.11IGN.A60/" style="display:block;text-decoration:none;">
        <img src="https://lethe-bremen.github.io/LED.11IGN.A60/assets/email-banner.png"
             width="600"
             alt="LED.11IGN.A60 – A-60 Sliding Door System: Zulassungen, Zeichnungen und Handbuch zum Download"
             style="display:block;width:100%;max-width:600px;height:auto;border:0;outline:none;text-decoration:none;">
      </a>
    </td>
  </tr>
  <tr>
    <td style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#1a1d21;">
      Direktlink:
      <a href="https://lethe-bremen.github.io/LED.11IGN.A60/"
         style="color:#143868;font-weight:bold;">lethe-bremen.github.io/LED.11IGN.A60</a>
    </td>
  </tr>
</table>
```

Der `alt`-Text ist kein Beiwerk: Er ist genau das, was der Empfänger bei blockierten
Bildern liest. Deshalb steht dort der Inhalt und nicht „Banner".

## Mailtext

**Betreff:** `LED.11IGN.A60 – Unterlagen zum A-60 Schiebetürsystem`

```
Sehr geehrte Damen und Herren,

wie besprochen finden Sie unter folgendem Link alle Unterlagen zu unserem
einflügeligen A-60 Brandschutz-Schiebetürsystem LED.11IGN.A60:

https://lethe-bremen.github.io/LED.11IGN.A60/

Enthalten sind die EG-Baumusterprüfbescheinigungen nach MED 2014/90/EU,
die Brandtestzeichnung als PDF und DWG, die Auslegungsmatrix, der
Anschlussplan sowie das Bedienhandbuch — dazu Fotos und Videos des
Prüfaufbaus.

Für Rückfragen stehe ich gerne zur Verfügung.

Mit freundlichen Grüßen
```

**Subject:** `LED.11IGN.A60 – documents for the A-60 sliding door system`

```
Dear Sir or Madam,

as discussed, please find all documents for our single-leaf A-60 sliding
fire door system LED.11IGN.A60 at the following link:

https://lethe-bremen.github.io/LED.11IGN.A60/

It contains the EC type-examination certificates under MED 2014/90/EU, the
fire test drawing as PDF and DWG, the configuration matrix, the wiring plan
and the user manual, along with photos and videos of the test assembly.

Please do not hesitate to contact me with any questions.

Kind regards
```

## Was ich nicht empfehlen würde

**Keinen URL-Kürzer** (bit.ly und Verwandte). Die Adresse ist kurz genug, gekürzte
Links landen häufiger im Spam-Ordner, und wenn der Dienst abgeschaltet wird, ist
der Link tot — auch der bereits gedruckte QR-Code.

**Keinen Massenversand über den normalen Mailclient.** Bei mehr als einer Handvoll
Empfänger gehört jede Adresse ins BCC, sonst gibt man Kundenadressen quer preis.

## Optional: eigene Subdomain

Die Adresse `lethe-bremen.github.io/LED.11IGN.A60` ist so, wie sie ist, in Ordnung —
der Firmenname steht drin, und sie wirkt in einer Geschäftsmail nicht mehr nach
Privatperson.

Ein Argument für `downloads.lethe-bremen.de` bleibt trotzdem: **Die Adresse hängt dann
nicht mehr am GitHub-Konto und am Repo-Namen.** Beim Umzug vom privaten auf den
Firmen-Account ist die alte Adresse ungültig geworden, und jeder bis dahin gedruckte
oder verschickte QR-Code lief ins Leere. Mit eigener Subdomain hätte sich nur der
DNS-Eintrag geändert, alle Codes wären weiter gegangen.

Das lohnt sich vor allem, wenn die Seite länger als eine Messe leben soll. Drei Schritte:

1. Beim DNS-Verwalter von lethe-bremen.de (laut Impressum Gemini ArtWork Media)
   einen CNAME-Eintrag anlegen: `downloads` → `lethe-bremen.github.io`
2. Im Repo unter *Settings → Pages → Custom domain* `downloads.lethe-bremen.de`
   eintragen und *Enforce HTTPS* aktivieren
3. `URL` in beiden Skripten unter `tools/` anpassen und Poster und Banner neu
   erzeugen — der QR-Code zeigt sonst weiter auf die alte Adresse

Wichtig dabei: Danach **nichts mehr drucken, bevor der DNS-Eintrag steht und HTTPS
aktiv ist.** Und: Sobald die Subdomain läuft, die Adresse auch nicht mehr ändern.

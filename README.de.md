# HA MoviesDB – Home Assistant Custom Integration

<p align="center">
  <img src="docs/logo.png" alt="HA MoviesDB Logo" width="360">
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="hacs_badge"></a>
  <a href="https://github.com/charly166/ha-moviesdb/releases"><img src="https://img.shields.io/github/v/release/charly166/ha-moviesdb" alt="GitHub Release"></a>
  <a href="https://github.com/charly166/ha-moviesdb/blob/main/LICENSE"><img src="https://img.shields.io/github/license/charly166/ha-moviesdb" alt="License"></a>
</p>

[English version](README.md)

---

Eine Home-Assistant-Custom-Integration mit eigener Lovelace-Karte (GUI) zum
Verwalten von Filmen: Filme über die kostenlose **themoviedb.org (TMDB)
API** suchen, auf die Watchlist setzen, und nach dem Ansehen ins Archiv
verschieben. Für jeden Film auf der Watchlist zeigt die Karte an, auf
welchem Streamingdienst er aktuell verfügbar ist (Abo, Leihen, Kaufen oder
kostenlos mit Werbung) – auf Basis der von JustWatch stammenden
Watch-Provider-Daten von TMDB.

Dieses Projekt ist ein Schwesterprojekt von
[HA SeriesDB](https://github.com/charly166/ha-seriesdb) mit derselben
Architektur, aber für Filme statt Serien.

## Features

- Suche auf themoviedb.org und Hinzufügen von Filmen zur Watchlist
- Tabs "Watchlist" und "Archiv" mit Poster-Raster
- Film-Detailansicht: Titel, Erscheinungsjahr, Laufzeit, Beschreibung
- **Als gesehen markieren** – verschiebt den Film ins "Archiv"; jederzeit
  rückgängig zu machen
- **Wo ist der Film verfügbar**: zeigt, auf welchen Streaminganbietern der
  Film aktuell verfügbar ist (Abo/Streaming, Leihen, Kaufen, kostenlos mit
  Werbung), gruppiert nach Typ, mit Hervorhebung der eigenen konfigurierten
  Anbieter
- **Konfigurierbare Region und eigene Streaminganbieter**: das eigene Land
  (Streaming-Verfügbarkeit ist länderspezifisch) sowie die tatsächlich
  abonnierten Dienste unter Einstellungen → Geräte & Dienste → HA MoviesDB
  → Konfigurieren auswählen
- Kartenbreite **und -höhe** sind in modernen "Sections"-Dashboards per
  Ziehen anpassbar und füllen die zugewiesene Rasterzelle exakt aus
- Eigenes Icon/Logo unter Einstellungen → Geräte & Dienste (Home Assistant
  2026.3+)
- Eine Sensor-Entität pro verfolgtem Film (Status + `available_on`-Liste der
  eigenen Anbieter, die den Film gerade im Abo haben) für Automationen, z.B.
  "benachrichtige mich, wenn ein Film auf Netflix verfügbar wird"
- Services für Automationen: `add_movie`, `remove_movie`, `set_watched`,
  `set_archived`, `refresh`, `refresh_watch_providers`
- Alle Daten (Watchlist, Sehstatus, Archiv) werden lokal in Home Assistant
  gespeichert (`.storage/ha_moviesdb_data`) – kein Cloud-Konto nötig außer
  dem kostenlosen TMDB-API-Key

**Bewusst nicht enthalten:** klassische TV-Sender-Programmzeiten (z.B. "läuft
Samstag 20:15 Uhr auf einem Sender"). Dafür gibt es keine saubere, kostenlose
API – diese Integration deckt daher ausschließlich On-Demand-Streaming ab.

## Rechtliches: TMDB- & JustWatch-Attribution, Lizenz

Diese Integration nutzt die kostenlose TMDB-API. Deren Nutzungsbedingungen
verlangen einen sichtbaren Attributionshinweis mit Logo. Die Karte zeigt den
Pflichttext bereits automatisch als kleine Fußzeile an – **du musst nur
einmalig die eigentliche TMDB-Logodatei ergänzen**, da TMDB eine automatische
Weiterverteilung des Logos nicht gestattet:

1. Lade eines der freigegebenen Logos von
   https://www.themoviedb.org/about/logos-attribution herunter (SVG oder
   PNG, z.B. die kurze quadratische Variante).
2. Speichere es unverändert (Farbe/Seitenverhältnis nicht anpassen) als
   `tmdb-logo.svg` (oder `.png`, dann einmalig den Dateinamen in
   `custom_components/ha_moviesdb/www/ha-moviesdb-card.js`, Methode
   `_renderTmdbAttribution()`, anpassen) hier ab:
   ```
   custom_components/ha_moviesdb/www/tmdb-logo.svg
   ```
3. Fertig – solange die Datei fehlt, blendet die Karte einfach den
   Logo-Platzhalter aus und zeigt weiterhin den Pflichttext.

Die Watch-Provider-Daten (Streaming-Verfügbarkeit) stammen von **JustWatch**
und werden über die `/watch/providers`-API von TMDB bereitgestellt – dafür
gilt eine eigene, separate Attributionspflicht (ein sichtbarer Link zurück
zu TMDB/JustWatch, bereits in der "Verfügbar auf"-Sektion der
Film-Detailansicht enthalten). Das ist keine Rechtsberatung – bitte prüfe
den aktuellen Wortlaut selbst unter
https://developer.themoviedb.org/docs/watch-providers-attribution-requirement
und https://www.themoviedb.org/api-terms-of-use, bevor du veröffentlichst.

Der Code selbst steht unter der [MIT-Lizenz](LICENSE) und darf frei
weiterverteilt, verändert und veröffentlicht werden. Das im Kartenkopf
gezeigte "HA MoviesDB"-Logo ist eigenständiges Artwork des Projektautors.

## Installation

### Über HACS (empfohlen)

1. In Home Assistant **HACS** öffnen
2. Drei-Punkte-Menü (oben rechts) → **Benutzerdefinierte Repositories**
3. `https://github.com/charly166/ha-moviesdb` als Repository-Typ
   **Integration** hinzufügen
4. In HACS nach **"HA MoviesDB"** suchen und herunterladen
5. Home Assistant neu starten

### Manuell

1. Den Ordner `custom_components/ha_moviesdb` in das
   `custom_components`-Verzeichnis der Home-Assistant-Konfiguration
   kopieren, z.B. per Samba/SSH nach:
   ```
   <config>/custom_components/ha_moviesdb/
   ```
2. Home Assistant neu starten

## 1. Kostenlosen TMDB-API-Key besorgen

1. Falls noch nicht vorhanden, ein kostenloses Konto unter
   https://www.themoviedb.org anlegen.
2. Unter **Profil → Einstellungen → API** (oder direkt
   https://www.themoviedb.org/settings/api) einen API-Key beantragen. TMDB
   fragt nach dem Verwendungszweck – "Developer"/private Nutzung reicht aus.
3. Den angezeigten **"API Key (v3 auth)"** kopieren (nicht das "API Read
   Access Token" – das wird von dieser Integration nicht genutzt).

Der kostenlose TMDB-Tarif erlaubt großzügige Rate-Limits für den privaten
Gebrauch (ca. 40 Anfragen pro 10 Sekunden), was für diese Integration mehr
als ausreicht.

## 2. Integration einrichten

**Einstellungen → Geräte & Dienste → Integration hinzufügen** → nach "HA
MoviesDB" suchen → API-Key eingeben.

## 3. Region und Streaminganbieter konfigurieren

Unter **Einstellungen → Geräte & Dienste → HA MoviesDB → Konfigurieren**
lässt sich einstellen:

- **Region**: das Land, für das die Streaming-Verfügbarkeit abgefragt wird
  (Standard: Deutschland). Streaming-Kataloge unterscheiden sich je Land –
  wähle die Region, aus der du tatsächlich schaust.
- **Meine Streaminganbieter**: welche Dienste du tatsächlich abonniert hast
  (Netflix, Disney+, Prime Video, …), ausgewählt aus der aktuellen,
  live von TMDB geladenen Anbieterliste für deine gewählte Region. Diese
  werden in der Film-Detailansicht hervorgehoben und speisen das
  `available_on`-Sensorattribut.

Ein Regionswechsel wirkt sich vollständig erst beim nächsten Öffnen dieses
Dialogs aus (die während des aktuellen Formulars angezeigte Anbieterliste
entspricht noch der Region, die beim Öffnen aktiv war).

## 4. Die Karte registriert sich automatisch

Die Karte registriert sich beim Einrichten selbst als Lovelace-Dashboard-
Ressource – genauso, wie es der manuelle Weg über "Einstellungen →
Dashboards → Ressourcen" auch tun würde, indem sie in dieselbe
Storage-Collection schreibt. Im Standard-Speichermodus ist dafür kein
manueller Schritt nötig. Nach der Installation einmal Home Assistant neu
starten und danach den Browser neu laden.

**Nur falls dein Dashboard den alten YAML-Modus** nutzt (nicht der
Standard), erlaubt Home Assistant Integrationen grundsätzlich nicht, die
Ressourcenliste zu schreiben. In diesem Fall folgendes manuell in die
`ui-lovelace.yaml` eintragen:
```yaml
resources:
  - url: /ha_moviesdb/ha-moviesdb-card.js?v=1
    type: module
```
In diesem Fall musst du die `?v=...`-Nummer nach jedem zukünftigen Update
selbst hochzählen – im Storage-Modus passiert das automatisch. Die aktuelle
Versionsnummer steht immer im Start-Log (**Einstellungen → System → Logs**,
Suche nach "HA MoviesDB").

## 5. Karte zum Dashboard hinzufügen

1. Dashboard bearbeiten → **Karte hinzufügen** → ganz nach unten scrollen →
   **Manuell**
2. Einfügen:
   ```yaml
   type: custom:ha-moviesdb-card
   ```
3. Speichern. Die Karte zeigt drei Tabs: "Watchlist", "Archiv" und "Film
   hinzufügen" (Suche).

Nutzt deine Dashboard-Ansicht das **"Sections"**-Layout (Standard für neue
Dashboards seit Home Assistant 2024.5), lassen sich Breite und Höhe der
Karte per Ziehen am Rand im Dashboard-Editor anpassen. Ältere
"Masonry"-Ansichten unterstützen keine Karten-individuelle Größe (eine
Einschränkung dieses Ansichtstyps, nicht der Karte).

## 6. Nutzung

- **Film hinzufügen**: Tab "Film hinzufügen" → Titel eintippen (die Suche
  startet automatisch ab 2 Zeichen) → beim gewünschten Treffer "Hinzufügen"
  klicken.
- **Film öffnen**: Poster in "Watchlist" oder "Archiv" anklicken – die
  Detailansicht zeigt Beschreibung, Laufzeit und aktuelle
  Streaming-Verfügbarkeit (eigene konfigurierte Anbieter werden golden
  umrandet hervorgehoben).
- **Als gesehen markieren**: in der Detailansicht – verschiebt den Film
  zugleich ins "Archiv". Erneutes Klicken macht nur den Sehstatus rückgängig
  (nicht den Archivstatus – dafür den separaten Archiv-Button nutzen).
- **Unabhängig archivieren**: "Ins Archiv verschieben" / "Aus Archiv
  zurückholen" archiviert bzw. entarchiviert einen Film, ohne den Sehstatus
  zu ändern (z.B. für Filme, die man sich doch nicht ansehen möchte).
- **Film entfernen**: in der Detailansicht.

## Automationsbeispiel

```yaml
automation:
  - alias: "Film jetzt verfügbar"
    trigger:
      - platform: state
        entity_id: sensor.the_matrix # entity_id hängt vom Film ab
        attribute: available_on
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.attributes.available_on | length > 0 }}"
    action:
      - service: notify.mobile_app_dein_handy
        data:
          message: >
            {{ trigger.to_state.name }} ist jetzt verfügbar auf
            {{ trigger.to_state.attributes.available_on | join(', ') }}.
```

## Technische Hinweise

- Reine Python-Standardbibliothek + `aiohttp` (bereits Teil von Home
  Assistant) – es werden keine zusätzlichen Pip-Pakete installiert.
- Die Lovelace-Karte ist ein reines Vanilla-Web-Component ohne Build-Schritt
  und lädt **keine externen Web-Fonts** (bewusste Entscheidung: Google Fonts
  bei jedem Kartenaufruf würde die IP-Adresse des Besuchers an Google
  übertragen, was Gerichte wie das LG München I (Urt. v. 20.01.2022, Az. 3 O
  17493/20) ohne Einwilligung als DSGVO-Verstoß werten). Stattdessen kommen
  System-Fonts zum Einsatz.
- Die Authentifizierung nutzt den einfachen TMDB-"API Key (v3 auth)" als
  Query-Parameter bei jeder Anfrage – kein separater Login/Token-Refresh
  nötig.
- Anders als die Episodenliste einer Serie ändern sich Filmmetadaten (Titel,
  Poster, Beschreibung, Laufzeit) nach dem Erscheinen praktisch nie und
  werden daher nur einmal beim Hinzufügen geholt. Was sich über die Zeit
  ändert, ist die Streaming-Verfügbarkeit – nur diese wird periodisch
  aufgefrischt (alle 12 Stunden für Filme auf der Watchlist, archivierte
  Filme werden übersprungen) und lässt sich zusätzlich gezielt beim Öffnen
  der Detailansicht aktualisieren.
- Texte/Beschreibungen sind standardmäßig **Deutsch** (`language=de-DE`),
  passend zum Ursprung dieses Projekts. Die Konstante `TMDB_LANGUAGE` in
  `const.py` kann bei Bedarf angepasst werden (z.B. auf `en-US`).
- `iot_class: cloud_polling` – die Integration fragt themoviedb.org aktiv
  ab, standardmäßig alle 12 Stunden für Filme auf der Watchlist, sowie bei
  jeder manuellen Such-/Hinzufüge-/Aktualisieren-Aktion.
- Eigenes Icon unter "Geräte & Dienste": seit Home Assistant 2026.3 können
  Custom-Integrationen ihr eigenes Icon lokal mitliefern (`brand/`-Ordner mit
  `icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png`) – kein Pull Request
  im separaten `home-assistant/brands`-Repository nötig. Auf älteren
  Home-Assistant-Versionen wird stattdessen ein generisches Platzhalter-Icon
  angezeigt.

## Ordnerstruktur

```
ha-moviesdb/
├── LICENSE                MIT-Lizenz
├── README.md / README.de.md
├── hacs.json               HACS-Metadaten
├── .github/workflows/      HACS- + Hassfest-Validierung
├── docs/logo.png           Vollständiges Logo für README/Repo
└── custom_components/ha_moviesdb/
    ├── __init__.py          Setup, Services, statische Dateiauslieferung
    ├── api.py                Schlanker themoviedb.org (TMDB) v3 Client
    ├── brand/                 Lokale Icons für "Geräte & Dienste" (HA 2026.3+)
    │   ├── icon.png / icon@2x.png
    │   └── logo.png / logo@2x.png
    ├── config_flow.py        Einrichtungsdialog (API-Key) + Options-Flow (Region/Anbieter)
    ├── const.py
    ├── coordinator.py        Periodische Watch-Provider-Aktualisierung
    ├── frontend.py            Automatische Lovelace-Ressourcen-Registrierung
    ├── manifest.json
    ├── sensor.py              Eine Sensor-Entität pro verfolgtem Film
    ├── services.yaml
    ├── store.py               Persistente Watchlist + Sehstatus + Archiv
    ├── strings.json / translations/
    ├── websocket_api.py       WebSocket-Befehle für die Karte
    └── www/
        ├── ha-moviesdb-card.js    Lovelace-Karte (GUI)
        ├── ha-moviesdb-icon.png   App-Icon für den Kartenkopf
        └── tmdb-logo.svg          ⚠️ musst du selbst ergänzen, siehe oben
```

## Mindestanforderungen

- Home Assistant **2024.12.0** oder neuer (der Options-Flow nutzt die
  `config_entry`-Property, die Home Assistant Config-Flows seit dieser
  Version selbst bereitstellt)

## Lizenz

MIT – siehe [LICENSE](LICENSE) für Details.

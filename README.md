# PULSE E8 – E-Drum-Konfigurator

Online-Produktkonfigurator für ein selbst entworfenes E-Drum-Set – Schulprojekt mit **Blender**, **three.js** und **Threlte** (Svelte 5).

Das Set „E8“: runde Mesh-Pads mit Spannschrauben, Rohr-Rack mit Querstange und zwei Seitenflügeln, Gummi-Becken mit Noppen, Kick-Säule, Alu-Pedale und ein Modul mit Handyhalter.

## Funktionen
- **Svelte-Komponente `Konfigurator`** (`src/lib/Konfigurator.svelte`) mit Zoom, Drehen, Verschieben (OrbitControls) und 5 Kamera-Perspektiven
- **Ladeanzeige** mit echtem Download-Fortschritt, solange das 3D-Modell lädt
- **Konfigurierbare Eigenschaften**
  - Farbe: Pad-Rahmen in 6 Farben
  - Material: Rack (Schwarz, Alu, Weiß, Titan), Becken-Pads und Mesh-Felle in je 3 Farben
  - LED-Ring: optional in 5 Farben – blitzt beim Spielen kurz auf
  - Ausstattung: zweites Crash-Pad, Kabelbaum, Hocker, Sticks (ein-/ausblenden)
- **Geometrie-Änderungen**
  - Morph Targets: `Pad_Gross` (alle Pads und Becken stufenlos bis 25 % größer), `Kick_Gross` (größeres Kick-Pad)
  - Bones: Höhe und Galgenwinkel von Crash und Ride, Hi-Hat öffnen, Fußmaschine
- Pads anklicken spielt synthetisierte Klänge (Web Audio), „Groove abspielen“ animiert Fußmaschine, Hi-Hat und Becken
- Live-Preisübersicht und Pad-Tabelle

## Starten
```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # statische Seite im Ordner build/
```

## Veröffentlichen
**Vercel / Netlify:** Repository verbinden, Build-Befehl `npm run build`, Ausgabeordner `build`.

**GitHub Pages:** Der Workflow `.github/workflows/deploy.yml` baut und veröffentlicht automatisch bei jedem Push auf `main`.
In GitHub unter *Settings → Pages → Source* „GitHub Actions“ auswählen.

## Dateien
| Datei | Inhalt |
|---|---|
| `static/drumset.glb` | 3D-Modell, aus Blender exportiert (glTF Binary) |
| `src/lib/Konfigurator.svelte` | Komponente: 3D-Ansicht, Ladeanzeige, Optionen |
| `src/lib/Scene.svelte` | Threlte-Szene: Kamera, Licht, Materialien, LEDs, Morph Targets, Bones, Animation |
| `src/lib/options.js` | Alle Optionen und Preise |
| `src/lib/sound.js` | Web-Audio-Klänge |
| `src/routes/+page.svelte` | Website, die den Konfigurator verwendet |
| `blender/` | Blender-Datei, Build-Script und Renderings |

PULSE ist eine erfundene Marke.

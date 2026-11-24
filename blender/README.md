# PULSE E8 – Blender-Modell

| Datei | Inhalt |
|---|---|
| `edrum_e8.blend` | Blender-Datei (Blender 4.0+, Texturen eingebettet) |
| `build_edrum_e8.py` | Python-Script, das das komplette Modell erzeugt |
| `renders/` | Gesamtansicht (von oben, Drummer-Sicht), Detailansicht (Snare-Pad), Bühnenlicht |

## Aufbau (Collections)
- **Trommeln**: Snare-Pad 10″, Tom-Pads 8″/8″/8″, Kick-Pad 6,5″ – rund, mit weißem Mesh-Fell, schwarzem Spannreifen und 6 Spannschrauben; Kick-Säule mit Füßen
- **Becken**: Crash 12″, Ride 12″, Hi-Hat 10″ – Gummi-Pads mit Noppen (Normal-Map)
- **Hardware**: Rohr-Rack (Querstange, zwei Seitenflügel, vier Beine mit Kappen und Füßen, Klemmen), Arme mit Kugelgelenk, Becken-Pfosten mit Galgen, Alu-Fußmaschine, Hi-Hat-Controller-Pedal, Modul mit Display und Handyhalter, Hocker, Sticks
- **Extras**: `Extra_Crash2_*` (zweites Crash-Pad), `Extra_Kabel` (Kabelbaum entlang des Racks)
- **Rig**: Armature `Drum_Rig`
- **Render_Setup**: weißes Studio, Studio- und Bühnenlicht, 3 Kameras

## Materialien für den Konfigurator
`Shell_Finish` (Pad-Rahmen), `Hardware_Metal` (Rack), `Cymbal_Pad`, `Drumhead` (Mesh), `LED_Glow` (optionaler LED-Ring), `Screen`, `Phone_Screen`, `Pedal_Alu`

## Morph Targets (Shape Keys)
- `Pad_Gross` – alle Pads und Becken stufenlos bis 25 % größer
- `Kick_Gross` – größeres, höher sitzendes Kick-Pad

## Bones (`Drum_Rig`)
`Crash_Hoehe`, `Crash_Neigung`, `Ride_Hoehe`, `Ride_Neigung`, `HiHat_Offen`, `HiHat_Pedal`, `Fussmaschine_Schlaegel`, `Fussmaschine_Trittbrett`

## Rendern
Kamera wählen (`Cam_Gesamt`, `Cam_Detail`, `Cam_Buehne`) und F12 drücken.
Für die Bühnenansicht die `*_Studio`-Lichter ausblenden und die `Spot_*`-Lichter einblenden.

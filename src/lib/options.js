// Alle Konfigurationsmöglichkeiten an einer Stelle.
// Farben sind sRGB-Hexwerte; three.js rechnet sie selbst in den linearen Farbraum um.

export const BASE_PRICE = 790;

// Rahmen und Kessel der Pads (Material "Shell_Finish")
export const finishes = [
	{ id: 'black', name: 'Schwarz', color: '#141416', metalness: 0, roughness: 0.4, sparkle: 0, price: 0 },
	{ id: 'white', name: 'Weiß', color: '#e8e7e3', metalness: 0, roughness: 0.35, sparkle: 0, price: 40 },
	{ id: 'red', name: 'Rot', color: '#b3202a', metalness: 0, roughness: 0.35, sparkle: 0, price: 40 },
	{ id: 'blue', name: 'Blau', color: '#1f4fa8', metalness: 0, roughness: 0.35, sparkle: 0, price: 40 },
	{ id: 'silver', name: 'Silber', color: '#b9bcc2', metalness: 0.8, roughness: 0.3, sparkle: 0, price: 60 },
	{ id: 'orange', name: 'Orange', color: '#e0681e', metalness: 0, roughness: 0.4, sparkle: 0, price: 40 }
];

// Rohr-Rack und Arme (Material "Hardware_Metal")
export const hardware = [
	{ id: 'black', name: 'Schwarz', color: '#1a1a1d', roughness: 0.45, metalness: 0.3, price: 0 },
	{ id: 'silver', name: 'Alu silber', color: '#c9ccd1', roughness: 0.28, metalness: 1, price: 80 },
	{ id: 'white', name: 'Weiß', color: '#e6e5e1', roughness: 0.4, metalness: 0.1, price: 60 },
	{ id: 'titan', name: 'Titan', color: '#7a7c82', roughness: 0.22, metalness: 1, price: 120 }
];

// Becken-Pads aus Gummi (Material "Cymbal_Pad", Noppen aus der Normal-Map)
export const cymbals = [
	{ id: 'black', name: 'Schwarz', color: '#141415', roughness: 0.8, price: 0 },
	{ id: 'grey', name: 'Grau', color: '#55575c', roughness: 0.75, price: 30 },
	{ id: 'white', name: 'Weiß', color: '#dcdad5', roughness: 0.7, price: 50 }
];

// Mesh-Felle (Material "Drumhead", Gewebe aus der Normal-Map)
export const heads = [
	{ id: 'white', name: 'Weiß', color: '#e4e4e1', roughness: 0.85, price: 0 },
	{ id: 'grey', name: 'Grau', color: '#7c7e83', roughness: 0.85, price: 20 },
	{ id: 'black', name: 'Schwarz', color: '#1e1f22', roughness: 0.85, price: 20 }
];

// LED-Ränder (Material "LED_Glow", leuchtet)
export const leds = [
	{ id: 'teal', name: 'Türkis', color: '#00e6c8' },
	{ id: 'amber', name: 'Bernstein', color: '#ffa31a' },
	{ id: 'magenta', name: 'Magenta', color: '#ff2bd1' },
	{ id: 'ice', name: 'Eisblau', color: '#5ab8ff' },
	{ id: 'white', name: 'Weiß', color: '#ffffff' },
	{ id: 'off', name: 'Aus', color: '#000000', off: true }
];

export const extras = [
	{ id: 'crash2', name: 'Zweites Crash-Pad 10″', objects: ['Extra_Crash2_Arm', 'Extra_Crash2_Cymbal'], price: 89 },
	{ id: 'cables', name: 'Kabelbaum sichtbar', objects: ['Extra_Kabel'], price: 0 },
	{ id: 'throne', name: 'Drumhocker', objects: ['Hocker_Gestell', 'Hocker_Sitz'], price: 69 },
	{ id: 'sticks', name: 'Sticks 5A', objects: ['Sticks'], price: 15 }
];

export const cameraViews = [
	{ id: 'front', name: 'Vorne', position: [1.3, 1.45, -1.9], target: [0, 0.62, 0.15] },
	{ id: 'drummer', name: 'Drummer', position: [0, 1.9, 1.6], target: [0, 0.6, 0.0] },
	{ id: 'snare', name: 'Snare', position: [-0.7, 1.0, 1.0], target: [-0.31, 0.64, 0.33] },
	{ id: 'module', name: 'Modul', position: [-0.15, 1.05, 0.98], target: [-0.62, 0.78, 0.3] },
	{ id: 'top', name: 'Oben', position: [0.05, 3.0, 0.55], target: [0, 0.5, 0.15] }
];

export function defaultConfig() {
	return {
		finish: 'black',
		hardware: 'black',
		cymbals: 'black',
		heads: 'white',
		led: 'off',
		extras: { crash2: false, cables: true, throne: true, sticks: true },
		padSize: 0, // 0 = Standard, 1 = 25 % größer (Morph Target "Pad_Gross")
		kickBig: false, // größeres Kick-Pad (Morph Target "Kick_Gross")
		crashHeight: 0, // cm  (Bone)
		crashTilt: 0, // Grad (Bone)
		rideHeight: 0,
		rideTilt: 0,
		hihatOpen: 0 // cm (Bone)
	};
}

// Pad-Größe in Zoll für Anzeige und Tabelle
export const padInch = (base, size) => String(Math.round(base * (1 + 0.25 * size) * 2) / 2).replace('.', ',');

const byId = (list, id) => list.find((x) => x.id === id);

export function priceLines(c) {
	const lines = [
		{ label: 'PULSE E8 E-Drum-Set mit Modul', price: BASE_PRICE },
		{ label: `Pad-Rahmen: ${byId(finishes, c.finish).name}`, price: byId(finishes, c.finish).price },
		{ label: `Rack: ${byId(hardware, c.hardware).name}`, price: byId(hardware, c.hardware).price },
		{ label: `Becken-Pads: ${byId(cymbals, c.cymbals).name}`, price: byId(cymbals, c.cymbals).price },
		{ label: `Mesh-Felle: ${byId(heads, c.heads).name}`, price: byId(heads, c.heads).price }
	];
	if (c.led !== 'off') lines.push({ label: `LED-Ring: ${byId(leds, c.led).name}`, price: 49 });
	if (c.padSize > 0.05) lines.push({ label: `Größere Pads (Snare ${padInch(10, c.padSize)}″)`, price: Math.round(c.padSize * 120) });
	if (c.kickBig) lines.push({ label: 'Großes Kick-Pad 8″', price: 40 });
	for (const e of extras) if (c.extras[e.id]) lines.push({ label: e.name, price: e.price });
	return lines;
}

export const euro = (n) =>
	new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n);

export { byId };

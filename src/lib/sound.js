// Kleine Web-Audio-Drum-Machine: alle Klänge werden live synthetisiert (keine Audiodateien).
let ctx;
let master;
let noiseBuffer;

function audio() {
	if (!ctx) {
		ctx = new (window.AudioContext || window.webkitAudioContext)();
		master = ctx.createGain();
		master.gain.value = 0.7;
		master.connect(ctx.destination);
		noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
		const d = noiseBuffer.getChannelData(0);
		for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
	}
	if (ctx.state === 'suspended') ctx.resume();
	return ctx;
}

function noise(t, dur, { type = 'highpass', freq = 7000, q = 0.7, gain = 0.5 } = {}) {
	const src = ctx.createBufferSource();
	src.buffer = noiseBuffer;
	const f = ctx.createBiquadFilter();
	f.type = type;
	f.frequency.value = freq;
	f.Q.value = q;
	const g = ctx.createGain();
	g.gain.setValueAtTime(gain, t);
	g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
	src.connect(f).connect(g).connect(master);
	src.start(t, Math.random());
	src.stop(t + dur + 0.05);
}

function tone(t, f0, f1, dur, gain = 0.9, type = 'sine') {
	const o = ctx.createOscillator();
	o.type = type;
	o.frequency.setValueAtTime(f0, t);
	o.frequency.exponentialRampToValueAtTime(f1, t + dur * 0.6);
	const g = ctx.createGain();
	g.gain.setValueAtTime(gain, t);
	g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
	o.connect(g).connect(master);
	o.start(t);
	o.stop(t + dur + 0.05);
}

const voices = {
	kick: (t, o) => {
		const deep = o.kickBig ? 0.8 : 0;
		tone(t, 150 - deep * 25, 42 - deep * 6, 0.45 + deep * 0.15, 1.0);
		noise(t, 0.02, { type: 'lowpass', freq: 3000, gain: 0.25 });
	},
	snare: (t, o) => {
		const deep = 0;
		tone(t, 230 - deep * 30, 160, 0.12, 0.45, 'triangle');
		noise(t, 0.22 + deep * 0.05, { type: 'bandpass', freq: 3200, q: 0.6, gain: 0.55 });
	},
	tom1: (t) => tone(t, 260, 170, 0.45, 0.75),
	tom2: (t) => tone(t, 200, 130, 0.5, 0.75),
	tom3: (t) => tone(t, 150, 92, 0.6, 0.8),
	floor: (t) => tone(t, 130, 82, 0.7, 0.85),
	floor2: (t) => tone(t, 160, 100, 0.6, 0.85),
	hihat: (t, o) => noise(t, (o.hihatOpen ?? 0) > 0.8 ? 0.35 : 0.06, { freq: 8500, gain: 0.32 }),
	hihatOpen: (t) => noise(t, 0.45, { freq: 8000, gain: 0.3 }),
	crash: (t, o) =>
		o.china
			? (noise(t, 1.6, { type: 'bandpass', freq: 4200, q: 0.9, gain: 0.5 }), noise(t, 0.6, { freq: 2500, gain: 0.2 }))
			: noise(t, 2.0, { freq: 5200, gain: 0.42 }),
	ride: (t, o) => {
		noise(t, o.flatRide ? 0.5 : 1.2, { type: 'bandpass', freq: 7500, q: 1.4, gain: 0.25 });
		tone(t, 3400, 3300, 0.6, 0.06, 'triangle');
	},
	crash2: (t) => noise(t, 2.4, { freq: 4200, gain: 0.4 }),
	splash: (t) => noise(t, 0.8, { freq: 7000, gain: 0.35 }),
	cowbell: (t) => {
		tone(t, 560, 560, 0.35, 0.18, 'square');
		tone(t, 845, 845, 0.3, 0.12, 'square');
	}
};

export function play(name, options = {}, when = 0) {
	audio();
	const v = voices[name];
	if (v) v(ctx.currentTime + when, options);
}

export function now() {
	return audio().currentTime;
}

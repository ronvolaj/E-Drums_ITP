<script>
	import { onMount } from 'svelte';
	import { Canvas } from '@threlte/core';
	import { WebGLRenderer } from 'three';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import Scene from './Scene.svelte';
	import { finishes, hardware, cymbals, heads, leds, extras, cameraViews, defaultConfig, padInch } from './options.js';

	/** Konfigurator: 3D-Ansicht mit Zoom/Perspektive + alle Optionen. */
	let { src = './drumset.glb', config = $bindable(defaultConfig()) } = $props();

	let model = $state(null);
	let progress = $state(0);
	let loadedMB = $state(0);
	let error = $state('');
	let view = $state('front');
	let viewNonce = $state(0);
	let groove = $state(false);
	let lastHit = $state('');
	const FALLBACK_SIZE = 4.2e6;

	onMount(() => {
		const loader = new GLTFLoader();
		loader.load(
			src,
			(gltf) => {
				progress = 1;
				// kurz 100 % zeigen, dann einblenden
				setTimeout(() => (model = gltf.scene), 250);
			},
			(e) => {
				const total = e.lengthComputable && e.total ? e.total : FALLBACK_SIZE;
				progress = Math.min(0.99, e.loaded / total);
				loadedMB = e.loaded / 1e6;
			},
			(err) => (error = 'Das 3D-Modell konnte nicht geladen werden. ' + (err?.message ?? ''))
		);
	});

	function setView(id) {
		view = id;
		viewNonce++;
	}

	const names = {
		kick: 'Kick', snare: 'Snare', tom1: 'Tom 1', tom2: 'Tom 2', tom3: 'Tom 3',
		hihat: 'Hi-Hat', hihatOpen: 'Hi-Hat offen', crash: 'Crash 12″', crash2: 'Crash 10″', ride: 'Ride 12″'
	};
	let hitTimer;
	function onhit(n) {
		if (groove) return;
		lastHit = names[n] ?? '';
		clearTimeout(hitTimer);
		hitTimer = setTimeout(() => (lastHit = ''), 900);
	}

	const fmt = (n) => String(n).replace('.', ',');
	const createRenderer = (canvas) =>
		new WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'high-performance' });
</script>

<section class="konfigurator" aria-label="Schlagzeug-Konfigurator">
	<div class="stage">
		{#if model}
			<div class="canvas">
				<Canvas {createRenderer}>
					<Scene {model} {config} view={view + ':' + viewNonce} {groove} {onhit} />
				</Canvas>
			</div>
		{/if}

		{#if !model}
			<div class="loader" role="status" aria-live="polite">
				{#if error}
					<p class="error">{error}</p>
				{:else}
					<svg class="ring" viewBox="0 0 120 120" aria-hidden="true">
						<circle cx="60" cy="60" r="50" class="track" />
						<circle cx="60" cy="60" r="50" class="bar" style="stroke-dashoffset: {314.16 * (1 - progress)}" />
						{#each Array(10) as _, i}
							<rect x="57" y="2" width="6" height="12" rx="2" class="lug" transform="rotate({i * 36 + 18} 60 60)" />
						{/each}
					</svg>
					<div class="loader-text">
						<span class="pct">{Math.round(progress * 100)}<small>%</small></span>
						<span class="sub">Schlagzeug wird geladen · {loadedMB.toFixed(1)} MB</span>
					</div>
				{/if}
			</div>
		{/if}

		<div class="views" role="group" aria-label="Kameraperspektive">
			{#each cameraViews as v}
				<button class:active={view === v.id} onclick={() => setView(v.id)} disabled={!model}>{v.name}</button>
			{/each}
		</div>

		<div class="stage-foot">
			<button class="groove" class:on={groove} onclick={() => (groove = !groove)} disabled={!model}>
				<span class="dot" aria-hidden="true"></span>{groove ? 'Groove stoppen' : 'Groove abspielen'}
			</button>
			<p class="hint">
				{#if lastHit}<strong>{lastHit}</strong>{:else}Ziehen zum Drehen · Scrollen/Pinch zum Zoomen · Trommeln anklicken zum Spielen{/if}
			</p>
		</div>
	</div>

	<div class="panel">
		<fieldset>
			<legend>Pad-Rahmen <span class="val">{finishes.find((f) => f.id === config.finish).name}</span></legend>
			<div class="swatches">
				{#each finishes as f}
					<label class="swatch" title={f.name}>
						<input type="radio" name="finish" value={f.id} bind:group={config.finish} />
						<span class="chip" class:sparkle={f.sparkle} class:wood={f.wood} class:walnut={f.texture} style="--c: {f.color}"></span>
						<span class="sr">{f.name}</span>
					</label>
				{/each}
			</div>
		</fieldset>

		<fieldset>
			<legend>Rack</legend>
			<div class="pills">
				{#each hardware as h}
					<label class="pill">
						<input type="radio" name="hardware" value={h.id} bind:group={config.hardware} />
						<span><i style="--c: {h.color}"></i>{h.name}</span>
					</label>
				{/each}
			</div>
		</fieldset>

		<fieldset>
			<legend>Becken-Pads</legend>
			<div class="pills">
				{#each cymbals as c}
					<label class="pill">
						<input type="radio" name="cymbals" value={c.id} bind:group={config.cymbals} />
						<span>{c.name}</span>
					</label>
				{/each}
			</div>
		</fieldset>

		<fieldset>
			<legend>Mesh-Felle</legend>
			<div class="pills">
				{#each heads as h}
					<label class="pill">
						<input type="radio" name="heads" value={h.id} bind:group={config.heads} />
						<span><i style="--c: {h.color}"></i>{h.name}</span>
					</label>
				{/each}
			</div>
		</fieldset>

		<fieldset>
			<legend>LED-Ring <span class="val">{leds.find((l) => l.id === config.led).name}</span></legend>
			<div class="swatches">
				{#each leds as l}
					<label class="swatch" title={l.name}>
						<input type="radio" name="led" value={l.id} bind:group={config.led} />
						<span class="chip led" class:off={l.off} style="--c: {l.color}"></span>
						<span class="sr">{l.name}</span>
					</label>
				{/each}
			</div>
		</fieldset>

		<fieldset>
			<legend>Form <span class="tag">Morph Targets</span></legend>
			<label class="range" for="round">
				<span>Pad-Größe</span><output>Snare {padInch(10, config.padSize)}″ · Toms {padInch(8, config.padSize)}″</output>
				<input id="round" type="range" min="0" max="1" step="0.25" bind:value={config.padSize} />
			</label>
			<div class="toggles">
				<div class="seg" role="group" aria-label="Kick-Säule">
					<button class:active={!config.kickBig} onclick={() => (config.kickBig = false)}>Kick 6,5″</button>
					<button class:active={config.kickBig} onclick={() => (config.kickBig = true)}>Kick 8″</button>
				</div>
			</div>
		</fieldset>

		<fieldset>
			<legend>Aufbau der Ständer <span class="tag">Bones</span></legend>
			<label class="range" for="ch">
				<span>Crash-Höhe</span><output>{config.crashHeight > 0 ? '+' : ''}{config.crashHeight} cm</output>
				<input id="ch" type="range" min="-15" max="20" step="1" bind:value={config.crashHeight} />
			</label>
			<label class="range" for="ct">
				<span>Crash-Galgen</span><output>{config.crashTilt > 0 ? '+' : ''}{config.crashTilt}°</output>
				<input id="ct" type="range" min="-20" max="25" step="1" bind:value={config.crashTilt} />
			</label>
			<label class="range" for="rh">
				<span>Ride-Höhe</span><output>{config.rideHeight > 0 ? '+' : ''}{config.rideHeight} cm</output>
				<input id="rh" type="range" min="-15" max="20" step="1" bind:value={config.rideHeight} />
			</label>
			<label class="range" for="rt">
				<span>Ride-Galgen</span><output>{config.rideTilt > 0 ? '+' : ''}{config.rideTilt}°</output>
				<input id="rt" type="range" min="-20" max="25" step="1" bind:value={config.rideTilt} />
			</label>
			<label class="range" for="hh">
				<span>Hi-Hat offen</span><output>{fmt(config.hihatOpen)} cm</output>
				<input id="hh" type="range" min="0" max="4" step="0.5" bind:value={config.hihatOpen} />
			</label>
		</fieldset>

		<fieldset>
			<legend>Ausstattung</legend>
			<div class="checks">
				{#each extras as e}
					<label class="check">
						<input type="checkbox" bind:checked={config.extras[e.id]} />
						<span>{e.name}</span>
					</label>
				{/each}
			</div>
		</fieldset>

		<button class="reset" onclick={() => (config = defaultConfig())}>Auf Standard zurücksetzen</button>
	</div>
</section>

<style>
	/* Karte: weiche Ebenen-Schatten, große Rundung */
	.konfigurator {
		display: grid;
		grid-template-columns: minmax(0, 1fr) 380px;
		border-radius: 24px;
		overflow: hidden;
		background: var(--panel);
		box-shadow:
			0 1px 0 rgb(255 255 255 / 0.9) inset,
			0 1px 2px rgb(20 30 60 / 0.06),
			0 12px 32px -8px rgb(20 30 60 / 0.14),
			0 40px 80px -24px rgb(42 85 224 / 0.18);
		border: 1px solid rgb(255 255 255 / 0.7);
	}

	/* Bühne: Studio-Licht von oben, Vignette an den Rändern */
	.stage {
		position: relative;
		min-height: 660px;
		isolation: isolate;
		background:
			radial-gradient(ellipse 55% 45% at 50% 30%, #ffffff 0%, rgb(255 255 255 / 0) 70%),
			radial-gradient(ellipse 90% 60% at 50% 100%, rgb(42 85 224 / 0.10) 0%, transparent 70%),
			linear-gradient(180deg, var(--stage-top) 0%, var(--stage-bottom) 100%);
	}
	.stage::after {
		content: '';
		position: absolute;
		inset: 0;
		pointer-events: none;
		z-index: 1;
		background: radial-gradient(ellipse 85% 80% at 50% 45%, transparent 60%, rgb(20 30 60 / 0.10) 100%);
	}
	.canvas {
		position: absolute;
		inset: 0;
		animation: reveal 1.1s cubic-bezier(0.2, 0.7, 0.2, 1) both;
	}
	@keyframes reveal {
		from { opacity: 0; transform: scale(0.97); filter: blur(6px); }
	}

	/* Ladeanzeige: Fortschrittsring mit 10 "Spannböckchen" */
	.loader {
		position: absolute;
		inset: 0;
		z-index: 2;
		display: grid;
		place-content: center;
		justify-items: center;
		gap: 20px;
		text-align: center;
	}
	.ring { width: 168px; height: 168px; transform: rotate(-90deg); filter: drop-shadow(0 8px 20px rgb(42 85 224 / 0.25)); }
	.track { fill: none; stroke: var(--track); stroke-width: 6; }
	.bar { fill: none; stroke: var(--accent); stroke-width: 6; stroke-linecap: round; stroke-dasharray: 314.16; transition: stroke-dashoffset 0.25s linear; }
	.lug { fill: var(--line-strong); animation: lugpulse 1.6s ease-in-out infinite; }
	.lug:nth-child(odd) { animation-delay: 0.8s; }
	@keyframes lugpulse { 50% { fill: var(--accent); } }
	.loader-text { display: grid; gap: 6px; }
	.pct { font-family: var(--display); font-size: 2.6rem; font-weight: 700; line-height: 1; color: var(--text); font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
	.pct small { font-size: 1.3rem; color: var(--muted); }
	.sub { font-size: 0.82rem; color: var(--muted); }
	.error { color: #c0392b; max-width: 32ch; }

	/* schwebende Glas-Bedienelemente */
	.views, .groove {
		background: rgb(255 255 255 / 0.72);
		backdrop-filter: blur(14px) saturate(1.4);
		-webkit-backdrop-filter: blur(14px) saturate(1.4);
		border: 1px solid rgb(255 255 255 / 0.9);
		box-shadow: 0 6px 20px -6px rgb(20 30 60 / 0.25);
	}
	.views {
		position: absolute;
		z-index: 3;
		top: 16px;
		left: 16px;
		display: flex;
		flex-wrap: wrap;
		gap: 2px;
		padding: 5px;
		border-radius: 999px;
	}
	.views button {
		font: 600 0.8rem/1 var(--body);
		color: var(--muted);
		background: none;
		border: 0;
		padding: 9px 14px;
		border-radius: 999px;
		cursor: pointer;
		transition: color 0.2s, background 0.25s, box-shadow 0.25s;
	}
	.views button:hover:not(:disabled) { color: var(--text); background: rgb(42 85 224 / 0.06); }
	.views button.active {
		background: linear-gradient(180deg, #4b74ff, var(--accent));
		color: var(--accent-ink);
		box-shadow: 0 4px 12px -2px rgb(42 85 224 / 0.5);
	}

	.stage-foot {
		position: absolute;
		z-index: 3;
		left: 16px;
		right: 16px;
		bottom: 16px;
		display: flex;
		align-items: center;
		gap: 14px;
		flex-wrap: wrap;
		pointer-events: none;
	}
	.groove {
		pointer-events: auto;
		display: inline-flex;
		align-items: center;
		gap: 10px;
		font: 700 0.85rem/1 var(--body);
		color: var(--text);
		padding: 12px 18px;
		border-radius: 999px;
		cursor: pointer;
		transition: transform 0.2s, box-shadow 0.2s;
	}
	.groove:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 10px 24px -8px rgb(42 85 224 / 0.45); }
	.groove .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 4px rgb(42 85 224 / 0.15); }
	.groove.on .dot { background: #ff4d5e; box-shadow: 0 0 0 4px rgb(255 77 94 / 0.2); animation: pulse 0.577s infinite; }
	@keyframes pulse { 50% { opacity: 0.35; } }
	.hint { margin: 0; font-size: 0.8rem; color: var(--muted); padding: 6px 12px; border-radius: 999px; background: rgb(255 255 255 / 0.55); backdrop-filter: blur(6px); }
	.hint strong { font-family: var(--display); font-size: 1rem; color: var(--accent); }

	button:disabled { opacity: 0.45; cursor: default; }
	button:focus-visible, input:focus-visible + span, input:focus-visible + .chip, input[type='range']:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

	/* Optionen */
	.panel {
		border-left: 1px solid var(--line);
		padding: 10px 24px 24px;
		max-height: 760px;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		background: linear-gradient(180deg, #ffffff 0%, #fafbfd 100%);
		scrollbar-width: thin;
		scrollbar-color: var(--line-strong) transparent;
	}
	fieldset { border: 0; border-bottom: 1px solid var(--line); margin: 0; padding: 18px 0; min-width: 0; }
	fieldset:last-of-type { border-bottom: 0; }
	legend {
		float: left;
		width: 100%;
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 8px;
		margin-bottom: 14px;
		font: 600 0.92rem/1.2 var(--display);
		color: var(--text);
		letter-spacing: -0.01em;
	}
	legend + * { clear: both; }
	.val { font: 500 0.8rem/1.2 var(--body); color: var(--muted); }
	.tag { font: 600 0.66rem/1 var(--body); color: var(--accent); background: var(--accent-soft); padding: 4px 8px; border-radius: 999px; }

	input[type='radio'], input[type='checkbox'] { position: absolute; opacity: 0; pointer-events: none; }
	.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }

	.swatches { display: flex; flex-wrap: wrap; gap: 12px; }
	.swatch { cursor: pointer; }
	.chip {
		display: block;
		width: 42px;
		height: 42px;
		border-radius: 50%;
		background: radial-gradient(circle at 32% 28%, color-mix(in srgb, var(--c) 45%, white) 0%, var(--c) 48%, color-mix(in srgb, var(--c) 65%, black) 100%);
		box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.12), 0 4px 10px -3px rgb(20 30 60 / 0.35);
		transition: transform 0.2s cubic-bezier(0.3, 1.6, 0.5, 1), box-shadow 0.2s;
	}
	.chip.sparkle {
		background-image:
			radial-gradient(circle at 30% 40%, #fff 0 1px, transparent 1.5px),
			radial-gradient(circle at 65% 30%, #fff 0 1px, transparent 1.5px),
			radial-gradient(circle at 55% 70%, #fff 0 1px, transparent 1.5px),
			radial-gradient(circle at 32% 28%, color-mix(in srgb, var(--c) 45%, white) 0%, var(--c) 48%, color-mix(in srgb, var(--c) 65%, black) 100%);
	}
	.chip.walnut { background: repeating-linear-gradient(95deg, #6b452a 0 4px, #4a2c18 4px 6px, #5e3b22 6px 10px, #3c2313 10px 11px); }
	.chip.led { background: radial-gradient(circle, color-mix(in srgb, var(--c) 30%, white) 0%, var(--c) 45%, color-mix(in srgb, var(--c) 40%, black) 100%); box-shadow: 0 0 16px -2px color-mix(in srgb, var(--c) 75%, transparent), inset 0 0 0 1px rgb(0 0 0 / 0.1); }
	.chip.led.off { background: repeating-linear-gradient(135deg, #e3e6eb 0 4px, #f4f5f7 4px 8px); box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.12); }
	.chip.wood { background: repeating-linear-gradient(100deg, #d4a56d 0 5px, #b98348 5px 7px, #cf9b5e 7px 11px); }
	.swatch input:checked + .chip { box-shadow: 0 0 0 3px #fff, 0 0 0 5px var(--accent), 0 8px 18px -4px rgb(42 85 224 / 0.45); transform: scale(1.04); }
	.swatch:hover .chip { transform: translateY(-2px) scale(1.06); }

	.pills { display: flex; flex-wrap: wrap; gap: 8px; }
	.pill span {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 9px 14px;
		border-radius: 12px;
		border: 1px solid var(--line);
		background: #fff;
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--text);
		cursor: pointer;
		transition: border-color 0.2s, background 0.2s, box-shadow 0.2s, transform 0.15s;
	}
	.pill i { width: 12px; height: 12px; border-radius: 50%; background: var(--c); box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.2); }
	.pill input:checked + span { border-color: var(--accent); background: var(--accent-soft); color: var(--accent); box-shadow: 0 0 0 3px rgb(42 85 224 / 0.12); }
	.pill:hover span { border-color: var(--line-strong); transform: translateY(-1px); }

	.range { display: grid; grid-template-columns: 1fr auto; gap: 8px 10px; margin-bottom: 16px; font-size: 0.86rem; font-weight: 500; }
	.range output { font-size: 0.8rem; font-weight: 600; color: var(--accent); font-variant-numeric: tabular-nums; background: var(--accent-soft); padding: 3px 8px; border-radius: 999px; }
	.range input { grid-column: 1 / -1; width: 100%; appearance: none; -webkit-appearance: none; height: 6px; border-radius: 999px; background: linear-gradient(90deg, #dfe4f6, #c9d3f5); cursor: pointer; }
	.range input::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #fff; border: 2px solid var(--accent); box-shadow: 0 2px 8px rgb(42 85 224 / 0.4); transition: transform 0.15s; }
	.range input::-webkit-slider-thumb:hover { transform: scale(1.15); }
	.range input::-moz-range-thumb { width: 18px; height: 18px; border-radius: 50%; background: #fff; border: 2px solid var(--accent); box-shadow: 0 2px 8px rgb(42 85 224 / 0.4); }

	.toggles { display: grid; gap: 8px; margin-top: 4px; }
	.seg { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; padding: 4px; border-radius: 14px; background: #eef1f6; }
	.seg button { font: 600 0.82rem/1 var(--body); color: var(--muted); background: none; border: 0; padding: 11px; border-radius: 10px; cursor: pointer; transition: background 0.2s, color 0.2s, box-shadow 0.2s; }
	.seg button.active { background: #fff; color: var(--accent); box-shadow: 0 2px 8px -2px rgb(20 30 60 / 0.2); }

	.checks { display: grid; gap: 10px; }
	.check span { display: flex; align-items: center; gap: 12px; font-size: 0.88rem; font-weight: 500; cursor: pointer; }
	.check span::before {
		content: '';
		width: 20px;
		height: 20px;
		border-radius: 6px;
		border: 1.5px solid var(--line-strong);
		background: #fff;
		flex: none;
		transition: background 0.2s, border-color 0.2s;
	}
	.check input:checked + span::before {
		background: var(--accent) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3.5 8.5l3 3 6-7' fill='none' stroke='%23ffffff' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/14px no-repeat;
		border-color: var(--accent);
	}

	.reset { margin-top: 18px; align-self: flex-start; font: 600 0.8rem/1 var(--body); color: var(--muted); background: #fff; border: 1px solid var(--line); padding: 10px 14px; border-radius: 10px; cursor: pointer; transition: color 0.2s, border-color 0.2s; }
	.reset:hover { color: var(--accent); border-color: var(--accent); }

	@media (max-width: 960px) {
		.konfigurator { grid-template-columns: minmax(0, 1fr); border-radius: 18px; }
		.stage { min-height: 0; height: 66vh; max-height: 560px; }
		.panel { border-left: 0; border-top: 1px solid var(--line); max-height: none; }
		.hint { display: none; }
	}
</style>

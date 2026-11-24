<script>
	import Konfigurator from '$lib/Konfigurator.svelte';
	import { defaultConfig, priceLines, euro, byId, finishes, hardware, heads, padInch } from '$lib/options.js';

	let config = $state(defaultConfig());
	const lines = $derived(priceLines(config));
	const total = $derived(lines.reduce((s, l) => s + l.price, 0));
	// sanft zu einem Bereich scrollen (keine #-Links, weil die Seite den Hash-Router nutzt)
	const go = (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });

	const shells = $derived([
		{ name: 'Snare', size: padInch(10, config.padSize) + '″', zones: '2 Zonen (Fell + Rand)', note: 'Mesh-Fell, 6 Spannschrauben' },
		{ name: 'Tom 1', size: padInch(8, config.padSize) + '″', zones: '1 Zone', note: 'an der Querstange' },
		{ name: 'Tom 2', size: padInch(8, config.padSize) + '″', zones: '1 Zone', note: 'an der Querstange' },
		{ name: 'Tom 3', size: padInch(8, config.padSize) + '″', zones: '1 Zone', note: 'am rechten Flügel' },
		{ name: 'Kick', size: config.kickBig ? '8″' : '6,5″', zones: '1 Zone', note: 'Kick-Säule mit Fußmaschine' },
		{ name: 'Hi-Hat', size: padInch(10, config.padSize) + '″', zones: '1 Zone + Controller', note: 'am Rack, Pedal am Boden' },
		{ name: 'Crash', size: padInch(12, config.padSize) + '″', zones: '1 Zone + Choke', note: 'Pfosten mit Galgen' },
		{ name: 'Ride', size: padInch(12, config.padSize) + '″', zones: '1 Zone', note: 'Pfosten mit Galgen' }
	]);
</script>

<svelte:head>
	<title>PULSE E8 Konfigurator</title>
</svelte:head>

<div class="bg" aria-hidden="true"></div>

<header class="top">
	<div class="top-inner">
		<a class="brand" href="./" aria-label="PULSE Percussion">
			<span class="logo"><svg viewBox="0 0 48 24" aria-hidden="true"><path d="M2 12h10l4-9 6 18 5-14 3 5h16" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" /></svg></span>
			PULSE
		</a>
		<nav aria-label="Seitenbereiche">
			<button onclick={() => go('konfigurator')}>Konfigurator</button>
			<button onclick={() => go('pads')}>Pads</button>
			<button onclick={() => go('preis')}>Preis</button>
		</nav>
		<span class="badge">E8 · E-Drum-Set</span>
	</div>
</header>

<div class="page">
	<section class="intro">
		<div class="intro-text">
			<h1>E-Drum-Konfigurator</h1>
			<p class="lead">Das Schlagzeug habe ich in Blender modelliert und als glTF exportiert. Du kannst es drehen und zoomen, Farben und Pad-Größe ändern und die Ständer verstellen. Wenn du auf ein Pad klickst, hörst du es.</p>
		</div>
		<ul class="stats" aria-label="Das Set auf einen Blick">
			<li><strong>5</strong><span>Mesh-Pads</span></li>
			<li><strong>3</strong><span>Becken-Pads</span></li>
			<li><strong>{padInch(10, config.padSize)}″</strong><span>Snare</span></li>
			<li class="price"><strong>{euro(total)}</strong><span>dein Set</span></li>
		</ul>
	</section>

	<div id="konfigurator" class="anchor">
		<Konfigurator bind:config src="./drumset.glb" />
	</div>

	<section class="details">
		<div id="pads" class="card specs">
			<div class="card-head">
				<h2>Pads</h2>
				<span class="sub">{byId(finishes, config.finish).name} · Rack {byId(hardware, config.hardware).name}</span>
			</div>
			<div class="table-wrap">
				<table>
					<thead><tr><th>Pad</th><th>Größe</th><th>Zonen</th><th>Detail</th></tr></thead>
					<tbody>
						{#each shells as s}
							<tr><td class="name">{s.name}</td><td><span class="size">{s.size}</span></td><td>{s.zones}</td><td class="note">{s.note}</td></tr>
						{/each}
					</tbody>
				</table>
			</div>
			<p class="small">Modul mit Display und Handyhalter, Rohr-Rack aus 38-mm-Rohr mit vier Beinen.</p>
		</div>

		<aside id="preis" class="card summary" aria-label="Preisübersicht">
			<div class="total">
				<span>Gesamt</span>
				<strong>{euro(total)}</strong>
			</div>
			<ul>
				{#each lines as l}
					<li><span>{l.label}</span><span class="amt">{l.price ? '+ ' + euro(l.price) : 'inkl.'}</span></li>
				{/each}
			</ul>
			<p class="small">Beispielpreise für dieses Schulprojekt.</p>
		</aside>
	</section>

	<footer>
		<span class="brand small-brand"><span class="logo"><svg viewBox="0 0 48 24" aria-hidden="true"><path d="M2 12h10l4-9 6 18 5-14 3 5h16" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" /></svg></span>PULSE</span>
		<p>Schulprojekt · 3D-Modell in Blender, Website mit Svelte, Threlte und three.js · PULSE ist eine erfundene Marke</p>
	</footer>
</div>

<style>
	:global(:root) {
		/* Helles Fotostudio: kühles Weißgrau, schwarzes Set, Kobaltblau als Akzent */
		--ink: #eef1f5;
		--panel: #ffffff;
		--line: #e1e5eb;
		--line-strong: #b9c0cb;
		--text: #111827;
		--muted: #5f6878;
		--accent: #2a55e0;
		--accent-ink: #ffffff;
		--accent-soft: #e8eefd;
		--accent-line: #b7c6f5;
		--track: #dde3ee;
		--glass: rgb(255 255 255 / 0.8);
		--stage-glow: #ffffff;
		--stage-top: #f8f9fb;
		--stage-bottom: #dfe4ec;
		--display: 'Unbounded', 'Arial Black', system-ui, sans-serif;
		--body: 'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
		--mono: 'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace;
		color-scheme: light;
		scroll-behavior: smooth;
		scroll-padding-top: 84px;
	}
	:global(body) {
		margin: 0;
		background: var(--ink);
		color: var(--text);
		font: 400 15px/1.6 var(--body);
		-webkit-font-smoothing: antialiased;
		overflow-x: clip;
	}

	/* Hintergrund: weiche Lichtflecken + feines Punktraster */
	.bg {
		position: fixed;
		inset: 0;
		z-index: -1;
		background:
			radial-gradient(40rem 28rem at 8% -6%, rgb(42 85 224 / 0.16), transparent 70%),
			radial-gradient(36rem 30rem at 100% 10%, rgb(120 160 255 / 0.18), transparent 70%),
			radial-gradient(50rem 30rem at 50% 110%, rgb(42 85 224 / 0.08), transparent 70%),
			radial-gradient(circle, rgb(17 24 39 / 0.07) 1px, transparent 1.2px) 0 0 / 22px 22px,
			var(--ink);
	}

	/* Kopfzeile aus Glas */
	.top {
		position: sticky;
		top: env(safe-area-inset-top, 0px);
		z-index: 20;
		padding-left: max(16px, env(safe-area-inset-left, 0px));
		padding-right: max(16px, env(safe-area-inset-right, 0px));
		padding-block: 12px;
	}
	.top-inner {
		max-width: 1320px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		gap: 20px;
		padding: 10px 14px 10px 18px;
		border-radius: 18px;
		background: rgb(255 255 255 / 0.7);
		backdrop-filter: blur(16px) saturate(1.5);
		-webkit-backdrop-filter: blur(16px) saturate(1.5);
		border: 1px solid rgb(255 255 255 / 0.9);
		box-shadow: 0 8px 24px -12px rgb(20 30 60 / 0.25);
	}
	.brand { display: inline-flex; align-items: center; gap: 10px; color: var(--text); text-decoration: none; font: 700 1.05rem/1 var(--display); letter-spacing: 0.16em; }
	.logo { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #5b82ff, #1d3fb8); color: #fff; box-shadow: 0 6px 14px -4px rgb(42 85 224 / 0.6); }
	.logo svg { width: 22px; height: 11px; }
	nav { display: flex; gap: 4px; margin-left: auto; }
	nav button { font: 600 0.88rem/1 var(--body); color: var(--muted); background: none; border: 0; cursor: pointer; padding: 9px 12px; border-radius: 10px; transition: color 0.2s, background 0.2s; }
	nav button:hover { color: var(--accent); background: var(--accent-soft); }
	.badge { font-size: 0.78rem; font-weight: 600; color: var(--accent); background: var(--accent-soft); border: 1px solid var(--accent-line); padding: 7px 12px; border-radius: 999px; white-space: nowrap; }

	.page {
		max-width: 1320px;
		margin: 0 auto;
		padding-block: 28px 48px;
		padding-left: max(16px, env(safe-area-inset-left, 0px));
		padding-right: max(16px, env(safe-area-inset-right, 0px));
		display: grid;
		gap: 36px;
	}

	.page > *, .intro > *, .details > * { min-width: 0; }

	/* Einstieg */
	.intro { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 28px 48px; animation: rise 0.8s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
	h1 {
		margin: 0 0 14px;
		font: 700 clamp(2rem, 4.6vw, 3.4rem)/1.04 var(--display);
		letter-spacing: -0.035em;
		text-wrap: balance;
		background: linear-gradient(180deg, #111827 30%, #34405a 100%);
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}
	.lead { margin: 0; max-width: 60ch; color: var(--muted); font-size: 1.05rem; }
	.stats { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4, auto); gap: 10px; }
	.stats li {
		display: grid;
		gap: 2px;
		padding: 14px 18px;
		border-radius: 16px;
		background: rgb(255 255 255 / 0.75);
		border: 1px solid rgb(255 255 255 / 0.9);
		box-shadow: 0 6px 18px -10px rgb(20 30 60 / 0.3);
		min-width: 92px;
	}
	.stats strong { font: 700 1.35rem/1.1 var(--display); letter-spacing: -0.02em; font-variant-numeric: tabular-nums; white-space: nowrap; }
	.stats span { font-size: 0.78rem; color: var(--muted); font-weight: 500; }
	.stats .price { background: linear-gradient(140deg, #4b74ff, #1d3fb8); border-color: transparent; box-shadow: 0 12px 26px -10px rgb(42 85 224 / 0.6); }
	.stats .price strong, .stats .price span { color: #fff; }
	.stats .price span { opacity: 0.8; }

	.anchor { animation: rise 0.9s 0.1s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
	@keyframes rise { from { opacity: 0; transform: translateY(14px); } }

	/* Karten unter dem Konfigurator */
	.details { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 24px; align-items: start; }
	.card {
		background: rgb(255 255 255 / 0.85);
		border: 1px solid rgb(255 255 255 / 0.9);
		border-radius: 22px;
		padding: 24px;
		box-shadow: 0 1px 2px rgb(20 30 60 / 0.05), 0 16px 36px -18px rgb(20 30 60 / 0.25);
	}
	.card-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
	h2 { margin: 0; font: 700 1.3rem/1.1 var(--display); letter-spacing: -0.02em; }
	.card-head .sub { font-size: 0.82rem; color: var(--muted); }
	.table-wrap { overflow-x: auto; }
	table { width: 100%; border-collapse: collapse; font-size: 0.9rem; min-width: 520px; }
	th { text-align: left; font: 600 0.75rem/1 var(--body); color: var(--muted); padding: 10px 12px; border-bottom: 1px solid var(--line); }
	td { padding: 12px; border-bottom: 1px solid var(--line); }
	tbody tr { transition: background 0.15s; }
	tbody tr:hover { background: #f5f7fc; }
	tbody tr:last-child td { border-bottom: 0; }
	td.name { font-weight: 600; }
	td.note { color: var(--muted); }
	.size { display: inline-block; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--accent); background: var(--accent-soft); padding: 3px 9px; border-radius: 999px; white-space: nowrap; }
	.small { color: var(--muted); font-size: 0.8rem; margin: 14px 0 0; }

	.summary { position: sticky; top: 96px; padding: 0; overflow: hidden; }
	.total {
		display: grid;
		gap: 4px;
		padding: 22px 24px;
		color: #fff;
		background:
			radial-gradient(20rem 10rem at 100% 0%, rgb(255 255 255 / 0.22), transparent 70%),
			linear-gradient(140deg, #4b74ff, #1d3fb8);
	}
	.total span { font-size: 0.8rem; font-weight: 600; opacity: 0.85; }
	.total strong { font: 700 2.3rem/1 var(--display); letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
	.summary ul { list-style: none; margin: 0; padding: 18px 24px 0; display: grid; gap: 10px; font-size: 0.86rem; }
	.summary li { display: flex; justify-content: space-between; gap: 12px; }
	.summary li span:first-child { min-width: 0; }
	.amt { color: var(--muted); white-space: nowrap; font-variant-numeric: tabular-nums; }
	.summary .small { padding: 0 24px 22px; }

	footer { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; padding-top: 22px; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.8rem; }
	footer p { margin: 0; }
	.small-brand { font-size: 0.85rem; }
	.small-brand .logo { width: 26px; height: 26px; border-radius: 8px; }
	.small-brand .logo svg { width: 16px; height: 8px; }

	@media (max-width: 1000px) {
		.intro { grid-template-columns: 1fr; }
		.stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
		.details { grid-template-columns: 1fr; }
		.summary { position: static; }
	}
	@media (max-width: 640px) {
		nav { display: none; }
		.badge { margin-left: auto; }
	}
	@media (prefers-reduced-motion: reduce) {
		:global(*) { animation: none !important; transition: none !important; }
		:global(:root) { scroll-behavior: auto; }
	}
</style>

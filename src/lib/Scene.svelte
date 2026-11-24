<script>
	import { T, useTask, useThrelte } from '@threlte/core';
	import { OrbitControls, ContactShadows, interactivity } from '@threlte/extras';
	import * as THREE from 'three';
	import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
	import { finishes, hardware, cymbals, heads, leds, extras, cameraViews, byId } from './options.js';
	import { play } from './sound.js';

	/** @type {{ model: THREE.Object3D, config: any, view: string, groove: boolean, onhit?: (name: string) => void }} */
	let { model, config, view, groove, onhit } = $props();

	const { renderer, scene, invalidate } = useThrelte();
	interactivity();

	// ---------- Umgebungslicht (keine HDR-Datei noetig) ----------
	const pmrem = new THREE.PMREMGenerator(renderer);
	scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
	scene.environmentIntensity = 0.85;

	// ---------- Modell analysieren ----------
	const materials = {};
	const morphMeshes = [];
	model.traverse((o) => {
		if (o.isMesh) {
			o.castShadow = true;
			const mats = Array.isArray(o.material) ? o.material : [o.material];
			for (const m of mats) materials[m.name] = m;
			if (o.morphTargetDictionary) morphMeshes.push(o);
		}
	});
	const shell = materials['Shell_Finish'];
	const veneerMap = shell?.map ?? null; // Walnuss-Furnier-Textur aus Blender
	const sparkleNormal = shell?.normalMap ?? null;
	const mapleMap = materials['Shell_Inner_Maple']?.map ?? null;

	const node = (name) => model.getObjectByName(name);
	// Bones (Gelenke) mit ihrer Ruhelage merken
	const boneNames = ['Crash_Hoehe', 'Crash_Neigung', 'Ride_Hoehe', 'Ride_Neigung', 'HiHat_Offen', 'HiHat_Pedal', 'Fussmaschine_Schlaegel', 'Fussmaschine_Trittbrett'];
	const bones = {};
	for (const n of boneNames) {
		const b = node(n);
		if (b) bones[n] = { obj: b, pos: b.position.clone(), quat: b.quaternion.clone() };
	}
	model.updateMatrixWorld(true);
	// Neigungsachse: waagerecht, quer zum Galgen
	function tiltAxis(boneName, childName) {
		const pivot = new THREE.Vector3();
		const tip = new THREE.Vector3();
		node(boneName)?.getWorldPosition(pivot);
		node(childName)?.getWorldPosition(tip);
		const d = tip.sub(pivot).setY(0).normalize();
		return d.cross(new THREE.Vector3(0, 1, 0)).normalize();
	}
	const axes = { crash: tiltAxis('Crash_Neigung', 'Crash_Cymbal'), ride: tiltAxis('Ride_Neigung', 'Ride_Cymbal') };
	const X = new THREE.Vector3(1, 0, 0);

	// Becken, die beim Anschlagen wackeln
	const wobbleNames = { crash: 'Crash_Cymbal', crash2: 'Extra_Crash2_Cymbal', ride: 'Ride_Cymbal', hihat: 'HiHat_Top' };
	const wobble = {};
	for (const [k, n] of Object.entries(wobbleNames)) {
		const o = node(n);
		if (o) wobble[k] = { obj: o, quat: o.quaternion.clone(), t: -10 };
	}

	// ---------- Farbe & Material ----------
	$effect(() => {
		const f = byId(finishes, config.finish);
		shell.color.set(f.color);
		shell.metalness = f.metalness;
		shell.roughness = f.roughness;
		shell.map = f.wood ? mapleMap : f.texture ? veneerMap : null;
		shell.normalMap = f.sparkle ? sparkleNormal : null;
		if (shell.normalScale) shell.normalScale.setScalar(f.sparkle || 0);
		shell.clearcoat = 1;
		shell.clearcoatRoughness = f.wood ? 0.15 : 0.03;
		shell.needsUpdate = true;
		invalidate();
	});

	$effect(() => {
		const h = byId(hardware, config.hardware);
		const m = materials['Hardware_Metal'];
		m.color.set(h.color);
		m.roughness = h.roughness;
		m.metalness = h.metalness;
		const brass = materials['Badge_Brass'];
		if (brass) brass.color.set(config.hardware === 'gold' ? '#d8a050' : '#e8b860');
		invalidate();
	});

	$effect(() => {
		const c = byId(cymbals, config.cymbals);
		const m = materials['Cymbal_Pad'];
		m.color.set(c.color);
		m.roughness = c.roughness;
		invalidate();
	});

	$effect(() => {
		const h = byId(heads, config.heads);
		const m = materials['Drumhead'];
		m.map = null; // Farbe kommt aus der Auswahl, das Gewebe aus der Normal-Map
		m.color.set(h.color);
		m.roughness = h.roughness;
		m.needsUpdate = true;
		invalidate();
	});

	// ---------- LED-Farbe ----------
	const led = materials['LED_Glow'];
	let ledBase = 5;
	$effect(() => {
		const l = byId(leds, config.led);
		led.emissive.set(l.color);
		ledBase = l.off ? 0 : 5;
		led.emissiveIntensity = ledBase;
		invalidate();
	});

	// ---------- Ausstattung ----------
	$effect(() => {
		for (const e of extras) for (const n of e.objects) {
			const o = node(n);
			if (o) o.visible = !!config.extras[e.id];
		}
		invalidate();
	});

	// ---------- Morph Targets (weich überblenden) ----------
	const morphTarget = { Pad_Gross: 0, Kick_Gross: 0 };
	const morphNow = { ...morphTarget };
	$effect(() => {
		morphTarget.Pad_Gross = config.padSize;
		morphTarget.Kick_Gross = config.kickBig ? 1 : 0;
	});

	// ---------- Kamera ----------
	let camera = $state();
	let controls = $state();
	let fly = null;
	$effect(() => {
		const v = cameraViews.find((c) => c.id === view.split(':')[0]);
		if (!v || !camera || !controls) return;
		fly = {
			t: 0,
			fromPos: camera.position.clone(),
			fromTarget: controls.target.clone(),
			toPos: new THREE.Vector3(...v.position),
			toTarget: new THREE.Vector3(...v.target)
		};
	});

	// ---------- Anschlagen ----------
	const hits = { kick: -10, hihatPedal: -10 };
	let lastFlash = -10;
	function strike(name) {
		play(name, config);
		const now = performance.now() / 1000;
		if (name === 'kick') hits.kick = now;
		if (name === 'hihatOpen') hits.hihatPedal = now - 0.12;
		const w = wobble[name === 'hihatOpen' ? 'hihat' : name];
		if (w) w.t = now;
		lastFlash = now;
		onhit?.(name);
	}

	const prefixes = [
		['Extra_Crash2', 'crash2'], ['Kick', 'kick'], ['Fussmaschine', 'kick'],
		['Snare', 'snare'], ['Tom1', 'tom1'], ['Tom2', 'tom2'], ['Tom3', 'tom3'],
		['HiHat', 'hihat'], ['Crash', 'crash'], ['Ride', 'ride']
	];
	function instrumentOf(obj) {
		for (let o = obj; o; o = o.parent) {
			if (!o.visible) return null;
			const hit = prefixes.find(([p]) => o.name?.startsWith(p));
			if (hit) return hit[1];
		}
		return null;
	}
	function onclick(e) {
		if (e.delta > 6) return; // war eine Drehbewegung, kein Klick
		const hit = e.intersections.find((i) => instrumentOf(i.object));
		if (!hit) return;
		e.stopPropagation();
		strike(instrumentOf(hit.object));
	}
	function onpointermove(e) {
		const hit = e.intersections.find((i) => instrumentOf(i.object));
		document.body.style.cursor = hit ? 'pointer' : '';
	}
	function onpointerleave() {
		document.body.style.cursor = '';
	}

	// ---------- Groove (8tel-Rockbeat, 104 BPM) ----------
	const pattern = {
		kick: [1, 0, 0, 1, 1, 0, 0, 0],
		snare: [0, 0, 1, 0, 0, 0, 1, 0],
		hihat: [1, 1, 1, 1, 1, 1, 1, 0]
	};
	let step = 0;
	let nextStep = 0;
	let bar = 0;
	$effect(() => {
		if (groove) {
			step = 0;
			bar = 0;
			nextStep = performance.now() / 1000 + 0.05;
		}
	});

	const env = (dt, attack, decay) => (dt < 0 ? 0 : dt < attack ? dt / attack : Math.exp(-(dt - attack) / decay));
	const q = new THREE.Quaternion();
	const q2 = new THREE.Quaternion();

	useTask((delta) => {
		const now = performance.now() / 1000;

		// Groove-Sequenzer
		if (groove && now >= nextStep) {
			if (step === 0 && bar % 4 === 0) strike('crash');
			if (pattern.kick[step]) strike('kick');
			if (pattern.snare[step]) strike('snare');
			if (step === 7) strike(bar % 2 ? 'hihatOpen' : 'hihat');
			else if (pattern.hihat[step] && !(step === 0 && bar % 4 === 0)) strike('hihat');
			if (step === 7 && bar % 4 === 3) { strike('tom1'); }
			step = (step + 1) % 8;
			if (step === 0) bar++;
			nextStep += 60 / 104 / 2;
		}

		// Morph Targets überblenden
		const k = 1 - Math.exp(-delta * 9);
		for (const key in morphTarget) morphNow[key] += (morphTarget[key] - morphNow[key]) * k;
		for (const m of morphMeshes) {
			for (const [key, idx] of Object.entries(m.morphTargetDictionary)) {
				if (key in morphNow) m.morphTargetInfluences[idx] = morphNow[key];
			}
		}

		// Bones: Ständerhöhe, Galgenneigung, Hi-Hat, Fußmaschine
		const setBone = (name, dy, axis, angle, extraAxis, extraAngle) => {
			const b = bones[name];
			if (!b) return;
			b.obj.position.copy(b.pos);
			b.obj.position.y += dy;
			b.obj.quaternion.copy(b.quat);
			if (axis && angle) b.obj.quaternion.premultiply(q.setFromAxisAngle(axis, angle));
			if (extraAxis && extraAngle) b.obj.quaternion.premultiply(q2.setFromAxisAngle(extraAxis, extraAngle));
		};
		const deg = Math.PI / 180;
		setBone('Crash_Hoehe', config.crashHeight / 100);
		setBone('Crash_Neigung', 0, axes.crash, config.crashTilt * deg);
		setBone('Ride_Hoehe', config.rideHeight / 100);
		setBone('Ride_Neigung', 0, axes.ride, config.rideTilt * deg);

		// Hi-Hat: Regler öffnet dauerhaft, "offene" Schläge im Groove öffnen kurz und schließen wieder
		const dtp = now - hits.hihatPedal;
		const pulse = dtp < 0 ? 0 : dtp < 0.33 ? 1 : Math.max(0, 1 - (dtp - 0.33) / 0.06);
		const open = config.hihatOpen / 100;
		setBone('HiHat_Offen', open + 0.022 * pulse);
		setBone('HiHat_Pedal', 0, X, 0.09 * Math.min(1, pulse + open / 0.04));

		const kick = env(now - hits.kick, 0.045, 0.09);
		setBone('Fussmaschine_Schlaegel', 0, X, -0.42 * kick);
		setBone('Fussmaschine_Trittbrett', 0, X, -0.16 * kick);

		// LEDs blitzen beim Anschlagen kurz auf
		led.emissiveIntensity = ledBase * (1 + 1.6 * env(now - lastFlash, 0.01, 0.12));

		// Becken wackeln
		for (const w of Object.values(wobble)) {
			const dt = now - w.t;
			w.obj.quaternion.copy(w.quat);
			if (dt < 3) w.obj.quaternion.multiply(q.setFromAxisAngle(X, 0.06 * Math.sin(dt * 18) * Math.exp(-dt * 1.6)));
		}

		// Kamerafahrt
		if (fly && camera && controls) {
			fly.t = Math.min(1, fly.t + delta / 1.1);
			const s = fly.t < 0.5 ? 4 * fly.t ** 3 : 1 - (-2 * fly.t + 2) ** 3 / 2;
			camera.position.lerpVectors(fly.fromPos, fly.toPos, s);
			controls.target.lerpVectors(fly.fromTarget, fly.toTarget, s);
			controls.update();
			if (fly.t >= 1) fly = null;
		}
	});
</script>

<T.PerspectiveCamera makeDefault position={[1.3, 1.45, -1.9]} fov={36} near={0.05} far={60} bind:ref={camera}>
	<OrbitControls
		bind:ref={controls}
		target={[0, 0.62, 0.15]}
		enableDamping
		dampingFactor={0.08}
		minDistance={0.55}
		maxDistance={6}
		maxPolarAngle={Math.PI * 0.49}
		enablePan
		onstart={() => (fly = null)}
	/>
</T.PerspectiveCamera>

<T.DirectionalLight position={[2.5, 4, -2]} intensity={1.6} color="#fff1dc" />
<T.DirectionalLight position={[-3, 2.5, 2.5]} intensity={0.55} color="#b9c8ff" />
<T.SpotLight position={[0, 4.2, 0.4]} angle={0.55} penumbra={0.8} intensity={14} distance={9} color="#ffffff" />

<!-- Bühne -->
<T.Mesh rotation.x={-Math.PI / 2} position.y={-0.012}>
	<T.CircleGeometry args={[2.2, 96]} />
	<T.MeshStandardMaterial color="#e6e9ee" roughness={1} metalness={0} envMapIntensity={0.4} />
</T.Mesh>
<T.Mesh rotation.x={-Math.PI / 2} position.y={-0.011}>
	<T.RingGeometry args={[2.17, 2.2, 128]} />
	<T.MeshBasicMaterial color="#2a55e0" />
</T.Mesh>
<ContactShadows position.y={0.0} scale={4.4} blur={2.4} far={1.6} opacity={0.75} resolution={1024} />

<T is={model} {onclick} {onpointermove} {onpointerleave} />

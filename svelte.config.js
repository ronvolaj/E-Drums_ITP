import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		// Statische Seite: läuft auf GitHub Pages, Netlify, Vercel ...
		adapter: adapter({ fallback: undefined }),
		// Für GitHub Pages im Unterordner: BASE_PATH=/repo-name npm run build
		paths: { base: process.env.BASE_PATH ?? '', relative: true },
		// Alles JS/CSS direkt in index.html -> keine Pfadprobleme beim Hosten
		output: { bundleStrategy: 'inline' },
		router: { type: 'hash' }
	}
};
export default config;

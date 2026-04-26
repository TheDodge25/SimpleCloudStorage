<script>
	import { Search, Plus, Upload, FolderUp, FolderPlus, X } from 'lucide-svelte';

	let { onsearch, onnewfile, onnewfolderupload, onnewfolder } = $props();

	let query = $state('');
	let dropOpen = $state(false);
	let timer;

	function handleInput(e) {
		clearTimeout(timer);
		query = e.target.value;
		timer = setTimeout(() => onsearch?.(query), 280);
	}

	function pick(fn) { dropOpen = false; fn?.(); }
</script>

<header class="topbar">
	<a href="/drive" class="brand">
		<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true">
			<polygon points="11,1 21,19 1,19" fill="none" stroke="#4285f4" stroke-width="2.5" stroke-linejoin="round"/>
			<line x1="6" y1="19" x2="16" y2="19" stroke="#34a853" stroke-width="2.5" stroke-linecap="round"/>
			<line x1="11" y1="1" x2="16" y2="19" stroke="#fbbc04" stroke-width="2.5" stroke-linecap="round"/>
		</svg>
		<span>Drive</span>
	</a>

	<div class="search-bar">
		<Search size={18} />
		<input id="drive-search" type="search" placeholder="Search in Drive"
			value={query} oninput={handleInput} autocomplete="off" />
		{#if query}
			<button class="icon-btn" onclick={() => { query = ''; onsearch?.(''); }} aria-label="Clear">
				<X size={15} />
			</button>
		{/if}
	</div>

	<div class="new-wrap">
		<button id="new-btn" class="btn-primary" onclick={() => (dropOpen = !dropOpen)}
			aria-haspopup="true" aria-expanded={dropOpen}>
			<Plus size={18} /> New
		</button>
		{#if dropOpen}
			<div class="backdrop" onclick={() => (dropOpen = false)} role="none"></div>
			<menu class="dropdown animate-fade-in" id="new-dropdown">
				<li><button onclick={() => pick(onnewfile)}><Upload size={15} /> Upload file</button></li>
				<li><button onclick={() => pick(onnewfolderupload)}><FolderUp size={15} /> Upload folder</button></li>
				<li class="sep"></li>
				<li><button onclick={() => pick(onnewfolder)}><FolderPlus size={15} /> New folder</button></li>
			</menu>
		{/if}
	</div>
</header>

<style>
	.topbar {
		position: sticky; top: 0; z-index: 100;
		display: flex; align-items: center; gap: 1rem;
		padding: 0 1.25rem; height: 64px;
		background: var(--color-bg);
		border-bottom: 1px solid var(--color-border);
	}
	.brand {
		display: flex; align-items: center; gap: 0.5rem;
		font-size: 1.2rem; font-weight: 500; min-width: 160px; color: var(--color-text);
	}
	.search-bar {
		flex: 1; max-width: 580px; display: flex; align-items: center; gap: 0.625rem;
		background: var(--color-surface); border: 1px solid var(--color-border);
		border-radius: 2rem; padding: 0.5rem 1rem;
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	.search-bar:focus-within {
		border-color: var(--color-primary); box-shadow: 0 0 0 2px #4285f420;
		background: var(--color-surface-alt);
	}
	.search-bar :global(svg) { color: var(--color-text-muted); flex-shrink: 0; }
	input[type="search"] {
		flex: 1; background: none; border: none; outline: none;
		color: var(--color-text); font: inherit; font-size: 0.9375rem;
	}
	input::-webkit-search-cancel-button { display: none; }
	.icon-btn { background: none; border: none; color: var(--color-text-muted); cursor: pointer; display: flex; padding: 0; }
	.icon-btn:hover { color: var(--color-text); }
	.new-wrap { position: relative; margin-left: auto; }
	.backdrop { position: fixed; inset: 0; z-index: 10; }
	.dropdown {
		position: absolute; top: calc(100% + 6px); right: 0; z-index: 20;
		min-width: 200px; background: var(--color-surface-alt);
		border: 1px solid var(--color-border); border-radius: var(--radius-md);
		padding: 0.375rem; list-style: none; margin: 0;
		box-shadow: 0 8px 24px #00000060;
	}
	.dropdown li button {
		display: flex; align-items: center; gap: 0.75rem; width: 100%;
		padding: 0.5rem 0.75rem; background: none; border: none;
		color: var(--color-text); cursor: pointer; border-radius: var(--radius-sm);
		font: inherit; font-size: 0.875rem; transition: background 0.1s;
	}
	.dropdown li button:hover { background: var(--color-surface); }
	.sep { height: 1px; background: var(--color-border); margin: 0.25rem 0; }
</style>

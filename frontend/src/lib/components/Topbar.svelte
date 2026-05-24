<script>
	import { Search, Plus, Upload, FolderUp, FolderPlus, X, LogOut, Settings } from 'lucide-svelte';
	import { page } from '$app/stores';

	let { onsearch, onnewfile, onnewfolderupload, onnewfolder } = $props();

	let query = $state('');
	let dropOpen = $state(false);
	let profileOpen = $state(false);
	let timer;

	const user = $derived($page.data.user);

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

	<div class="actions">
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

		{#if user}
		<div class="profile-wrap">
			<button class="profile-btn" onclick={() => (profileOpen = !profileOpen)} aria-label="Profile">
				<div class="avatar">{user.username[0].toUpperCase()}</div>
			</button>
			{#if profileOpen}
				<div class="backdrop" onclick={() => (profileOpen = false)} role="none"></div>
				<menu class="dropdown profile-dropdown animate-fade-in">
					<li class="profile-header">
						<strong>{user.username}</strong>
						<span>{user.email}</span>
					</li>
					<li class="sep"></li>
					{#if user.role === 'admin'}
					<li><a href="/admin" class="dropdown-link" onclick={() => (profileOpen = false)}><Settings size={15} /> Admin Panel</a></li>
					{/if}
					<li>
						<form action="/login?/logout" method="POST">
							<button type="submit" class="dropdown-link text-danger"><LogOut size={15} /> Log out</button>
						</form>
					</li>
				</menu>
			{/if}
		</div>
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
	
	.actions { display: flex; align-items: center; gap: 1rem; margin-left: auto; }
	.new-wrap, .profile-wrap { position: relative; }
	.backdrop { position: fixed; inset: 0; z-index: 10; }
	
	.profile-btn {
		background: none; border: none; padding: 0; cursor: pointer;
		border-radius: 50%; overflow: hidden;
		transition: opacity 0.2s;
	}
	.profile-btn:hover { opacity: 0.8; }
	.avatar {
		width: 36px; height: 36px; border-radius: 50%;
		background: var(--color-primary); color: white;
		display: flex; align-items: center; justify-content: center;
		font-weight: 600; font-size: 1.1rem;
	}
	
	.dropdown {
		position: absolute; top: calc(100% + 6px); right: 0; z-index: 20;
		min-width: 200px; background: var(--color-surface-alt);
		border: 1px solid var(--color-border); border-radius: var(--radius-md);
		padding: 0.375rem; list-style: none; margin: 0;
		box-shadow: 0 8px 24px #00000060;
	}
	.dropdown li button, .dropdown-link {
		display: flex; align-items: center; gap: 0.75rem; width: 100%;
		padding: 0.5rem 0.75rem; background: none; border: none;
		color: var(--color-text); cursor: pointer; border-radius: var(--radius-sm);
		font: inherit; font-size: 0.875rem; transition: background 0.1s; text-decoration: none;
	}
	.dropdown li button:hover, .dropdown-link:hover { background: var(--color-surface); }
	.profile-dropdown { min-width: 220px; }
	.profile-header { padding: 0.75rem; display: flex; flex-direction: column; }
	.profile-header strong { font-size: 0.95rem; color: var(--color-text); }
	.profile-header span { font-size: 0.8rem; color: var(--color-text-muted); }
	.text-danger { color: #ea4335 !important; }
	.sep { height: 1px; background: var(--color-border); margin: 0.25rem 0; }
</style>

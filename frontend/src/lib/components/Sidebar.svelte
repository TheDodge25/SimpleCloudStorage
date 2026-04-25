<script>
	import { HardDrive, Clock, Trash2 } from 'lucide-svelte';
	import { page } from '$app/stores';

	const navItems = [
		{ href: '/drive', icon: HardDrive, label: 'My Drive' },
		{ href: '/drive?recent=1', icon: Clock, label: 'Recent' },
		{ href: '/drive?trash=1', icon: Trash2, label: 'Trash' }
	];
</script>

<aside class="sidebar">
	<nav class="nav">
		{#each navItems as item}
			<a
				href={item.href}
				class="nav-item"
				class:active={$page.url.pathname === '/drive' && item.href === '/drive'}
				aria-current={$page.url.pathname === '/drive' && item.href === '/drive' ? 'page' : undefined}
			>
				<svelte:component this={item.icon} size={20} />
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="storage">
		<div class="storage-label">
			<span>Storage</span>
			<span class="storage-used">— GB used</span>
		</div>
		<div class="storage-bar" role="meter" aria-label="Storage usage">
			<div class="storage-fill" style="width: 0%"></div>
		</div>
		<p class="storage-sub">Storage tracking coming soon</p>
	</div>
</aside>

<style>
	.sidebar {
		width: 240px;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		padding: 0.75rem 0;
		border-right: 1px solid var(--color-border);
		height: calc(100vh - 64px);
		position: sticky;
		top: 64px;
		overflow-y: auto;
	}
	.nav { display: flex; flex-direction: column; gap: 2px; padding: 0 0.75rem; }
	.nav-item {
		display: flex; align-items: center; gap: 0.875rem;
		padding: 0.625rem 0.875rem;
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
		font-size: 0.875rem; font-weight: 500;
		transition: background 0.12s, color 0.12s;
	}
	.nav-item:hover { background: var(--color-surface-alt); color: var(--color-text); }
	.nav-item.active { background: #4285f420; color: var(--color-primary); }
	.storage {
		margin-top: auto;
		padding: 1rem 1.25rem;
		border-top: 1px solid var(--color-border);
	}
	.storage-label {
		display: flex; justify-content: space-between;
		font-size: 0.75rem; color: var(--color-text-muted); margin-bottom: 0.5rem;
	}
	.storage-used { color: var(--color-text-faint); }
	.storage-bar {
		height: 4px; background: var(--color-border);
		border-radius: 2px; overflow: hidden;
	}
	.storage-fill { height: 100%; background: var(--color-primary); border-radius: 2px; }
	.storage-sub { font-size: 0.7rem; color: var(--color-text-faint); margin: 0.375rem 0 0; }
</style>

<script>
	import { ChevronRight, HardDrive } from 'lucide-svelte';

	/** @type {{ id: string, name: string }[]} */
	let { crumbs = [] } = $props();
</script>

<nav class="breadcrumb" aria-label="Folder path">
	<a href="/drive" class="crumb root" aria-label="My Drive">
		<HardDrive size={16} />
		<span>My Drive</span>
	</a>

	{#each crumbs as crumb, i}
		<ChevronRight size={14} class="sep" />
		{#if i === crumbs.length - 1}
			<span class="crumb current" aria-current="page">{crumb.name}</span>
		{:else}
			<a href="/drive/{crumb.id}" class="crumb">{crumb.name}</a>
		{/if}
	{/each}
</nav>

<style>
	.breadcrumb {
		display: flex; align-items: center; gap: 0.125rem;
		padding: 0.625rem 1.25rem;
		font-size: 0.875rem; color: var(--color-text-muted);
	}
	.crumb {
		display: flex; align-items: center; gap: 0.375rem;
		padding: 0.25rem 0.5rem; border-radius: var(--radius-sm);
		color: var(--color-text-muted);
		transition: background 0.12s, color 0.12s;
		white-space: nowrap;
	}
	.crumb:hover { background: var(--color-surface-alt); color: var(--color-text); }
	.crumb.current { color: var(--color-text); font-weight: 500; pointer-events: none; }
	:global(.sep) { color: var(--color-text-faint); flex-shrink: 0; }
</style>

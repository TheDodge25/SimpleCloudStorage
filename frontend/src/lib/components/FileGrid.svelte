<script>
	import { ArrowUp, ArrowDown, LayoutGrid, List } from 'lucide-svelte';
	import FolderCard from './FolderCard.svelte';
	import FileRow from './FileRow.svelte';
	import { sortState, cycleSort } from '$lib/stores.js';

	let { folders = [], files = [], oncontextmenu, loading = false } = $props();

	let viewMode = $state('grid'); // 'grid' | 'list'

	const sortedFolders = $derived(
		[...folders].sort((a, b) => {
			const dir = $sortState.dir === 'asc' ? 1 : -1;
			if ($sortState.field === 'name') return dir * a.name.localeCompare(b.name);
			if ($sortState.field === 'date') return dir * (new Date(a.created_date) - new Date(b.created_date));
			return 0;
		})
	);

	const sortedFiles = $derived(
		[...files].sort((a, b) => {
			const dir = $sortState.dir === 'asc' ? 1 : -1;
			if ($sortState.field === 'name') return dir * a.original_name.localeCompare(b.original_name);
			if ($sortState.field === 'date') return dir * (new Date(a.upload_date) - new Date(b.upload_date));
			if ($sortState.field === 'size') return dir * (a.size - b.size);
			return 0;
		})
	);

	function SortIcon(field) {
		if ($sortState.field !== field) return null;
		return $sortState.dir === 'asc' ? ArrowUp : ArrowDown;
	}
</script>

<div class="grid-wrap">
	<div class="toolbar">
		<div class="sort-btns">
			{#each [['name','Name'],['date','Modified'],['size','Size']] as [field, label]}
				<button class="sort-btn" class:active={$sortState.field === field} onclick={() => cycleSort(field)}>
					{label}
					{#if $sortState.field === field}
						<svelte:component this={SortIcon(field)} size={13} />
					{/if}
				</button>
			{/each}
		</div>
		<div class="view-btns">
			<button class="icon-btn" class:active={viewMode==='grid'} onclick={() => (viewMode='grid')} aria-label="Grid view"><LayoutGrid size={18}/></button>
			<button class="icon-btn" class:active={viewMode==='list'} onclick={() => (viewMode='list')} aria-label="List view"><List size={18}/></button>
		</div>
	</div>

	{#if loading}
		<div class="skeleton-wrap">
			{#each Array(8) as _}<div class="skeleton"></div>{/each}
		</div>
	{:else if sortedFolders.length === 0 && sortedFiles.length === 0}
		<div class="empty animate-fade-in">
			<p>This folder is empty</p>
			<p class="hint">Drop files here or use the New button to add content</p>
		</div>
	{:else}
		{#if sortedFolders.length > 0}
			<p class="section-label">Folders</p>
			<div class="grid" class:list={viewMode === 'list'}>
				{#each sortedFolders as folder (folder.id)}
					<FolderCard {folder} {oncontextmenu} />
				{/each}
			</div>
		{/if}
		{#if sortedFiles.length > 0}
			<p class="section-label">Files</p>
			<div class="file-list">
				{#each sortedFiles as file (file.id)}
					<FileRow {file} {oncontextmenu} />
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.grid-wrap { flex: 1; display: flex; flex-direction: column; overflow: auto; }
	.toolbar { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 1.25rem; border-bottom: 1px solid var(--color-border); }
	.sort-btns { display: flex; gap: 0.25rem; }
	.sort-btn {
		display: flex; align-items: center; gap: 0.25rem;
		padding: 0.25rem 0.625rem; background: none; border: none;
		color: var(--color-text-muted); cursor: pointer; border-radius: var(--radius-sm);
		font: inherit; font-size: 0.8125rem; transition: background 0.12s, color 0.12s;
	}
	.sort-btn:hover, .sort-btn.active { background: var(--color-surface-alt); color: var(--color-text); }
	.view-btns { display: flex; gap: 0.25rem; }
	.icon-btn { background: none; border: none; color: var(--color-text-muted); cursor: pointer; padding: 0.375rem; border-radius: var(--radius-sm); display: flex; transition: background 0.12s, color 0.12s; }
	.icon-btn:hover, .icon-btn.active { background: var(--color-surface-alt); color: var(--color-text); }
	.section-label { margin: 0.875rem 1.25rem 0.375rem; font-size: 0.75rem; font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
	.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.5rem; padding: 0 1rem 0.5rem; }
	.grid.list { grid-template-columns: 1fr; }
	.file-list { display: flex; flex-direction: column; gap: 2px; padding: 0 1rem 1rem; }
	.empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.375rem; color: var(--color-text-muted); padding: 4rem; text-align: center; }
	.empty p { margin: 0; font-size: 0.9375rem; }
	.hint { color: var(--color-text-faint) !important; font-size: 0.8125rem !important; }
	.skeleton-wrap { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.5rem; padding: 1rem; }
	.skeleton { height: 120px; border-radius: var(--radius-md); background: var(--color-surface); animation: pulse 1.4s ease-in-out infinite; }
	@keyframes pulse { 0%,100%{opacity:.4} 50%{opacity:.8} }
</style>

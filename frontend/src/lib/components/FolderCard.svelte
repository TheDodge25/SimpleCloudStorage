<script>
	import { Folder } from 'lucide-svelte';
	import { selected, toggleSelect } from '$lib/stores.js';

	/** @type {{ id: string, name: string, oncontextmenu?: (e: MouseEvent, item: object) => void }} */
	let { folder, oncontextmenu } = $props();

	let isSelected = $derived($selected.has(folder.id));
</script>

<a
	href="/drive/{folder.id}"
	id="folder-{folder.id}"
	class="folder-card card"
	class:selected={isSelected}
	onclick={(e) => { if (e.ctrlKey || e.metaKey || e.shiftKey) { e.preventDefault(); toggleSelect(folder.id, e); } }}
	oncontextmenu={(e) => { e.preventDefault(); oncontextmenu?.(e, { ...folder, type: 'folder' }); }}
	draggable="false"
>
	<Folder size={40} fill="#4285f420" color="#4285f4" />
	<span class="name" title={folder.name}>{folder.name}</span>
</a>

<style>
	.folder-card {
		display: flex; flex-direction: column; align-items: center; justify-content: center;
		gap: 0.625rem; padding: 1.25rem 0.75rem;
		text-align: center; cursor: pointer; text-decoration: none;
		color: var(--color-text);
	}
	.name {
		font-size: 0.8125rem; font-weight: 500;
		width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
	}
</style>

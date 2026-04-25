<script>
	import { Download, Trash2 } from 'lucide-svelte';
	import { selected, clearSelection } from '$lib/stores.js';
	import { getDownloadUrl } from '$lib/api.js';

	/** @type {{ x: number, y: number, item: object } | null} */
	let { menu = null, ondelete } = $props();

	const isMulti = $derived($selected.size > 1);
	const label = $derived(isMulti ? `${$selected.size} items` : menu?.item?.original_name ?? menu?.item?.name ?? '');

	function download() {
		if (menu?.item?.type === 'file') window.open(getDownloadUrl(menu.item.id));
	}

	async function del() {
		if (!menu) return;
		const ids = isMulti ? [...$selected] : [menu.item.id];
		const types = isMulti ? null : menu.item.type;
		await ondelete?.(ids, types);
		clearSelection();
	}
</script>

{#if menu}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="backdrop" onclick={clearSelection} role="none"></div>
	<menu class="ctx animate-fade-in" id="context-menu"
		style="left:{menu.x}px; top:{menu.y}px" role="menu">
		<li class="ctx-label" role="none">{label}</li>
		{#if !isMulti && menu.item?.type === 'file'}
			<li role="none">
				<button role="menuitem" onclick={download}><Download size={15}/> Download</button>
			</li>
		{/if}
		<li role="none">
			<button role="menuitem" class="danger" onclick={del}>
				<Trash2 size={15}/> Delete{isMulti ? ` (${$selected.size})` : ''}
			</button>
		</li>
	</menu>
{/if}

<style>
	.backdrop { position: fixed; inset: 0; z-index: 200; }
	.ctx {
		position: fixed; z-index: 201;
		min-width: 180px; background: var(--color-surface-alt);
		border: 1px solid var(--color-border); border-radius: var(--radius-md);
		padding: 0.375rem; list-style: none; margin: 0;
		box-shadow: 0 8px 24px #00000070;
	}
	.ctx-label {
		padding: 0.25rem 0.75rem;
		font-size: 0.75rem; color: var(--color-text-faint);
		overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 200px;
	}
	.ctx button {
		display: flex; align-items: center; gap: 0.625rem; width: 100%;
		padding: 0.5rem 0.75rem; background: none; border: none;
		color: var(--color-text); cursor: pointer; border-radius: var(--radius-sm);
		font: inherit; font-size: 0.875rem; transition: background 0.1s;
	}
	.ctx button:hover { background: var(--color-surface); }
	.ctx button.danger { color: var(--color-danger); }
	.ctx button.danger:hover { background: #ea433520; }
</style>

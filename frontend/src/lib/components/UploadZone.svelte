<script>
	/**
	 * Wraps the content area. Intercepts drag-drop anywhere inside
	 * and fires onfiles(FileList, folderId).
	 */
	let { children, folderId = null, onfiles } = $props();

	let dragging = $state(false);
	let depth = 0; // track enter/leave on nested elements

	function onDragEnter(e) { e.preventDefault(); depth++; dragging = true; }
	function onDragLeave()  { depth--; if (depth === 0) dragging = false; }
	function onDragOver(e)  { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; }

	function onDrop(e) {
		e.preventDefault();
		depth = 0; dragging = false;
		const files = e.dataTransfer?.files;
		if (files?.length) onfiles?.(files, folderId);
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class="zone"
	class:dragging
	role="region"
	aria-label="File drop zone"
	ondragenter={onDragEnter}
	ondragleave={onDragLeave}
	ondragover={onDragOver}
	ondrop={onDrop}
>
	{@render children?.()}
	{#if dragging}
		<div class="drop-overlay animate-fade-in">
			<div class="drop-inner">
				<p class="drop-title">Drop to upload</p>
				<p class="drop-sub">Files will be added to the current folder</p>
			</div>
		</div>
	{/if}
</div>

<style>
	.zone { position: relative; flex: 1; display: flex; flex-direction: column; }
	.drop-overlay {
		position: absolute; inset: 0; z-index: 50;
		background: #4285f418; border: 2px dashed var(--color-primary);
		border-radius: var(--radius-md); display: flex;
		align-items: center; justify-content: center;
		pointer-events: none;
	}
	.drop-inner { text-align: center; }
	.drop-title { margin: 0; font-size: 1.125rem; font-weight: 600; color: var(--color-primary); }
	.drop-sub   { margin: 0.375rem 0 0; font-size: 0.875rem; color: var(--color-text-muted); }
</style>

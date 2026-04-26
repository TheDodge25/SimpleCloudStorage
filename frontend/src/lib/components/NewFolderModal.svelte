<script>
	import { FolderPlus, X } from 'lucide-svelte';

	let { open = false, oncreate, onclose } = $props();
	let name = $state('');
	let error = $state('');
	let busy = $state(false);

	async function submit() {
		if (!name.trim()) { error = 'Name is required'; return; }
		busy = true; error = '';
		try {
			await oncreate?.(name.trim());
			name = '';
			onclose?.();
		} catch (e) {
			error = e.message ?? 'Failed to create folder';
		} finally {
			busy = false;
		}
	}

	function onkeydown(e) { if (e.key === 'Enter') submit(); }
</script>

{#if open}
	<div class="overlay" onclick={onclose} role="none"></div>
	<dialog class="modal animate-slide-up card" aria-labelledby="modal-title" open>
		<div class="modal-head">
			<FolderPlus size={20} color="var(--color-primary)" />
			<h2 id="modal-title">New folder</h2>
			<button class="close-btn" onclick={onclose} aria-label="Close"><X size={18}/></button>
		</div>

		<input
			id="folder-name-input"
			type="text"
			placeholder="Folder name"
			bind:value={name}
			{onkeydown}
			autofocus
			class="name-input"
			class:error={!!error}
		/>
		{#if error}<p class="err-msg">{error}</p>{/if}

		<div class="modal-actions">
			<button class="btn-ghost" onclick={onclose} disabled={busy}>Cancel</button>
			<button class="btn-primary" onclick={submit} disabled={busy || !name.trim()}>
				{busy ? 'Creating…' : 'Create'}
			</button>
		</div>
	</dialog>
{/if}

<style>
	.overlay { position: fixed; inset: 0; z-index: 300; background: #00000050; backdrop-filter: blur(2px); }
	.modal {
		position: fixed; z-index: 301;
		top: 50%; left: 50%; transform: translate(-50%, -50%);
		width: min(380px, 90vw); padding: 1.25rem; border: none;
		display: flex; flex-direction: column; gap: 1rem;
	}
	.modal-head { display: flex; align-items: center; gap: 0.625rem; }
	h2 { margin: 0; font-size: 1rem; font-weight: 600; flex: 1; color: var(--color-text); }
	.close-btn { background: none; border: none; color: var(--color-text-muted); cursor: pointer; display: flex; padding: 0; }
	.name-input {
		background: var(--color-surface); border: 1px solid var(--color-border);
		border-radius: var(--radius-sm); padding: 0.625rem 0.875rem;
		color: var(--color-text); font: inherit; font-size: 0.9375rem; outline: none;
		transition: border-color 0.15s;
	}
	.name-input:focus { border-color: var(--color-primary); box-shadow: 0 0 0 2px #4285f420; }
	.name-input.error { border-color: var(--color-danger); }
	.err-msg { margin: -0.5rem 0 0; font-size: 0.8125rem; color: var(--color-danger); }
	.modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; }
</style>

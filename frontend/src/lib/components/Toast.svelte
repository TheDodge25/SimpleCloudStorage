<script>
	import { toasts } from '$lib/stores.js';
	import { CheckCircle, XCircle, Info, X } from 'lucide-svelte';

	const icons = { success: CheckCircle, error: XCircle, info: Info };
	const colors = {
		success: 'var(--color-success)',
		error:   'var(--color-danger)',
		info:    'var(--color-primary)'
	};
</script>

<div class="toast-stack">
	{#each $toasts as toast (toast.id)}
		<div class="toast animate-slide-up" style="--accent:{colors[toast.type]}">
			<svelte:component this={icons[toast.type]} size={16} color={colors[toast.type]} />
			<span>{toast.message}</span>
			<button
				class="dismiss"
				onclick={() => toasts.update((t) => t.filter((x) => x.id !== toast.id))}
				aria-label="Dismiss"
			>
				<X size={14} />
			</button>
		</div>
	{/each}
</div>

<style>
	.toast-stack {
		position: fixed;
		top: 1rem;
		right: 1rem;
		z-index: 9999;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		pointer-events: none;
	}
	.toast {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.625rem 0.875rem;
		background: var(--color-surface-alt);
		border: 1px solid var(--accent);
		border-radius: var(--radius-sm);
		color: var(--color-text);
		font-size: 0.875rem;
		box-shadow: 0 4px 16px #00000060;
		pointer-events: all;
		min-width: 240px;
		max-width: 360px;
	}
	.toast span { flex: 1; }
	.dismiss {
		background: none;
		border: none;
		color: var(--color-text-faint);
		cursor: pointer;
		padding: 0;
		display: flex;
	}
	.dismiss:hover { color: var(--color-text); }
</style>

<script>
	import { X, CheckCircle, AlertCircle } from 'lucide-svelte';

	/** @type {{ id: string, name: string, progress: number, status: 'uploading'|'done'|'error' }[]} */
	let { uploads = [], onclear } = $props();

	const visible = $derived(uploads.length > 0);
</script>

{#if visible}
	<div class="panel animate-slide-up" id="upload-progress-panel" role="status" aria-live="polite">
		<div class="panel-head">
			<span class="panel-title">Uploading {uploads.length} file{uploads.length > 1 ? 's' : ''}</span>
			{#if uploads.every(u => u.status !== 'uploading')}
				<button class="icon-btn" onclick={onclear} aria-label="Dismiss"><X size={16}/></button>
			{/if}
		</div>

		<ul class="upload-list">
			{#each uploads as u (u.id)}
				<li class="upload-item">
					<span class="upload-name" title={u.name}>{u.name}</span>
					{#if u.status === 'uploading'}
						<div class="progress-track" role="progressbar" aria-valuenow={Math.round(u.progress * 100)} aria-valuemin="0" aria-valuemax="100">
							<div class="progress-fill" style="width:{u.progress * 100}%"></div>
						</div>
						<span class="pct">{Math.round(u.progress * 100)}%</span>
					{:else if u.status === 'done'}
						<CheckCircle size={16} color="var(--color-success)" />
					{:else}
						<AlertCircle size={16} color="var(--color-danger)" />
					{/if}
				</li>
			{/each}
		</ul>
	</div>
{/if}

<style>
	.panel {
		position: fixed; bottom: 1.25rem; right: 1.25rem; z-index: 400;
		width: 320px; background: var(--color-surface-alt);
		border: 1px solid var(--color-border); border-radius: var(--radius-md);
		box-shadow: 0 8px 24px #00000060; overflow: hidden;
	}
	.panel-head { display: flex; align-items: center; padding: 0.75rem 1rem; border-bottom: 1px solid var(--color-border); }
	.panel-title { flex: 1; font-size: 0.875rem; font-weight: 600; color: var(--color-text); }
	.icon-btn { background: none; border: none; color: var(--color-text-muted); cursor: pointer; display: flex; padding: 0; }
	.upload-list { list-style: none; margin: 0; padding: 0.5rem; max-height: 240px; overflow-y: auto; }
	.upload-item {
		display: grid; grid-template-columns: 1fr auto auto; align-items: center;
		gap: 0.5rem; padding: 0.375rem 0.5rem; border-radius: var(--radius-sm);
	}
	.upload-item:hover { background: var(--color-surface); }
	.upload-name { font-size: 0.8125rem; color: var(--color-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.progress-track { width: 60px; height: 4px; background: var(--color-border); border-radius: 2px; overflow: hidden; }
	.progress-fill { height: 100%; background: var(--color-primary); border-radius: 2px; transition: width 0.1s; }
	.pct { font-size: 0.75rem; color: var(--color-text-muted); min-width: 2.5rem; text-align: right; }
</style>

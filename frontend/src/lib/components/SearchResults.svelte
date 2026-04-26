<script>
	import { FileText, X } from 'lucide-svelte';
	import { getDownloadUrl } from '$lib/api.js';

	let { results = [], query = '', onclose } = $props();

	function fmtSize(bytes) {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
	}
</script>

{#if query}
	<div class="overlay animate-fade-in" role="none" onclick={onclose}></div>
	<div class="panel animate-slide-up card" id="search-results" role="region" aria-label="Search results">
		<div class="panel-head">
			<span class="panel-title">Results for "<strong>{query}</strong>"</span>
			<span class="count">{results.length} file{results.length !== 1 ? 's' : ''}</span>
			<button class="icon-btn" onclick={onclose} aria-label="Close search"><X size={16}/></button>
		</div>

		{#if results.length === 0}
			<p class="empty">No files match your search</p>
		{:else}
			<ul class="result-list" role="list">
				{#each results as file (file.id)}
					<li role="listitem">
						<a
							href={getDownloadUrl(file.id)}
							class="result-item"
							target="_blank"
							rel="noopener noreferrer"
							title={file.original_name}
						>
							<FileText size={18} color="var(--color-primary)" />
							<span class="result-name">{file.original_name}</span>
							<span class="result-size">{fmtSize(file.size)}</span>
						</a>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
{/if}

<style>
	.overlay { position: fixed; inset: 0; z-index: 150; }
	.panel {
		position: fixed; top: 72px; left: 50%; transform: translateX(-50%);
		z-index: 151; width: min(560px, 90vw); max-height: 60vh;
		display: flex; flex-direction: column; overflow: hidden;
	}
	.panel-head { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; border-bottom: 1px solid var(--color-border); }
	.panel-title { flex: 1; font-size: 0.875rem; color: var(--color-text-muted); }
	.panel-title strong { color: var(--color-text); }
	.count { font-size: 0.75rem; color: var(--color-text-faint); }
	.icon-btn { background: none; border: none; color: var(--color-text-muted); cursor: pointer; display: flex; padding: 0; }
	.result-list { list-style: none; margin: 0; padding: 0.375rem; overflow-y: auto; }
	.result-item {
		display: flex; align-items: center; gap: 0.75rem;
		padding: 0.5rem 0.75rem; border-radius: var(--radius-sm);
		color: var(--color-text); text-decoration: none;
		transition: background 0.1s;
	}
	.result-item:hover { background: var(--color-surface-alt); }
	.result-name { flex: 1; font-size: 0.875rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.result-size { font-size: 0.8125rem; color: var(--color-text-muted); white-space: nowrap; }
	.empty { padding: 2rem; text-align: center; color: var(--color-text-muted); font-size: 0.9rem; margin: 0; }
</style>

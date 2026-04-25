<script>
	import { FileText, Image, Film, Music, Archive, FileCode, File } from 'lucide-svelte';
	import { selected, toggleSelect } from '$lib/stores.js';
	import { getDownloadUrl } from '$lib/api.js';

	let { file, oncontextmenu } = $props();
	let isSelected = $derived($selected.has(file.id));

	const MIME_ICONS = {
		'image/':       { icon: Image,    color: '#34a853' },
		'video/':       { icon: Film,     color: '#ea4335' },
		'audio/':       { icon: Music,    color: '#fbbc04' },
		'text/':        { icon: FileText, color: '#4285f4' },
		'application/zip':    { icon: Archive,  color: '#ff7043' },
		'application/x-zip':  { icon: Archive,  color: '#ff7043' },
		'application/json':   { icon: FileCode, color: '#ab47bc' },
		'application/pdf':    { icon: FileText, color: '#ea4335' },
	};

	function getIcon(mime) {
		for (const [prefix, meta] of Object.entries(MIME_ICONS)) {
			if (mime?.startsWith(prefix)) return meta;
		}
		return { icon: File, color: 'var(--color-text-muted)' };
	}

	function fmtSize(bytes) {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
		if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
		return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
	}

	function fmtDate(iso) {
		return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	const { icon: IconComponent, color } = $derived(getIcon(file.content_type));
</script>

<div
	id="file-{file.id}"
	class="file-row card"
	class:selected={isSelected}
	role="row"
	onclick={(e) => toggleSelect(file.id, e)}
	ondblclick={() => window.open(getDownloadUrl(file.id))}
	oncontextmenu={(e) => { e.preventDefault(); oncontextmenu?.(e, { ...file, type: 'file' }); }}
	tabindex="0"
>
	<span class="icon"><svelte:component this={IconComponent} size={20} {color} /></span>
	<span class="name" title={file.original_name}>{file.original_name}</span>
	<span class="meta">{fmtDate(file.upload_date)}</span>
	<span class="meta">{fmtSize(file.size)}</span>
</div>

<style>
	.file-row {
		display: grid;
		grid-template-columns: 2rem 1fr 9rem 7rem;
		align-items: center; gap: 0.75rem;
		padding: 0.5rem 1rem;
		border-radius: var(--radius-sm);
		cursor: pointer; user-select: none;
	}
	.name { font-size: 0.875rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.meta { font-size: 0.8125rem; color: var(--color-text-muted); white-space: nowrap; }
</style>

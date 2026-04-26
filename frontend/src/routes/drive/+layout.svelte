<script>
	import { uploadFile, createFolder, deleteFile, deleteFolder, search } from '$lib/api.js';
	import { addToast, clearSelection } from '$lib/stores.js';
	import Topbar from '$lib/components/Topbar.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import NewFolderModal from '$lib/components/NewFolderModal.svelte';
	import ContextMenu from '$lib/components/ContextMenu.svelte';
	import SearchResults from '$lib/components/SearchResults.svelte';
	import UploadProgress from '$lib/components/UploadProgress.svelte';
	import { invalidateAll } from '$app/navigation';
	import { page } from '$app/stores';

	let { children } = $props();

	let modalOpen = $state(false);
	let ctxMenu = $state(null);
	let searchQuery = $state('');
	let searchResults = $state([]);
	let uploads = $state([]);

	const folderId = $derived($page.params.folderId ?? null);

	// ── File inputs (hidden) ────────────────────────────────────────────────
	let fileInput;
	let folderInput;

	async function handleFiles(fileList, folder) {
		const files = [...fileList];
		const newUploads = files.map((f) => ({ id: crypto.randomUUID(), name: f.name, progress: 0, status: 'uploading' }));
		uploads = [...uploads, ...newUploads];
		await Promise.all(
			files.map((file, i) =>
				uploadFile(file, folder, (pct) => {
					uploads = uploads.map((u) => (u.id === newUploads[i].id ? { ...u, progress: pct } : u));
				})
					.then(() => { uploads = uploads.map((u) => (u.id === newUploads[i].id ? { ...u, status: 'done' } : u)); })
					.catch(() => { uploads = uploads.map((u) => (u.id === newUploads[i].id ? { ...u, status: 'error' } : u)); addToast('error', `Failed to upload ${file.name}`); })
			)
		);
		await invalidateAll();
		addToast('success', `${files.length} file${files.length > 1 ? 's' : ''} uploaded`);
	}

	async function handleSearch(q) {
		searchQuery = q;
		if (!q.trim()) { searchResults = []; return; }
		try { searchResults = await search(q, null); }
		catch { searchResults = []; }
	}

	async function handleCreate(name) {
		await createFolder({ name, parent_id: folderId });
		await invalidateAll();
		addToast('success', `Folder "${name}" created`);
	}

	async function handleDelete(ids, type) {
		if (!confirm(`Delete ${ids.length} item${ids.length > 1 ? 's' : ''}? This cannot be undone.`)) return;
		ctxMenu = null;
		await Promise.all(ids.map((id) => (type === 'file' ? deleteFile(id) : deleteFolder(id))));
		clearSelection();
		await invalidateAll();
		addToast('success', 'Deleted');
	}
</script>

<input bind:this={fileInput} type="file" multiple hidden onchange={(e) => handleFiles(e.target.files, folderId)} />
<input bind:this={folderInput} type="file" webkitdirectory multiple hidden onchange={(e) => handleFiles(e.target.files, folderId)} />

<div class="drive-layout">
	<Topbar
		onsearch={handleSearch}
		onnewfile={() => fileInput.click()}
		onnewfolderupload={() => folderInput.click()}
		onnewfolder={() => (modalOpen = true)}
	/>
	<div class="drive-body">
		<Sidebar />
		<main class="drive-main" onclick={() => { ctxMenu = null; clearSelection(); }}>
			{@render children()}
		</main>
	</div>
</div>

<NewFolderModal open={modalOpen} oncreate={handleCreate} onclose={() => (modalOpen = false)} />
<ContextMenu menu={ctxMenu} ondelete={handleDelete} />
<SearchResults results={searchResults} query={searchQuery} onclose={() => { searchQuery = ''; searchResults = []; }} />
<UploadProgress {uploads} onclear={() => (uploads = uploads.filter((u) => u.status === 'uploading'))} />

<style>
	.drive-layout { display: flex; flex-direction: column; height: 100vh; }
	.drive-body { display: flex; flex: 1; overflow: hidden; }
	.drive-main { flex: 1; display: flex; flex-direction: column; overflow: auto; }
</style>

<script>
	import { getContext } from 'svelte';
	import { page } from '$app/stores';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import FileGrid from '$lib/components/FileGrid.svelte';
	import UploadZone from '$lib/components/UploadZone.svelte';

	let { data } = $props();
	const { handleFiles } = getContext('drive');

	const folderId = $derived($page.params.folderId);
	const folderName = $derived(data.crumbs.at(-1)?.name ?? 'Folder');
</script>

<svelte:head><title>{folderName} — Drive</title></svelte:head>

<BreadcrumbNav crumbs={data.crumbs} />

<UploadZone {folderId} onfiles={(files) => handleFiles(files, folderId)}>
	<FileGrid folders={data.folders} files={data.files} />
</UploadZone>

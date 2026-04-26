<script>
	import { getContext } from 'svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import FileGrid from '$lib/components/FileGrid.svelte';
	import UploadZone from '$lib/components/UploadZone.svelte';

	let { data } = $props();
	const { handleFiles } = getContext('drive');
</script>

<svelte:head><title>My Drive</title></svelte:head>

<BreadcrumbNav crumbs={data.crumbs} />

<UploadZone folderId={null} onfiles={(files) => handleFiles(files, null)}>
	<FileGrid folders={data.folders} files={data.files} />
</UploadZone>

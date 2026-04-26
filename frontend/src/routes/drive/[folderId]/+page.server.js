import { listFiles, listFolders, getBreadcrumb } from '$lib/api.js';

/** @type {import('./$types').PageServerLoad} */
export async function load({ params }) {
	const { folderId } = params;
	const [files, folders, crumbs] = await Promise.all([
		listFiles(folderId),
		listFolders(folderId),
		getBreadcrumb(folderId)
	]);
	return { files, folders, crumbs };
}

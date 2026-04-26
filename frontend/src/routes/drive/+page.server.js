import { listFiles, listFolders } from '$lib/api.js';

/** @type {import('./$types').PageServerLoad} */
export async function load() {
	const [files, folders] = await Promise.all([
		listFiles(null),
		listFolders(null)
	]);
	return { files, folders, crumbs: [] };
}

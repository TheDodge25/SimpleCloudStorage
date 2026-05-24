import { error } from '@sveltejs/kit';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ locals }) {
	if (!locals.user || locals.user.role !== 'admin') {
		error(403, 'Admin access required');
	}
	return {};
}

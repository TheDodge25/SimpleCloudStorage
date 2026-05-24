import { fail } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND = env.BACKEND_URL ?? 'http://localhost:8000';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
	const accessToken = cookies.get('access_token');
	try {
		const res = await fetch(`${BACKEND}/api/v1/admin/users`, {
			headers: { Cookie: `access_token=${accessToken}` }
		});
		if (res.ok) {
			const users = await res.json();
			return { users };
		}
	} catch (err) {
		// handle silently
	}
	return { users: [] };
}

/** @type {import('./$types').Actions} */
export const actions = {
	create: async ({ request, cookies }) => {
		const data = await request.formData();
		const username = data.get('username');
		const email = data.get('email');
		const password = data.get('password');
		const role = data.get('role');
		const quotaRaw = data.get('quota_bytes');
		const quota_bytes = quotaRaw ? parseInt(quotaRaw.toString()) * 1024 * 1024 * 1024 : undefined;

		const accessToken = cookies.get('access_token');
		try {
			const res = await fetch(`${BACKEND}/api/v1/admin/users`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Cookie: `access_token=${accessToken}`
				},
				body: JSON.stringify({ username, email, password, role, quota_bytes })
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: 'Failed to create user' }));
				return fail(res.status, { action: 'create', error: err.detail });
			}
		} catch (err) {
			return fail(500, { action: 'create', error: 'Network error connecting to backend' });
		}
		return { action: 'create', success: true };
	},

	update: async ({ request, cookies }) => {
		const data = await request.formData();
		const userId = data.get('userId');
		const role = data.get('role');
		const quotaRaw = data.get('quota_bytes');
		const quota_bytes = quotaRaw ? parseInt(quotaRaw.toString()) * 1024 * 1024 * 1024 : undefined;

		const accessToken = cookies.get('access_token');
		try {
			const res = await fetch(`${BACKEND}/api/v1/admin/users/${userId}`, {
				method: 'PATCH',
				headers: {
					'Content-Type': 'application/json',
					Cookie: `access_token=${accessToken}`
				},
				body: JSON.stringify({ role, quota_bytes })
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: 'Failed to update user' }));
				return fail(res.status, { action: 'update', error: err.detail });
			}
		} catch (err) {
			return fail(500, { action: 'update', error: 'Network error' });
		}
		return { action: 'update', success: true };
	},

	delete: async ({ request, cookies }) => {
		const data = await request.formData();
		const userId = data.get('userId');

		const accessToken = cookies.get('access_token');
		try {
			const res = await fetch(`${BACKEND}/api/v1/admin/users/${userId}`, {
				method: 'DELETE',
				headers: { Cookie: `access_token=${accessToken}` }
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: 'Failed to delete user' }));
				return fail(res.status, { action: 'delete', error: err.detail });
			}
		} catch (err) {
			return fail(500, { action: 'delete', error: 'Network error' });
		}
		return { action: 'delete', success: true };
	}
};

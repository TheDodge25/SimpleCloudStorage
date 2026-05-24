import { fail, redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND = env.BACKEND_URL ?? 'http://localhost:8000';

/** @type {import('./$types').PageServerLoad} */
export async function load({ locals }) {
	// If already logged in, redirect away from login page
	if (locals.user) {
		redirect(303, '/drive');
	}
	return {};
}

/** @type {import('./$types').Actions} */
export const actions = {
	login: async ({ request, cookies, url }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');

		if (!username || !password) {
			return fail(400, { error: 'Username and password are required' });
		}

		try {
			const res = await fetch(`${BACKEND}/api/v1/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			if (!res.ok) {
				const msg = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
				return fail(res.status, { error: msg.detail || 'Login failed' });
			}

			// Extract and set cookies returned by backend
			const setCookieHeaders = res.headers.getSetCookie?.() ?? [];
			for (const header of setCookieHeaders) {
				const [nameVal, ...directives] = header.split(';').map((s) => s.trim());
				const [name, value] = nameVal.split('=');
				const opts = { path: '/', httpOnly: true, sameSite: 'lax' };
				const maxAgeDir = directives.find((d) => d.toLowerCase().startsWith('max-age'));
				if (maxAgeDir) opts.maxAge = parseInt(maxAgeDir.split('=')[1]);
				cookies.set(name, value, opts);
			}
		} catch (err) {
			return fail(500, { error: 'Network error connecting to auth server' });
		}

		const redirectTo = url.searchParams.get('redirectTo') || '/drive';
		redirect(303, redirectTo);
	},
	
	logout: async ({ cookies }) => {
		const refreshToken = cookies.get('refresh_token');
		if (refreshToken) {
			try {
				await fetch(`${BACKEND}/api/v1/auth/logout`, {
					method: 'POST',
					headers: { Cookie: `refresh_token=${refreshToken}` }
				});
			} catch {
				// Ignore network errors on logout
			}
		}

		// Clear local cookies
		cookies.delete('access_token', { path: '/' });
		cookies.delete('refresh_token', { path: '/' });

		redirect(303, '/login');
	}
};

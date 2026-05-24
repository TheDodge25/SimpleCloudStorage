/**
 * hooks.server.js — SvelteKit server hooks.
 *
 * Runs on every incoming request before any load function.
 * Responsibilities:
 *  1. Read the access_token cookie and validate it.
 *  2. If the access token is expired but a refresh_token cookie exists,
 *     call the backend /auth/refresh endpoint and rotate the cookies.
 *  3. Populate event.locals.user for use in load functions.
 *  4. Redirect unauthenticated requests to /login (except /login itself).
 */

import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const BACKEND = env.BACKEND_URL ?? 'http://localhost:8000';
const PUBLIC_ROUTES = ['/login'];

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
	const { cookies, url } = event;
	const isPublic = PUBLIC_ROUTES.some((r) => url.pathname.startsWith(r));

	// ── Try to load user from access_token ──────────────────────────────────
	const accessToken = cookies.get('access_token');

	if (accessToken) {
		try {
			const res = await fetch(`${BACKEND}/api/v1/auth/me`, {
				headers: { Cookie: `access_token=${accessToken}` }
			});
			if (res.ok) {
				event.locals.user = await res.json();
				return resolve(event);
			}
		} catch {
			// Network error — fall through to refresh attempt
		}
	}

	// ── Try to refresh using refresh_token ───────────────────────────────────
	const refreshToken = cookies.get('refresh_token');
	if (refreshToken) {
		try {
			const res = await fetch(`${BACKEND}/api/v1/auth/refresh`, {
				method: 'POST',
				headers: { Cookie: `refresh_token=${refreshToken}` }
			});
			if (res.ok) {
				const data = await res.json();
				event.locals.user = data.user;

				// Forward the new cookies set by the backend to the browser
				const setCookieHeaders = res.headers.getSetCookie?.() ?? [];
				for (const header of setCookieHeaders) {
					// Parse each Set-Cookie header and re-set via SvelteKit cookies
					const [nameVal, ...directives] = header.split(';').map((s) => s.trim());
					const [name, value] = nameVal.split('=');
					const opts = { path: '/', httpOnly: true, sameSite: 'lax' };
					const maxAgeDir = directives.find((d) => d.toLowerCase().startsWith('max-age'));
					if (maxAgeDir) opts.maxAge = parseInt(maxAgeDir.split('=')[1]);
					cookies.set(name, value, opts);
				}

				return resolve(event);
			}
		} catch {
			// Refresh failed — fall through to unauthenticated handling
		}
	}

	// ── No valid session ─────────────────────────────────────────────────────
	event.locals.user = null;

	if (!isPublic) {
		redirect(303, `/login?redirectTo=${encodeURIComponent(url.pathname)}`);
	}

	return resolve(event);
}

/**
 * Server-side API client — runs only in SvelteKit load functions (+page.server.js).
 * Uses BACKEND_URL env var to reach FastAPI directly inside Docker (http://backend:8000).
 * Falls back to localhost:8000 for local dev without Docker.
 */
import { env } from '$env/dynamic/private';

const BASE = `${env.BACKEND_URL ?? 'http://localhost:8000'}/api/v1`;

/** @param {string} path @param {RequestInit} [opts] */
async function req(path, opts = {}) {
	const res = await fetch(BASE + path, opts);
	if (!res.ok) {
		const msg = await res.text().catch(() => res.statusText);
		throw new Error(msg || `HTTP ${res.status}`);
	}
	return res.status === 204 ? null : res.json();
}

// ── Files ────────────────────────────────────────────────────────────────
/** @param {string|null} folderId */
export const listFiles = (folderId = null) =>
	req(`/files${folderId ? `?folder_id=${folderId}` : ''}`);

// ── Folders ──────────────────────────────────────────────────────────────
/** @param {string|null} parentId */
export const listFolders = (parentId = null) =>
	req(`/folders${parentId ? `?parent_id=${parentId}` : ''}`);

/** @param {string} folderId */
export const getBreadcrumb = (folderId) =>
	req(`/folders/${folderId}/breadcrumb`);

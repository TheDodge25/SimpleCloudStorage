const BASE = '/api/v1';

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

/** @param {string} fileId */
export const deleteFile = (fileId) =>
	req(`/files/${fileId}`, { method: 'DELETE' });

/** @param {string} fileId */
export const getDownloadUrl = (fileId) => `${BASE}/files/${fileId}/download`;

/**
 * Upload a single file with progress tracking.
 * @param {File} file
 * @param {string|null} folderId
 * @param {(pct: number) => void} onProgress  0–1
 * @returns {Promise<object>}
 */
export function uploadFile(file, folderId, onProgress) {
	return new Promise((resolve, reject) => {
		const xhr = new XMLHttpRequest();
		const fd = new FormData();
		fd.append('file', file);
		const url = `${BASE}/files/upload${folderId ? `?folder_id=${folderId}` : ''}`;
		xhr.open('POST', url);
		xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(e.loaded / e.total);
		xhr.onload = () => {
			if (xhr.status === 201) resolve(JSON.parse(xhr.responseText));
			else reject(new Error(xhr.responseText || `HTTP ${xhr.status}`));
		};
		xhr.onerror = () => reject(new Error('Upload failed'));
		xhr.send(fd);
	});
}

// ── Folders ──────────────────────────────────────────────────────────────

/** @param {string|null} parentId */
export const listFolders = (parentId = null) =>
	req(`/folders${parentId ? `?parent_id=${parentId}` : ''}`);

/** @param {{ name: string, parent_id?: string|null }} body */
export const createFolder = (body) =>
	req('/folders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

/** @param {string} folderId */
export const deleteFolder = (folderId) =>
	req(`/folders/${folderId}`, { method: 'DELETE' });

/** @param {string} folderId */
export const getBreadcrumb = (folderId) =>
	req(`/folders/${folderId}/breadcrumb`);

// ── Search ───────────────────────────────────────────────────────────────

/** @param {string} q @param {string|null} [folderId] */
export const search = (q, folderId = null) =>
	req(`/search?q=${encodeURIComponent(q)}${folderId ? `&folder_id=${folderId}` : ''}`);

import { writable } from 'svelte/store';

// ── Multi-select ─────────────────────────────────────────────────────────
/** @type {import('svelte/store').Writable<Set<string>>} */
export const selected = writable(new Set());

export function toggleSelect(id, event) {
	selected.update((s) => {
		const next = new Set(s);
		if (event?.ctrlKey || event?.metaKey) {
			next.has(id) ? next.delete(id) : next.add(id);
		} else if (event?.shiftKey) {
			next.add(id);
		} else {
			return next.has(id) && next.size === 1 ? new Set() : new Set([id]);
		}
		return next;
	});
}

export const clearSelection = () => selected.set(new Set());

// ── Toasts ───────────────────────────────────────────────────────────────
/** @typedef {{ id: string, type: 'success'|'error'|'info', message: string }} Toast */
/** @type {import('svelte/store').Writable<Toast[]>} */
export const toasts = writable([]);

/** @param {'success'|'error'|'info'} type @param {string} message */
export function addToast(type, message) {
	const id = crypto.randomUUID();
	toasts.update((t) => [...t, { id, type, message }]);
	setTimeout(() => toasts.update((t) => t.filter((x) => x.id !== id)), 3500);
}

// ── Sort state ───────────────────────────────────────────────────────────
/** @typedef {{ field: 'name'|'size'|'date', dir: 'asc'|'desc' }} SortState */
/** @type {import('svelte/store').Writable<SortState>} */
export const sortState = writable({ field: 'name', dir: 'asc' });

export function cycleSort(field) {
	sortState.update((s) => ({
		field,
		dir: s.field === field && s.dir === 'asc' ? 'desc' : 'asc'
	}));
}

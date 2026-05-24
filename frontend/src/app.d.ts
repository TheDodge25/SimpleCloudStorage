// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user: {
				id: string;
				username: string;
				email: string;
				role: 'user' | 'admin';
				quota_bytes: number;
				used_bytes: number;
			} | null;
		}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};

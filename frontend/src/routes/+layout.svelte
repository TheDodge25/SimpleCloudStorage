<script>
	import './layout.css';
	import Toast from '$lib/components/Toast.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<meta name="description" content="Self-hosted Google Drive clone" />
	<title>Drive</title>
</svelte:head>

<div class="app-shell">
	{@render children()}
</div>

<Toast />

<style>
	.app-shell {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background: var(--color-bg);
	}
</style>

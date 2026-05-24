<script>
	import { enhance } from '$app/forms';
	import { Cloud } from 'lucide-svelte';

	let { form } = $props();
	let loading = $state(false);
</script>

<svelte:head>
	<title>Log in - Drive</title>
</svelte:head>

<div class="login-container">
	<div class="login-box">
		<div class="brand">
			<svg width="32" height="32" viewBox="0 0 22 22" aria-hidden="true">
				<polygon points="11,1 21,19 1,19" fill="none" stroke="#4285f4" stroke-width="2.5" stroke-linejoin="round"/>
				<line x1="6" y1="19" x2="16" y2="19" stroke="#34a853" stroke-width="2.5" stroke-linecap="round"/>
				<line x1="11" y1="1" x2="16" y2="19" stroke="#fbbc04" stroke-width="2.5" stroke-linecap="round"/>
			</svg>
			<h1>Sign in</h1>
			<p>Continue to SimpleCloudStorage</p>
		</div>

		{#if form?.error}
			<div class="error-msg" role="alert">
				{form.error}
			</div>
		{/if}

		<form
			method="POST"
			action="?/login"
			class="login-form"
			use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					await update();
					loading = false;
				};
			}}
		>
			<div class="field">
				<label for="username">Username</label>
				<input type="text" id="username" name="username" required autocomplete="username" />
			</div>
			
			<div class="field">
				<label for="password">Password</label>
				<input type="password" id="password" name="password" required autocomplete="current-password" />
			</div>

			<button type="submit" class="btn-primary login-btn" disabled={loading}>
				{loading ? 'Signing in...' : 'Sign in'}
			</button>
		</form>
	</div>
</div>

<style>
	.login-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		background: var(--color-bg);
		padding: 1rem;
	}
	.login-box {
		width: 100%;
		max-width: 400px;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 2.5rem;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
	}
	.brand {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		margin-bottom: 2rem;
	}
	.brand h1 {
		font-size: 1.5rem;
		font-weight: 500;
		color: var(--color-text);
		margin: 1rem 0 0.5rem;
	}
	.brand p {
		color: var(--color-text-muted);
		margin: 0;
		font-size: 0.95rem;
	}
	.error-msg {
		background: #ea433520;
		color: #ea4335;
		padding: 0.75rem;
		border-radius: var(--radius-sm);
		margin-bottom: 1.5rem;
		font-size: 0.875rem;
		border: 1px solid #ea433540;
		text-align: center;
	}
	.login-form {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}
	.field {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	label {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		font-weight: 500;
	}
	input {
		padding: 0.75rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		color: var(--color-text);
		font-size: 1rem;
		outline: none;
		transition: border-color 0.2s;
	}
	input:focus {
		border-color: var(--color-primary);
	}
	.login-btn {
		margin-top: 1rem;
		padding: 0.75rem;
		font-size: 1rem;
		justify-content: center;
	}
	.login-btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}
</style>

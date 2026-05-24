<script>
	import { enhance } from '$app/forms';
	import { Trash2, Edit2, Plus, Shield, ShieldAlert } from 'lucide-svelte';
	import { addToast } from '$lib/stores.js';
	import Topbar from '$lib/components/Topbar.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';

	let { data, form } = $props();

	// form result handling via effect
	$effect(() => {
		if (form?.error) {
			addToast('error', form.error);
		} else if (form?.success) {
			addToast('success', `Action ${form.action} completed successfully`);
			if (form.action === 'create') {
				createModalOpen = false;
			} else if (form.action === 'update') {
				editModalOpen = false;
			}
		}
	});

	let createModalOpen = $state(false);
	let editModalOpen = $state(false);
	let selectedUser = $state(null);

	function openEdit(user) {
		selectedUser = user;
		editModalOpen = true;
	}
</script>

<svelte:head>
	<title>Admin Panel - Drive</title>
</svelte:head>

<div class="drive-layout">
	<Topbar />
	<div class="drive-body">
		<Sidebar />
		<main class="drive-main">
			<div class="admin-header">
				<h1>User Management</h1>
				<button class="btn-primary" onclick={() => (createModalOpen = true)}>
					<Plus size={16} /> New User
				</button>
			</div>

			<div class="table-wrap">
				<table class="admin-table">
					<thead>
						<tr>
							<th>Username</th>
							<th>Email</th>
							<th>Role</th>
							<th>Storage Used</th>
							<th>Quota</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each data.users as user}
							<tr>
								<td><strong>{user.username}</strong></td>
								<td>{user.email}</td>
								<td>
									<span class="role-badge" class:admin={user.role === 'admin'}>
										{#if user.role === 'admin'}
											<ShieldAlert size={14} /> Admin
										{:else}
											<Shield size={14} /> User
										{/if}
									</span>
								</td>
								<td>{(user.used_bytes / (1024 ** 3)).toFixed(2)} GB</td>
								<td>{(user.quota_bytes / (1024 ** 3)).toFixed(2)} GB</td>
								<td>
									<div class="row-actions">
										<button class="icon-btn" aria-label="Edit" onclick={() => openEdit(user)}>
											<Edit2 size={16} />
										</button>
										{#if user.id !== data.user.id}
											<form action="?/delete" method="POST" use:enhance onsubmit={(e) => {
												if (!confirm(`Delete user ${user.username} and all their files? This CANNOT be undone.`)) {
													e.preventDefault();
												}
											}}>
												<input type="hidden" name="userId" value={user.id} />
												<button class="icon-btn danger" type="submit" aria-label="Delete">
													<Trash2 size={16} />
												</button>
											</form>
										{/if}
									</div>
								</td>
							</tr>
						{:else}
							<tr>
								<td colspan="6" class="empty">No users found.</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</main>
	</div>
</div>

{#if createModalOpen}
	<div class="modal-backdrop">
		<div class="modal-content animate-fade-in">
			<h3>Create New User</h3>
			<form action="?/create" method="POST" use:enhance class="modal-form">
				<div class="field">
					<label for="username">Username</label>
					<input type="text" id="username" name="username" required minlength="3" />
				</div>
				<div class="field">
					<label for="email">Email</label>
					<input type="email" id="email" name="email" required />
				</div>
				<div class="field">
					<label for="password">Password</label>
					<input type="password" id="password" name="password" required minlength="8" />
				</div>
				<div class="field">
					<label for="role">Role</label>
					<select id="role" name="role">
						<option value="user">User</option>
						<option value="admin">Admin</option>
					</select>
				</div>
				<div class="field">
					<label for="quota">Quota (GB)</label>
					<input type="number" id="quota" name="quota_bytes" min="1" placeholder="10" />
					<small>Leave blank for default (10 GB)</small>
				</div>
				<div class="modal-actions">
					<button type="button" class="btn-text" onclick={() => (createModalOpen = false)}>Cancel</button>
					<button type="submit" class="btn-primary">Create User</button>
				</div>
			</form>
		</div>
	</div>
{/if}

{#if editModalOpen && selectedUser}
	<div class="modal-backdrop">
		<div class="modal-content animate-fade-in">
			<h3>Edit User: {selectedUser.username}</h3>
			<form action="?/update" method="POST" use:enhance class="modal-form">
				<input type="hidden" name="userId" value={selectedUser.id} />
				<div class="field">
					<label for="edit-role">Role</label>
					<select id="edit-role" name="role" value={selectedUser.role}>
						<option value="user">User</option>
						<option value="admin">Admin</option>
					</select>
				</div>
				<div class="field">
					<label for="edit-quota">Quota (GB)</label>
					<input type="number" id="edit-quota" name="quota_bytes" min="1" value={selectedUser.quota_bytes / (1024 ** 3)} />
				</div>
				<div class="modal-actions">
					<button type="button" class="btn-text" onclick={() => (editModalOpen = false)}>Cancel</button>
					<button type="submit" class="btn-primary">Save Changes</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<style>
	.drive-layout { display: flex; flex-direction: column; height: 100vh; }
	.drive-body { display: flex; flex: 1; overflow: hidden; }
	.drive-main { flex: 1; display: flex; flex-direction: column; overflow: auto; padding: 2rem; background: var(--color-bg); }

	.admin-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}
	.admin-header h1 {
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--color-text);
		margin: 0;
	}

	.table-wrap {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.admin-table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
	}
	.admin-table th, .admin-table td {
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--color-border);
		color: var(--color-text);
		font-size: 0.95rem;
	}
	.admin-table th {
		background: var(--color-surface-alt);
		font-weight: 500;
		color: var(--color-text-muted);
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.admin-table tr:last-child td { border-bottom: none; }
	.admin-table tbody tr:hover { background: var(--color-surface-alt); }

	.role-badge {
		display: inline-flex; align-items: center; gap: 0.375rem;
		padding: 0.25rem 0.5rem; border-radius: 1rem;
		font-size: 0.75rem; font-weight: 600;
		background: #34a85320; color: #34a853;
	}
	.role-badge.admin { background: #ea433520; color: #ea4335; }

	.row-actions {
		display: flex; gap: 0.5rem; align-items: center;
	}
	.icon-btn {
		background: none; border: none; padding: 0.4rem;
		border-radius: var(--radius-sm); color: var(--color-text-muted);
		cursor: pointer; display: flex; transition: all 0.2s;
	}
	.icon-btn:hover { background: var(--color-border); color: var(--color-text); }
	.icon-btn.danger:hover { background: #ea433520; color: #ea4335; }

	.empty { text-align: center; color: var(--color-text-muted); padding: 3rem !important; }

	/* Modals */
	.modal-backdrop {
		position: fixed; inset: 0; z-index: 200;
		background: rgba(0, 0, 0, 0.5);
		display: flex; align-items: center; justify-content: center;
		padding: 1rem;
	}
	.modal-content {
		background: var(--color-surface); border: 1px solid var(--color-border);
		border-radius: var(--radius-lg); padding: 1.5rem; width: 100%; max-width: 420px;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
	}
	.modal-content h3 { margin: 0 0 1.25rem; font-size: 1.25rem; font-weight: 500; }
	.modal-form { display: flex; flex-direction: column; gap: 1.25rem; }
	.field { display: flex; flex-direction: column; gap: 0.5rem; }
	.field label { font-size: 0.875rem; color: var(--color-text-muted); font-weight: 500; }
	.field input, .field select {
		padding: 0.625rem; background: var(--color-bg); border: 1px solid var(--color-border);
		border-radius: var(--radius-sm); color: var(--color-text); font-size: 0.95rem; outline: none;
	}
	.field input:focus, .field select:focus { border-color: var(--color-primary); }
	.field small { font-size: 0.75rem; color: var(--color-text-faint); }
	.modal-actions {
		display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem;
	}
	.btn-text {
		background: none; border: none; padding: 0.5rem 1rem; color: var(--color-text);
		font-weight: 500; cursor: pointer; border-radius: var(--radius-sm);
	}
	.btn-text:hover { background: var(--color-surface-alt); }
</style>

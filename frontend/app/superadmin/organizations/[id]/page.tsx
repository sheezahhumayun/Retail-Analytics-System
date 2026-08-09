'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ArrowLeft, Edit2, Plus, Trash2 } from 'lucide-react';

import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { ResetPasswordModal } from '@/components/admin/reset-password-modal';
import { UserModal } from '@/components/admin/user-modal';
import { UserTable } from '@/components/admin/user-table';
import { StoreModal } from '@/components/superadmin/store-modal';
import { ApiClientError } from '@/lib/api/client';
import type { BackendStore } from '@/lib/api/mappers';
import {
  getOrganization,
  getOrgStores,
  getOrgUsers,
  toggleOrganization,
  type Organization,
} from '@/lib/api/organizations-admin';
import {
  createStore,
  deleteStore,
  updateStore,
  type CreateStoreData,
  type UpdateStoreData,
} from '@/lib/api/stores-admin';
import {
  createUser,
  deleteUser,
  resetPassword,
  updateUser,
} from '@/lib/api/users';
import type { User } from '@/lib/types';

function getApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiClientError) {
    if (error.code === 'validation_error' && Array.isArray(error.details)) {
      const firstDetail = error.details[0];
      if (
        firstDetail &&
        typeof firstDetail === 'object' &&
        'msg' in firstDetail &&
        typeof firstDetail.msg === 'string'
      ) {
        return firstDetail.msg;
      }
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
}

function getSaveUserErrorMessage(error: unknown): string {
  return getApiErrorMessage(error, 'Failed to save user');
}

function formatStatus(status: Organization['status']): string {
  return status === 'active' ? 'Active' : 'Disabled';
}

function statusBadgeClass(status: Organization['status']): string {
  return status === 'active'
    ? 'bg-green-500/10 text-green-700 dark:text-green-400'
    : 'bg-gray-500/10 text-gray-700 dark:text-gray-400';
}

type ServiceRowConfig = {
  id: string;
  label: string;
  enabled: boolean;
  onToggle: () => void;
  toggling: boolean;
};

export default function SuperadminOrganizationDetailPage() {
  const params = useParams<{ id: string }>();
  const orgId = params.id;

  const [organization, setOrganization] = useState<Organization | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [stores, setStores] = useState<BackendStore[]>([]);
  const [storeNames, setStoreNames] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [actionError, setActionError] = useState('');
  const [togglingService, setTogglingService] = useState(false);
  const [editingStore, setEditingStore] = useState<BackendStore | undefined>();
  const [showStoreModal, setShowStoreModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | undefined>();
  const [showAddModal, setShowAddModal] = useState(false);
  const [resetPasswordUser, setResetPasswordUser] = useState<User | undefined>();
  const [showResetPasswordModal, setShowResetPasswordModal] = useState(false);

  const refreshStores = useCallback(async () => {
    const storesData = await getOrgStores(orgId);
    setStores(storesData);
    setStoreNames(storesData.map((store) => store.name));
  }, [orgId]);

  const loadPage = useCallback(async () => {
    const [org, orgUsers, storesData] = await Promise.all([
      getOrganization(orgId),
      getOrgUsers(orgId),
      getOrgStores(orgId),
    ]);
    setOrganization(org);
    setUsers(orgUsers);
    setStores(storesData);
    setStoreNames(storesData.map((store) => store.name));
    setLoadError('');
  }, [orgId]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        await loadPage();
      } catch (error) {
        if (!cancelled) {
          setLoadError(getApiErrorMessage(error, 'Failed to load organization'));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [loadPage]);

  const handleToggleRetailAnalytics = useCallback(async () => {
    setActionError('');
    setTogglingService(true);
    try {
      const updated = await toggleOrganization(orgId);
      setOrganization(updated);
    } catch (error) {
      setActionError(
        getApiErrorMessage(error, 'Failed to toggle Retail Analytics service'),
      );
    } finally {
      setTogglingService(false);
    }
  }, [orgId]);

  const serviceRows: ServiceRowConfig[] = useMemo(() => {
    if (!organization) return [];
    return [
      {
        id: 'retail-analytics',
        label: 'Retail Analytics',
        enabled: organization.status === 'active',
        onToggle: handleToggleRetailAnalytics,
        toggling: togglingService,
      },
    ];
  }, [organization, togglingService, handleToggleRetailAnalytics]);

  const handleAddStore = () => {
    setEditingStore(undefined);
    setShowStoreModal(true);
  };

  const handleEditStore = (store: BackendStore) => {
    setEditingStore(store);
    setShowStoreModal(true);
  };

  const handleSaveStore = async (data: CreateStoreData | UpdateStoreData) => {
    try {
      if (editingStore) {
        await updateStore(editingStore.id, data as UpdateStoreData);
      } else {
        await createStore(data as CreateStoreData);
      }
      await refreshStores();
      setActionError('');
    } catch (error) {
      throw new Error(getApiErrorMessage(error, 'Failed to save store'));
    }
  };

  const handleDeleteStore = async (store: BackendStore) => {
    if (!confirm(`Are you sure you want to delete store "${store.name}"?`)) {
      return;
    }
    setActionError('');
    try {
      await deleteStore(store.id);
      await refreshStores();
    } catch (error) {
      setActionError(getApiErrorMessage(error, 'Failed to delete store'));
    }
  };

  const handleAddUser = () => {
    setEditingUser(undefined);
    setShowAddModal(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setShowAddModal(true);
  };

  const handleSaveUser = async (user: User & { password?: string }) => {
    try {
      if (editingUser) {
        const updated = await updateUser(user.id, user, orgId);
        setUsers((prev) => prev.map((u) => (u.id === user.id ? updated : u)));
      } else {
        const created = await createUser(
          {
            name: user.name,
            email: user.email,
            role: user.role,
            assignedStore: user.assignedStore,
            status: user.status,
            password: user.password ?? 'demo',
            id: user.id || undefined,
          },
          orgId,
        );
        setUsers((prev) => [...prev, created]);
      }
    } catch (error) {
      throw new Error(getSaveUserErrorMessage(error));
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (confirm('Are you sure you want to delete this user?')) {
      const removed = await deleteUser(userId, orgId);
      if (removed) {
        setUsers((prev) => prev.filter((u) => u.id !== userId));
      }
    }
  };

  const handleResetPassword = (user: User) => {
    setResetPasswordUser(user);
    setShowResetPasswordModal(true);
  };

  const handleSaveResetPassword = async (newPassword: string) => {
    if (resetPasswordUser) {
      await resetPassword(resetPasswordUser.id, newPassword, orgId);
    }
    setShowResetPasswordModal(false);
  };

  const activeUsersCount = users.filter((u) => u.status === 'Active').length;
  const disabledUsersCount = users.filter((u) => u.status === 'Disabled').length;

  return (
    <DashboardShell hideScopeSelector>
      <div className="space-y-6">
        <div>
          <Link
            href="/superadmin/organizations"
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to organizations
          </Link>

          {loading ? (
            <div className="h-10 w-64 animate-pulse rounded bg-muted" />
          ) : organization ? (
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-bold text-foreground font-mono">{organization.id}</h1>
              <span className="text-2xl text-muted-foreground">·</span>
              <span className="text-2xl font-semibold text-foreground">{organization.name}</span>
              <span
                className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${statusBadgeClass(organization.status)}`}
              >
                {formatStatus(organization.status)}
              </span>
            </div>
          ) : null}
        </div>

        {actionError && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-600 dark:text-red-400">
            {actionError}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-block relative w-10 h-10 mb-3">
                <div className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full animate-spin" />
              </div>
              <p className="text-sm text-muted-foreground">Loading organization…</p>
            </div>
          </div>
        ) : loadError ? (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-600 dark:text-red-400">
            {loadError}
          </div>
        ) : organization ? (
          <>
            <section className="bg-card border border-border rounded-lg">
              <div className="px-4 py-3 border-b border-border">
                <h2 className="text-lg font-semibold text-foreground">Services</h2>
                <p className="text-sm text-muted-foreground mt-0.5">
                  Enable or disable platform services for this organization
                </p>
              </div>
              <div className="divide-y divide-border">
                {serviceRows.map((service) => (
                  <div
                    key={service.id}
                    className="flex items-center justify-between gap-4 px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-foreground">{service.label}</p>
                      <p className="text-xs text-muted-foreground">
                        {service.enabled
                          ? 'Organization can log in and run analytics'
                          : 'Organization login and processing are blocked'}
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-checked={service.enabled}
                      aria-label={`${service.label} ${service.enabled ? 'enabled' : 'disabled'}`}
                      disabled={service.toggling}
                      onClick={service.onToggle}
                      className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-60 disabled:cursor-not-allowed ${
                        service.enabled ? 'bg-primary' : 'bg-muted'
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
                          service.enabled ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-card border border-border rounded-lg">
              <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                <div>
                  <h2 className="text-lg font-semibold text-foreground">Stores</h2>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Manage retail locations for this organization
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleAddStore}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Add Store
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-border bg-muted/40">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-foreground">ID</th>
                      <th className="px-4 py-3 text-left font-semibold text-foreground">Name</th>
                      <th className="px-4 py-3 text-left font-semibold text-foreground">Address</th>
                      <th className="px-4 py-3 text-left font-semibold text-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {stores.map((store) => (
                      <tr key={store.id} className="hover:bg-muted/40 transition-colors">
                        <td className="px-4 py-3 font-mono text-foreground">{store.id}</td>
                        <td className="px-4 py-3 text-foreground">{store.name}</td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {store.address || '—'}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => handleEditStore(store)}
                              title="Edit store"
                              className="p-1.5 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteStore(store)}
                              title="Delete store"
                              className="p-1.5 rounded transition-colors text-red-600 hover:bg-red-500/10 dark:text-red-400"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {stores.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                          No stores yet. Add one to assign users and cameras.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-foreground">Users</h2>
                  <p className="text-muted-foreground mt-1 text-sm">
                    Manage accounts for this organization
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleAddUser}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Add User
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-card border border-border rounded-lg p-4">
                  <p className="text-sm text-muted-foreground">Total Users</p>
                  <p className="text-2xl font-bold text-foreground">{users.length}</p>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                  <p className="text-sm text-muted-foreground">Active</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {activeUsersCount}
                  </p>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                  <p className="text-sm text-muted-foreground">Disabled</p>
                  <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">
                    {disabledUsersCount}
                  </p>
                </div>
              </div>

              <UserTable
                users={users}
                onEdit={handleEditUser}
                onDelete={handleDeleteUser}
                onResetPassword={handleResetPassword}
              />
            </section>
          </>
        ) : null}
      </div>

      <StoreModal
        store={editingStore}
        orgId={orgId}
        isOpen={showStoreModal}
        onClose={() => {
          setShowStoreModal(false);
          setEditingStore(undefined);
        }}
        onSave={handleSaveStore}
      />
      <UserModal
        user={editingUser}
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSave={handleSaveUser}
        storeOptions={storeNames}
      />
      <ResetPasswordModal
        userName={resetPasswordUser?.name}
        isOpen={showResetPasswordModal}
        onClose={() => setShowResetPasswordModal(false)}
        onSave={handleSaveResetPassword}
      />
    </DashboardShell>
  );
}

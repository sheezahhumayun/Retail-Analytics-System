'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Plus, Trash2 } from 'lucide-react';

import { CreateOrgModal } from '@/components/superadmin/create-org-modal';
import { DeleteOrgModal } from '@/components/superadmin/delete-org-modal';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { ApiClientError } from '@/lib/api/client';
import {
  createOrganization,
  deleteOrganization,
  listOrganizations,
  toggleOrganization,
  type Organization,
} from '@/lib/api/organizations-admin';

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

function formatStatus(status: Organization['status']): string {
  return status === 'active' ? 'Active' : 'Disabled';
}

function statusBadgeClass(status: Organization['status']): string {
  return status === 'active'
    ? 'bg-green-500/10 text-green-700 dark:text-green-400'
    : 'bg-gray-500/10 text-gray-700 dark:text-gray-400';
}

export default function SuperadminOrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [actionError, setActionError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [deletingOrg, setDeletingOrg] = useState<Organization | undefined>();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await listOrganizations();
        if (!cancelled) {
          setOrganizations(data);
          setLoadError('');
        }
      } catch (error) {
        if (!cancelled) {
          setLoadError(getApiErrorMessage(error, 'Failed to load organizations'));
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
  }, []);

  const handleCreateOrganization = async (data: { id: string; name: string }) => {
    try {
      const created = await createOrganization(data);
      setOrganizations((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
    } catch (error) {
      throw new Error(getApiErrorMessage(error, 'Failed to create organization'));
    }
  };

  const handleToggleOrganization = async (org: Organization) => {
    setActionError('');
    setTogglingId(org.id);
    try {
      const updated = await toggleOrganization(org.id);
      setOrganizations((prev) =>
        prev.map((item) => (item.id === updated.id ? updated : item)),
      );
    } catch (error) {
      setActionError(getApiErrorMessage(error, 'Failed to toggle organization status'));
    } finally {
      setTogglingId(null);
    }
  };

  const handleDeleteOrganization = async (id: string, confirm: string) => {
    try {
      await deleteOrganization(id, confirm);
      setOrganizations((prev) => prev.filter((org) => org.id !== id));
      setActionError('');
    } catch (error) {
      throw new Error(getApiErrorMessage(error, 'Failed to delete organization'));
    }
  };

  const activeCount = organizations.filter((org) => org.status === 'active').length;
  const disabledCount = organizations.filter((org) => org.status === 'disabled').length;

  return (
    <DashboardShell hideScopeSelector>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Organizations</h1>
            <p className="text-muted-foreground mt-1">
              Manage tenant organizations across the platform
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium"
          >
            <Plus className="w-4 h-4" />
            Create Organization
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Total Organizations</p>
            <p className="text-2xl font-bold text-foreground">
              {loading ? '—' : organizations.length}
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Active</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {loading ? '—' : activeCount}
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Disabled</p>
            <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">
              {loading ? '—' : disabledCount}
            </p>
          </div>
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
              <p className="text-sm text-muted-foreground">Loading organizations…</p>
            </div>
          </div>
        ) : loadError ? (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-600 dark:text-red-400">
            {loadError}
          </div>
        ) : (
          <div className="overflow-x-auto border border-border rounded-lg bg-card">
            <table className="w-full text-sm">
              <thead className="border-b border-border bg-muted/40">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-foreground">ID</th>
                  <th className="px-4 py-3 text-left font-semibold text-foreground">Name</th>
                  <th className="px-4 py-3 text-left font-semibold text-foreground">Status</th>
                  <th className="px-4 py-3 text-left font-semibold text-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {organizations.map((org) => (
                  <tr key={org.id} className="hover:bg-muted/40 transition-colors">
                    <td className="px-4 py-3 font-mono text-foreground">
                      <Link
                        href={`/superadmin/organizations/${org.id}`}
                        className="hover:text-primary transition-colors"
                      >
                        {org.id}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-foreground">
                      <Link
                        href={`/superadmin/organizations/${org.id}`}
                        className="hover:text-primary transition-colors"
                      >
                        {org.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${statusBadgeClass(org.status)}`}
                      >
                        {formatStatus(org.status)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/superadmin/organizations/${org.id}`}
                          className="px-3 py-1.5 rounded-md border border-border bg-card text-foreground hover:bg-muted transition-colors text-xs font-medium"
                        >
                          Manage
                        </Link>
                        <button
                          type="button"
                          onClick={() => handleToggleOrganization(org)}
                          disabled={togglingId === org.id}
                          className="px-3 py-1.5 rounded-md border border-border bg-muted text-foreground hover:bg-muted/80 transition-colors text-xs font-medium disabled:opacity-60"
                        >
                          {togglingId === org.id
                            ? 'Updating…'
                            : org.status === 'active'
                              ? 'Disable'
                              : 'Enable'}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setDeletingOrg(org);
                            setShowDeleteModal(true);
                          }}
                          title="Delete organization"
                          className="p-1.5 rounded transition-colors text-red-600 hover:bg-red-500/10 dark:text-red-400"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {organizations.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                      No organizations yet. Create one to get started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <CreateOrgModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSave={handleCreateOrganization}
      />
      <DeleteOrgModal
        organization={deletingOrg}
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setDeletingOrg(undefined);
        }}
        onDelete={handleDeleteOrganization}
      />
    </DashboardShell>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

import type { Organization } from '@/lib/api/organizations-admin';

interface DeleteOrgModalProps {
  organization?: Organization;
  isOpen: boolean;
  onClose: () => void;
  onDelete: (id: string, confirm: string) => Promise<void>;
}

export function DeleteOrgModal({
  organization,
  isOpen,
  onClose,
  onDelete,
}: DeleteOrgModalProps) {
  const [confirmId, setConfirmId] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    setConfirmId('');
    setDeleteError('');
    setIsDeleting(false);
  }, [isOpen, organization?.id]);

  const canDelete =
    organization !== undefined && confirmId === organization.id && !isDeleting;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!organization || confirmId !== organization.id) {
      return;
    }

    setDeleteError('');
    setIsDeleting(true);
    try {
      await onDelete(organization.id, confirmId);
      onClose();
    } catch (error) {
      setDeleteError(
        error instanceof Error ? error.message : 'Failed to delete organization',
      );
    } finally {
      setIsDeleting(false);
    }
  };

  if (!isOpen || !organization) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md max-h-[90vh] bg-card border border-border rounded-lg shadow-lg overflow-y-auto">
        <div className="sticky top-0 flex items-center justify-between px-6 py-4 border-b border-border bg-card">
          <h2 className="text-lg font-semibold text-foreground">Delete Organization</h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="flex gap-3 rounded-lg border border-destructive/30 bg-destructive/10 p-4">
            <AlertTriangle className="h-5 w-5 shrink-0 text-destructive" aria-hidden="true" />
            <div className="space-y-1 text-sm">
              <p className="font-medium text-foreground">
                This action is permanent and cannot be undone.
              </p>
              <p className="text-muted-foreground">
                Deleting <span className="font-medium text-foreground">{organization.name}</span>{' '}
                ({organization.id}) will cascade-delete all stores, cameras, users, analytics data,
                and every other record belonging to this organization.
              </p>
            </div>
          </div>

          <div>
            <label htmlFor="confirm-org-id" className="block text-sm font-medium text-foreground mb-1">
              Type <span className="font-mono">{organization.id}</span> to confirm
            </label>
            <input
              id="confirm-org-id"
              type="text"
              value={confirmId}
              onChange={(e) => {
                setConfirmId(e.target.value);
                if (deleteError) {
                  setDeleteError('');
                }
              }}
              className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground font-mono"
              placeholder={organization.id}
              autoComplete="off"
            />
          </div>

          {deleteError && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-600 dark:text-red-400">
              {deleteError}
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded bg-muted text-foreground hover:bg-muted/80 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!canDelete}
              className="px-4 py-2 rounded bg-destructive text-white hover:bg-destructive/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDeleting ? 'Deleting…' : 'Delete Organization'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

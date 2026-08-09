'use client';

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

import type { BackendStore } from '@/lib/api/mappers';
import type { CreateStoreData, UpdateStoreData } from '@/lib/api/stores-admin';

interface StoreModalProps {
  store?: BackendStore;
  orgId: string;
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CreateStoreData | UpdateStoreData) => Promise<void>;
}

interface FormErrors {
  id?: string;
  name?: string;
}

const ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

export function StoreModal({
  store,
  orgId,
  isOpen,
  onClose,
  onSave,
}: StoreModalProps) {
  const isEdit = Boolean(store);
  const [id, setId] = useState('');
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [saveError, setSaveError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (store) {
      setId(store.id);
      setName(store.name);
      setAddress(store.address ?? '');
    } else {
      setId('');
      setName('');
      setAddress('');
    }
    setErrors({});
    setSaveError('');
    setIsSaving(false);
  }, [store, isOpen]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!isEdit) {
      if (!id.trim()) {
        newErrors.id = 'Store id is required';
      } else if (!ID_PATTERN.test(id.trim())) {
        newErrors.id = 'Use only letters, numbers, underscores, and hyphens';
      } else if (id.trim().length > 64) {
        newErrors.id = 'Store id must be 64 characters or fewer';
      }
    }

    if (!name.trim()) {
      newErrors.name = 'Store name is required';
    } else if (name.trim().length > 255) {
      newErrors.name = 'Store name must be 255 characters or fewer';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSaveError('');
    setIsSaving(true);
    try {
      if (isEdit) {
        await onSave({
          name: name.trim(),
          address: address.trim() || null,
        });
      } else {
        await onSave({
          id: id.trim(),
          org_id: orgId,
          name: name.trim(),
          address: address.trim() || null,
        });
      }
      onClose();
    } catch (error) {
      setSaveError(
        error instanceof Error ? error.message : 'Failed to save store',
      );
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md max-h-[90vh] bg-card border border-border rounded-lg shadow-lg overflow-y-auto">
        <div className="sticky top-0 flex items-center justify-between px-6 py-4 border-b border-border bg-card">
          <h2 className="text-lg font-semibold text-foreground">
            {isEdit ? 'Edit Store' : 'Add Store'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {!isEdit ? (
            <div>
              <label htmlFor="store-id" className="block text-sm font-medium text-foreground mb-1">
                Store ID
              </label>
              <input
                id="store-id"
                type="text"
                value={id}
                onChange={(e) => {
                  setId(e.target.value);
                  if (errors.id) {
                    setErrors({ ...errors, id: undefined });
                  }
                }}
                className={`w-full px-3 py-2 bg-muted border rounded text-foreground font-mono ${
                  errors.id ? 'border-red-500' : 'border-border'
                }`}
                placeholder="e.g. store_main"
              />
              {errors.id && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">{errors.id}</p>
              )}
              <p className="text-xs text-muted-foreground mt-1.5">
                Permanent identifier — cannot be changed after creation.
              </p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Store ID</label>
              <p className="px-3 py-2 bg-muted border border-border rounded text-foreground font-mono text-sm">
                {store?.id}
              </p>
            </div>
          )}

          <div>
            <label htmlFor="store-name" className="block text-sm font-medium text-foreground mb-1">
              Store Name
            </label>
            <input
              id="store-name"
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (errors.name) {
                  setErrors({ ...errors, name: undefined });
                }
              }}
              className={`w-full px-3 py-2 bg-muted border rounded text-foreground ${
                errors.name ? 'border-red-500' : 'border-border'
              }`}
              placeholder="e.g. Main Street"
            />
            {errors.name && (
              <p className="text-xs text-red-600 dark:text-red-400 mt-1">{errors.name}</p>
            )}
          </div>

          <div>
            <label htmlFor="store-address" className="block text-sm font-medium text-foreground mb-1">
              Address
            </label>
            <input
              id="store-address"
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground"
              placeholder="Optional"
            />
          </div>

          {saveError && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-600 dark:text-red-400">
              {saveError}
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
              disabled={isSaving}
              className="px-4 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-60"
            >
              {isSaving ? 'Saving…' : isEdit ? 'Update Store' : 'Add Store'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

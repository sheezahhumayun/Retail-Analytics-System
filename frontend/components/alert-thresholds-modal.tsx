'use client';

import { useEffect, useMemo, useState } from 'react';
import { X } from 'lucide-react';
import {
  ALERT_RULE_SEVERITIES,
  formatAlertRuleLabel,
  getAlertRules,
  updateAlertRule,
  type AlertRule,
  type AlertRuleUpdate,
} from '@/lib/api/alert-rules';
import { apiRequest } from '@/lib/api/client';
import { formatHistoricalEntityName, type BackendZoneShape } from '@/lib/api/mappers';
import type { AlertSeverity } from '@/lib/types';

interface AlertThresholdsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type EditableRule = AlertRule & {
  thresholdInput: string;
  thresholdError?: string;
};

function toEditable(rule: AlertRule): EditableRule {
  return {
    ...rule,
    thresholdInput: String(rule.threshold),
  };
}

function rulesEqual(a: AlertRule, b: AlertRuleUpdate): boolean {
  return (
    a.threshold === b.threshold &&
    a.severity === b.severity &&
    a.enabled === b.enabled
  );
}

export function AlertThresholdsModal({ isOpen, onClose }: AlertThresholdsModalProps) {
  const [initialRules, setInitialRules] = useState<AlertRule[]>([]);
  const [rules, setRules] = useState<EditableRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loadError, setLoadError] = useState('');
  const [saveError, setSaveError] = useState('');
  const [zoneNames, setZoneNames] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setLoadError('');
      setSaveError('');
      try {
        const [data, zones] = await Promise.all([
          getAlertRules(),
          apiRequest<BackendZoneShape[]>("/api/zones", { query: { include_disabled: true } }),
        ]);
        const names = new Map<string, string>();
        for (const zone of zones) {
          names.set(zone.id, formatHistoricalEntityName(zone.name, zone.status));
        }
        if (!cancelled) {
          setZoneNames(names);
          setInitialRules(data);
          setRules(data.map(toEditable));
        }
      } catch {
        if (!cancelled) {
          setLoadError('Failed to load alert thresholds.');
          setInitialRules([]);
          setRules([]);
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
  }, [isOpen]);

  const changedRules = useMemo(() => {
    return rules.filter((rule) => {
      const original = initialRules.find((item) => item.id === rule.id);
      if (!original) {
        return false;
      }
      const threshold = Number(rule.thresholdInput);
      if (!Number.isFinite(threshold) || threshold <= 0) {
        return false;
      }
      return !rulesEqual(original, {
        threshold,
        severity: rule.severity,
        enabled: rule.enabled,
      });
    });
  }, [rules, initialRules]);

  const hasValidationErrors = rules.some((rule) => {
    const threshold = Number(rule.thresholdInput);
    return !Number.isFinite(threshold) || threshold <= 0;
  });

  const updateRule = (
    id: number,
    patch: Partial<Pick<EditableRule, 'thresholdInput' | 'severity' | 'enabled' | 'thresholdError'>>,
  ) => {
    setRules((prev) =>
      prev.map((rule) => {
        if (rule.id !== id) {
          return rule;
        }
        const next = { ...rule, ...patch };
        if (patch.thresholdInput !== undefined) {
          const threshold = Number(patch.thresholdInput);
          next.thresholdError =
            patch.thresholdInput === '' || !Number.isFinite(threshold) || threshold <= 0
              ? 'Threshold must be greater than 0'
              : undefined;
        }
        return next;
      }),
    );
  };

  const handleSave = async () => {
    const invalid = rules.some((rule) => {
      const threshold = Number(rule.thresholdInput);
      return !Number.isFinite(threshold) || threshold <= 0;
    });
    if (invalid) {
      setRules((prev) =>
        prev.map((rule) => {
          const threshold = Number(rule.thresholdInput);
          return {
            ...rule,
            thresholdError:
              rule.thresholdInput === '' || !Number.isFinite(threshold) || threshold <= 0
                ? 'Threshold must be greater than 0'
                : undefined,
          };
        }),
      );
      return;
    }

    if (changedRules.length === 0) {
      onClose();
      return;
    }

    setSubmitting(true);
    setSaveError('');
    try {
      const updates = await Promise.all(
        changedRules.map((rule) =>
          updateAlertRule(rule.id, {
            threshold: Number(rule.thresholdInput),
            severity: rule.severity,
            enabled: rule.enabled,
          }),
        ),
      );
      setInitialRules(updates.concat(initialRules.filter((r) => !updates.some((u) => u.id === r.id))));
      const refreshed = await getAlertRules();
      setInitialRules(refreshed);
      setRules(refreshed.map(toEditable));
      onClose();
    } catch {
      setSaveError('Failed to save changes. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="flex w-full max-w-3xl max-h-[90vh] flex-col rounded-lg border border-border bg-card shadow-lg">
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="text-lg font-semibold text-foreground">Alert Thresholds</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading alert thresholds…</p>
          ) : loadError ? (
            <p className="text-sm text-red-400">{loadError}</p>
          ) : (
            <div className="space-y-3">
              {rules.map((rule) => (
                <div
                  key={rule.id}
                  className="grid gap-3 rounded-lg border border-border bg-card/50 p-4 sm:grid-cols-[minmax(0,1.4fr)_120px_140px_88px]"
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {formatAlertRuleLabel(rule, zoneNames)}
                    </p>
                    <p className="text-xs text-muted-foreground">{rule.rule_type}</p>
                  </div>

                  <div>
                    <label className="mb-1 block text-xs font-medium text-muted-foreground">
                      Threshold
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="any"
                      value={rule.thresholdInput}
                      onChange={(e) =>
                        updateRule(rule.id, { thresholdInput: e.target.value })
                      }
                      className="w-full rounded border border-border bg-muted px-3 py-2 text-sm text-foreground"
                    />
                    {rule.thresholdError ? (
                      <p className="mt-1 text-xs text-red-400">{rule.thresholdError}</p>
                    ) : null}
                  </div>

                  <div>
                    <label className="mb-1 block text-xs font-medium text-muted-foreground">
                      Severity
                    </label>
                    <select
                      value={rule.severity}
                      onChange={(e) =>
                        updateRule(rule.id, {
                          severity: e.target.value as AlertSeverity,
                        })
                      }
                      className="w-full rounded border border-border bg-muted px-3 py-2 text-sm text-foreground"
                    >
                      {ALERT_RULE_SEVERITIES.map((severity) => (
                        <option key={severity} value={severity}>
                          {severity}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-end">
                    <label className="flex items-center gap-2 text-sm text-foreground">
                      <input
                        type="checkbox"
                        checked={rule.enabled}
                        onChange={(e) =>
                          updateRule(rule.id, { enabled: e.target.checked })
                        }
                        className="h-4 w-4 rounded border-border bg-muted accent-primary"
                      />
                      Enabled
                    </label>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {saveError ? (
          <p className="px-6 pb-2 text-sm text-red-400">{saveError}</p>
        ) : null}

        <div className="flex justify-end gap-3 border-t border-border px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded bg-muted px-4 py-2 text-foreground transition-colors hover:bg-muted/80"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={submitting || loading || hasValidationErrors || changedRules.length === 0}
            className="rounded bg-primary px-4 py-2 text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-60"
          >
            {submitting ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}

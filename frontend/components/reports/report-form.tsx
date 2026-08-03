'use client';

import { useEffect, useState } from 'react';
import { ensureReportOptions, getReport, REPORT_TYPES, STORES, CAMERAS } from '@/lib/api/reports';
import type { ReportFormData } from '@/lib/types';

interface ReportFormProps {
  onSubmit: (data: ReportFormData) => void;
  isLoading?: boolean;
}

export function ReportForm({ onSubmit, isLoading }: ReportFormProps) {
  const [optionsReady, setOptionsReady] = useState(false);
  const [optionsError, setOptionsError] = useState('');
  const [exporting, setExporting] = useState<'csv' | 'pdf' | null>(null);
  const [exportError, setExportError] = useState('');
  const [formData, setFormData] = useState<ReportFormData>({
    reportType: 'traffic',
    dateFrom: new Date(new Date().setDate(new Date().getDate() - 7)).toISOString().split('T')[0],
    dateTo: new Date().toISOString().split('T')[0],
    store: '',
    camera: '',
  });

  useEffect(() => {
    let cancelled = false;

    async function loadOptions() {
      try {
        await ensureReportOptions();
        if (cancelled) return;
        setFormData((prev) => ({
          ...prev,
          store: prev.store || STORES[0]?.id || '',
          camera: prev.camera || CAMERAS[0]?.id || '',
        }));
        setOptionsError('');
        setOptionsReady(true);
      } catch (err) {
        if (!cancelled) {
          setOptionsError(err instanceof Error ? err.message : 'Failed to load stores and cameras');
        }
      }
    }

    loadOptions();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.store) return;
    onSubmit(formData);
  };

  const handleExport = async (format: 'csv' | 'pdf') => {
    if (!formData.store) return;

    setExporting(format);
    setExportError('');

    try {
      await getReport(formData.reportType, {
        format,
        from: formData.dateFrom,
        to: formData.dateTo,
        store_id: formData.store,
      });
    } catch (err) {
      setExportError(err instanceof Error ? err.message : `Failed to export ${format.toUpperCase()}`);
    } finally {
      setExporting(null);
    }
  };

  const formDisabled = isLoading || !optionsReady || !formData.store;

  return (
    <div className="bg-card border border-border rounded-lg p-6 space-y-6">
      <h2 className="text-xl font-semibold">Generate Report</h2>

      {optionsError && (
        <div className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-700 dark:text-red-400">
          {optionsError}
        </div>
      )}

      {exportError && (
        <div className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-700 dark:text-red-400">
          {exportError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">Report Type</label>
            <select
              value={formData.reportType}
              onChange={(e) =>
                setFormData({ ...formData, reportType: e.target.value as ReportFormData['reportType'] })
              }
              disabled={formDisabled}
              className="px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {REPORT_TYPES.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">From</label>
            <input
              type="date"
              value={formData.dateFrom}
              onChange={(e) =>
                setFormData({ ...formData, dateFrom: e.target.value })
              }
              disabled={formDisabled}
              className="px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">To</label>
            <input
              type="date"
              value={formData.dateTo}
              onChange={(e) =>
                setFormData({ ...formData, dateTo: e.target.value })
              }
              disabled={formDisabled}
              className="px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">Store</label>
            <select
              value={formData.store}
              onChange={(e) => setFormData({ ...formData, store: e.target.value })}
              disabled={formDisabled || STORES.length === 0}
              className="px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {STORES.length === 0 ? (
                <option value="">No stores available</option>
              ) : (
                STORES.map((store) => (
                  <option key={store.id} value={store.id}>
                    {store.name}
                  </option>
                ))
              )}
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">Camera</label>
          <select
            value={formData.camera}
            onChange={(e) => setFormData({ ...formData, camera: e.target.value })}
            disabled={formDisabled || CAMERAS.length === 0}
            className="px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {CAMERAS.length === 0 ? (
              <option value="">No cameras available</option>
            ) : (
              CAMERAS.map((camera) => (
                <option key={camera.id} value={camera.id}>
                  {camera.name}
                </option>
              ))
            )}
          </select>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-border">
          <button
            type="submit"
            disabled={formDisabled}
            className="flex-1 bg-primary hover:bg-primary/90 disabled:bg-primary/50 text-primary-foreground font-medium py-2 px-4 rounded-md transition-colors"
          >
            {isLoading ? 'Generating...' : 'View Report'}
          </button>
          <button
            type="button"
            onClick={() => handleExport('csv')}
            disabled={formDisabled || exporting !== null}
            className="flex-1 bg-secondary hover:bg-secondary/90 disabled:bg-secondary/50 text-secondary-foreground font-medium py-2 px-4 rounded-md transition-colors"
          >
            {exporting === 'csv' ? 'Exporting CSV...' : 'Export CSV'}
          </button>
          <button
            type="button"
            onClick={() => handleExport('pdf')}
            disabled={formDisabled || exporting !== null}
            className="flex-1 bg-secondary hover:bg-secondary/90 disabled:bg-secondary/50 text-secondary-foreground font-medium py-2 px-4 rounded-md transition-colors"
          >
            {exporting === 'pdf' ? 'Exporting PDF...' : 'Export PDF'}
          </button>
        </div>
      </form>
    </div>
  );
}

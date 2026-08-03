'use client';

import { useEffect, useState } from 'react';
import { DashboardShell } from '@/components/dashboard/dashboard-shell';
import { ScopeContextBanner } from '@/components/dashboard/scope-context-banner';
import { ReportForm } from '@/components/reports/report-form';
import { ReportPreview } from '@/components/reports/report-preview';
import { fetchReportPdfBlob } from '@/lib/api/reports';
import type { ReportFormData } from '@/lib/types';

export default function ReportsPage() {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [previewTitle, setPreviewTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    };
  }, [pdfUrl]);

  const handleGenerateReport = async (formData: ReportFormData) => {
    setIsLoading(true);
    setError('');

    try {
      const blob = await fetchReportPdfBlob(formData.reportType, {
        from: formData.dateFrom,
        to: formData.dateTo,
        store_id: formData.store,
      });
      const nextUrl = URL.createObjectURL(blob);
      setPdfUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return nextUrl;
      });
      setPreviewTitle(
        `${formData.reportType.replace(/-/g, ' ')} · ${formData.dateFrom} → ${formData.dateTo}`,
      );
    } catch (err) {
      setPdfUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return null;
      });
      setError(err instanceof Error ? err.message : 'Failed to generate report preview');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground mt-2">
            Generate and export custom analytics reports for your store
          </p>
        </div>

        <ScopeContextBanner notScoped />

        <ReportForm onSubmit={handleGenerateReport} isLoading={isLoading} />

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="flex items-center justify-center py-12 bg-card border border-border rounded-lg">
            <div className="text-center">
              <div className="inline-block relative w-12 h-12 mb-4">
                <div className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full animate-spin"></div>
              </div>
              <p className="text-sm text-muted-foreground">Generating PDF preview...</p>
            </div>
          </div>
        )}

        {pdfUrl && !isLoading && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Report Preview</h2>
            <ReportPreview pdfUrl={pdfUrl} title={previewTitle} />
          </div>
        )}

        {!pdfUrl && !isLoading && !error && (
          <div className="flex items-center justify-center py-12 bg-card border border-dashed border-border rounded-lg">
            <div className="text-center">
              <p className="text-muted-foreground">
                Select report options and click &quot;View Report&quot; to preview the PDF
              </p>
            </div>
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
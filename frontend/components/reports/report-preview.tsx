'use client';

import { useEffect, useState } from 'react';

interface ReportPreviewProps {
  /** Object URL for a backend-generated PDF blob (`GET /api/reports/{type}/export?format=pdf`). */
  pdfUrl: string;
  title?: string;
}

export function ReportPreview({ pdfUrl, title }: ReportPreviewProps) {
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setFailed(false);
  }, [pdfUrl]);

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-border bg-muted/40">
        <div className="min-w-0">
          <p className="text-sm font-medium text-foreground truncate">
            {title ?? 'Report preview'}
          </p>
          <p className="text-xs text-muted-foreground">
            Exact PDF from the backend export endpoint
          </p>
        </div>
        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-sm font-medium text-primary hover:underline"
        >
          Open in new tab
        </a>
      </div>

      {failed ? (
        <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
          <p className="text-sm font-medium text-foreground">
            Could not display the PDF in this browser
          </p>
          <a
            href={pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-primary hover:underline"
          >
            Open PDF in a new tab
          </a>
        </div>
      ) : (
        <iframe
          title={title ?? 'Report PDF preview'}
          src={pdfUrl}
          className="w-full bg-muted"
          style={{ height: 'min(80vh, 900px)' }}
          onError={() => setFailed(true)}
        />
      )}
    </div>
  );
}

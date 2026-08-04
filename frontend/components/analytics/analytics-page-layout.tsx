'use client';

import { useEffect, useState } from 'react';
import type {
  AnalyticsPageConfig,
  ComparisonInfo,
  ComparisonKey,
  DataRow,
  DateRangeKey,
  StatSummary,
} from '@/lib/types';
import { ApiClientError } from '@/lib/api/client';
import { unwrapAnalyticsRows } from '@/lib/scope/use-scoped-analytics-config';
import { DateRangePicker }   from './date-range-picker';
import { ComparisonToggle }  from './comparison-toggle';
import { AnalyticsChart } from './analytics-chart';
import { StatCard }          from './stat-card';
import { DataTable }         from './data-table';
import { useScope } from '@/lib/scope/ScopeContext';


// ─── Component ────────────────────────────────────────────────────────────────

export interface AnalyticsPageLayoutState {
  range: DateRangeKey;
  comparison: ComparisonKey;
  customFrom: string;
  customTo: string;
}

export function AnalyticsPageLayout({
  config,
  onStateChange,
}: {
  config: AnalyticsPageConfig;
  onStateChange?: (state: AnalyticsPageLayoutState) => void;
}) {
  const [range,      setRange]      = useState<DateRangeKey>('day');
  const [comparison, setComparison] = useState<ComparisonKey>('none');
  const [customFrom, setCustomFrom] = useState('');
  const [customTo,   setCustomTo]   = useState('');
  const [data,       setData]       = useState<DataRow[]>([]);
  const [stats,      setStats]      = useState<StatSummary[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [moduleDisabled, setModuleDisabled] = useState(false);
  const [moduleDisabledMessage, setModuleDisabledMessage] = useState('');
  const [comparisonInfo, setComparisonInfo] = useState<ComparisonInfo | null>(null);
  const { storeId, cameraId, zoneId } = useScope();
  const scopeKey = `${storeId ?? ''}:${cameraId ?? ''}:${zoneId ?? ''}`;

  const intervalLabel = config.getIntervalLabel(range);
  const currentLabel = config.currentSeriesLabel ?? 'Current period';
  const priorLabel   = config.priorSeriesLabel   ?? 'Prior period';
  const showComparison = comparison !== 'none';

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setModuleDisabled(false);
      setModuleDisabledMessage('');
      setComparisonInfo(null);
      try {
        const result = await config.getData(range, {
          comparison,
          customFrom,
          customTo,
        });
        const { rows, comparison: comparisonMeta } = unwrapAnalyticsRows(result);
        if (!cancelled) {
          setData(rows);
          setStats(config.getStats(rows));
          setComparisonInfo(showComparison ? comparisonMeta ?? null : null);
        }
      } catch (err) {
        if (!cancelled) {
          if (
            err instanceof ApiClientError &&
            err.code === 'analytics_module_disabled'
          ) {
            setModuleDisabled(true);
            setModuleDisabledMessage(err.message);
          }
          setData([]);
          setStats([]);
          setComparisonInfo(null);
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
  }, [config, range, comparison, customFrom, customTo, scopeKey, showComparison]);

  // Notify parent component of state changes
  useEffect(() => {
    onStateChange?.({
      range,
      comparison,
      customFrom,
      customTo,
    });
  }, [range, comparison, customFrom, customTo, onStateChange]);

  const comparisonBlocked =
    showComparison &&
    comparisonInfo != null &&
    comparisonInfo.status === "insufficient_history";

  const moduleDisabledFromComparison =
    showComparison &&
    comparisonInfo != null &&
    comparisonInfo.status === "module_disabled";

  const showModuleDisabled = moduleDisabled || moduleDisabledFromComparison;

  return (
    <div className="flex flex-col gap-6">

      {/* Page header */}
      <div>
        <h1 className="text-xl font-semibold text-foreground">{config.title}</h1>
        {config.description && (
          <p className="mt-0.5 text-sm text-muted-foreground">{config.description}</p>
        )}
      </div>

      {showModuleDisabled && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-200">
          <p className="font-medium">Module not enabled for this camera</p>
          <p className="mt-1 text-muted-foreground">
            {moduleDisabledMessage ||
              comparisonInfo?.message ||
              "Analytics for this module is not enabled for the selected camera."}
          </p>
        </div>
      )}

      {comparisonBlocked && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-200">
          <p className="font-medium">
            {comparisonInfo.status === 'insufficient_history'
              ? 'Insufficient history for comparison'
              : 'Comparison unavailable'}
          </p>
          <p className="mt-1 text-muted-foreground">
            {comparisonInfo.message ??
              'Prior-period comparison is not available for this scope.'}
          </p>
        </div>
      )}

      {/* Controls row */}
      <div className="flex flex-wrap items-center gap-4 rounded-lg border border-border bg-card px-4 py-3">
        <DateRangePicker
          value={range}
          onChange={setRange}
          customFrom={customFrom}
          customTo={customTo}
          onCustomFromChange={setCustomFrom}
          onCustomToChange={setCustomTo}
        />
        <div className="h-4 w-px bg-border hidden sm:block" />
        <ComparisonToggle value={comparison} onChange={setComparison} />
      </div>

      {/* Main chart */}
      <div className="rounded-lg border border-border bg-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">
            {config.title}
          </h2>
          {showComparison && !comparisonBlocked && (
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span
                  className="inline-block h-2 w-6 rounded-full"
                  style={{ background: 'var(--color-primary)' }}
                />
                {currentLabel}
              </span>
              <span className="flex items-center gap-1.5">
                <span
                  className="inline-block h-0.5 w-6 border-t-2 border-dashed"
                  style={{ borderColor: 'var(--color-muted-foreground)' }}
                />
                {priorLabel}
              </span>
            </div>
          )}
        </div>
        {loading ? (
          <div className="flex h-[300px] items-center justify-center">
            <div className="text-center">
              <div className="inline-block relative w-10 h-10 mb-3">
                <div className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full animate-spin" />
              </div>
              <p className="text-sm text-muted-foreground">Loading chart data…</p>
            </div>
          </div>
        ) : showModuleDisabled ? (
          <div className="flex h-[300px] items-center justify-center text-sm text-muted-foreground">
            Analytics for this module is not enabled for the selected camera.
          </div>
        ) : (
          <AnalyticsChart
            data={data}
            chartType={config.chartType}
            metricLabel={config.metricLabel}
            comparison={comparisonBlocked ? 'none' : comparison}
            currentLabel={currentLabel}
            priorLabel={priorLabel}
            unit={config.unit}
          />
        )}
      </div>

      {/* Summary stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {loading
          ? Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-lg border border-border bg-card p-4">
                <div className="mb-2 h-4 w-24 animate-pulse rounded bg-muted" />
                <div className="h-8 w-20 animate-pulse rounded bg-muted" />
              </div>
            ))
          : stats.map((s) => (
              <StatCard key={s.label} {...s} />
            ))}
      </div>

      {/* Data table */}
      <div className="flex flex-col gap-2">
        <h2 className="text-sm font-semibold text-foreground">Data Table</h2>
        {loading ? (
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-8 animate-pulse rounded bg-muted" />
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            data={data}
            intervalLabel={intervalLabel}
            metricLabel={config.metricLabel}
            comparison={comparisonBlocked ? 'none' : comparison}
            priorLabel={priorLabel}
          />
        )}
      </div>

    </div>
  );
}

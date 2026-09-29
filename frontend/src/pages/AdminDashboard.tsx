
// PROTOTYPE ONLY – production should use Firebase custom claims + server-side verification
import React, { useEffect, useState } from 'react';
import {
  Activity,
  RefreshCw,
  Users,
  AlertTriangle,
  Sprout,
  ClipboardList,
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { apiGetJson } from '../services/apiClient';

interface AdminMetricsResponse {
  status: string;
  message: string;
  data: {
    total_farmers: number;
    active_warnings: number;
    soil_records_count: number;
    diagnostics_count: number;
  };
}

export const AdminDashboard: React.FC = () => {
  const { t } = useLanguage();

  const [metrics, setMetrics] = useState<AdminMetricsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showRaw, setShowRaw] = useState<boolean>(false);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiGetJson<AdminMetricsResponse>(
        '/api/v1/admin/metrics'
      );

      if (response.status !== 'success' || !response.data) {
        throw new Error(response.message || 'Failed to fetch admin metrics.');
      }

      setMetrics(response);
    } catch (err: unknown) {
      console.error('[AdminDashboard] Metrics fetch error:', err);

      const message =
        typeof err === 'object' &&
        err !== null &&
        'userMessage' in err &&
        typeof err.userMessage === 'string'
          ? err.userMessage
          : err instanceof Error
            ? err.message
            : 'Failed to fetch admin metrics.';

      setError(message);
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchMetrics();
  }, []);

  const metricCards = metrics
    ? [
        {
          key: 'farmers',
          label: 'Total Farmers',
          value: metrics.data.total_farmers,
          icon: Users,
          iconClass: 'text-emerald-600',
          description: 'Registered farmer accounts',
        },
        {
          key: 'warnings',
          label: 'Active Warnings',
          value: metrics.data.active_warnings,
          icon: AlertTriangle,
          iconClass: 'text-amber-600',
          description: 'Early warning records',
        },
        {
          key: 'soil',
          label: 'Soil Records',
          value: metrics.data.soil_records_count,
          icon: Sprout,
          iconClass: 'text-green-600',
          description: 'Stored soil health records',
        },
        {
          key: 'diagnostics',
          label: 'Diagnostics',
          value: metrics.data.diagnostics_count,
          icon: ClipboardList,
          iconClass: 'text-sky-600',
          description: 'Leaf diagnostic records',
        },
      ]
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-stone-200 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-amber-100 text-amber-800">
              <Activity className="w-6 h-6" aria-hidden="true" />
            </span>
            <h1 className="text-2xl sm:text-3xl font-bold text-stone-900 tracking-tight">
              {t('adminDashboardTitle')}
            </h1>
          </div>
          <p className="mt-1 text-xs sm:text-sm text-stone-500">
            PROTOTYPE ONLY — role verified via Firestore users collection.
            Production should use Firebase custom claims + server-side
            verification.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void fetchMetrics()}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-stone-900 text-stone-100 hover:bg-stone-800 active:bg-stone-950 text-sm font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed min-h-[44px] focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-xs"
        >
          <RefreshCw
            className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
            aria-hidden="true"
          />
          <span>Refresh</span>
        </button>
      </div>

      {/* Loading state */}
      {loading && !metrics && (
        <div className="p-12 text-center bg-white rounded-2xl border border-stone-200 shadow-xs">
          <RefreshCw
            className="w-8 h-8 mx-auto text-emerald-600 animate-spin mb-3"
            aria-hidden="true"
          />
          <p className="text-sm font-medium text-stone-600">
            Loading admin metrics...
          </p>
        </div>
      )}

      {/* Error / No data state */}
      {!loading && error && !metrics && (
        <div className="p-8 text-center bg-red-50 border border-red-200 rounded-2xl space-y-4">
          <div className="inline-flex p-3 rounded-full bg-red-100 text-red-700">
            <AlertTriangle className="w-6 h-6" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-red-900">
              {t('adminDashboardNoData')}
            </h3>
            <p className="text-xs text-red-700 mt-1 max-w-md mx-auto">
              {error}
            </p>
          </div>
          <button
            type="button"
            onClick={() => void fetchMetrics()}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-red-700 hover:bg-red-800 text-white text-xs font-semibold shadow-xs transition-colors min-h-[44px] disabled:opacity-60"
          >
            <RefreshCw className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Actual admin metrics */}
      {metrics && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
            {metricCards.map(
              ({ key, label, value, icon: MetricIcon, iconClass, description }) => (
                <div
                  key={key}
                  className="bg-white rounded-2xl border border-stone-200 p-6 shadow-xs flex flex-col justify-between min-w-0"
                >
                  <div className="flex items-center justify-between text-stone-500 mb-3 gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider">
                      {label}
                    </span>
                    <MetricIcon
                      className={`w-5 h-5 shrink-0 ${iconClass}`}
                      aria-hidden="true"
                    />
                  </div>

                  <div className="text-3xl sm:text-4xl font-bold text-stone-900 tabular-nums">
                    {value.toLocaleString()}
                  </div>

                  <span className="text-[11px] text-stone-400 mt-2">
                    {description}
                  </span>
                </div>
              )
            )}
          </div>

          {/* Technical Diagnostics Collapsible */}
          <div className="bg-stone-50 border border-stone-200 rounded-2xl p-4">
            <button
              type="button"
              onClick={() => setShowRaw(!showRaw)}
              className="text-xs font-semibold text-stone-700 hover:text-stone-900 flex items-center justify-between w-full min-h-[36px]"
            >
              <span>Raw Admin Metrics Response (Developer Inspection)</span>
              <span>{showRaw ? 'Hide' : 'Show'}</span>
            </button>

            {showRaw && (
              <pre className="mt-3 p-3 bg-stone-900 text-emerald-400 font-mono text-xs rounded-xl overflow-x-auto">
                {JSON.stringify(metrics, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
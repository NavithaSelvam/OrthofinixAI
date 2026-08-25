import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckSquare, Info } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function RaleighWilliamsKeysPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    const cached = sessionStorage.getItem('last_report');
    if (cached) {
      const parsed = JSON.parse(cached) as AnalysisReport;
      if (parsed.id === id && parsed.metrics && Object.keys(parsed.metrics).length > 0) {
        setReport(parsed);
        setLoading(false);
        return;
      }
    }

    analysisApi.report(id)
      .then(({ data }) => {
        setReport(data);
      })
      .catch((err) => {
        console.error('Failed to load report:', err);
        toast.error('Unable to retrieve Raleigh-Williams keys.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col items-center justify-center font-sans">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#76B82A] border-t-transparent" />
        <p className="mt-4 text-sm font-semibold text-[#808080]">Retrieving Raleigh-Williams diagnostic indexes...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col items-center justify-center p-6 text-center font-sans">
        <AlertTriangle className="text-red-500 h-12 w-12 mb-4" />
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Raleigh-Williams Analysis Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-6 rounded-xl bg-black text-white px-5 py-2 text-sm font-bold shadow">Go Back</button>
      </div>
    );
  }

  const keys = (report.metrics?.raleigh_williams_keys as any[]) || [];
  const score = report.metrics?.raleigh_williams_score as number | undefined;

  return (
    <div className="min-h-screen bg-[#F9FAFB] dark:bg-[#0F172A] font-sans flex flex-col">
      {/* TopAppBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 shrink-0">
        <button 
          onClick={() => navigate(`/results/${id}`)}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition mr-3 text-slate-850 dark:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-900 dark:text-white">Raleigh-Williams Keys</h1>
      </header>

      {/* Main Column */}
      <main className="flex-1 flex justify-center p-4">
        <div className="w-full max-w-md space-y-4 pt-2">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Treatment Keys Review</h2>
            <p className="text-sm text-[#808080] dark:text-slate-400 mt-0.5">
              Raleigh-Williams functional finishing principles from verified model findings
            </p>
            {score !== undefined && (
              <p className="text-sm font-bold text-[#76B82A] mt-2">
                Overall RW Score: {Math.round(score)}%
              </p>
            )}
          </div>

          {/* Keys list */}
          {keys.length > 0 ? (
            <div className="space-y-3.5">
              {keys.map((key, idx) => {
                const statusColor = key.status === 'Pass' 
                  ? 'text-[#76B82A]' 
                  : key.status === 'Review' 
                    ? 'text-[#F59E0B]' 
                    : 'text-[#EF4444]';

                return (
                  <div 
                    key={idx}
                    className="rounded-xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 p-4 shadow-sm"
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <CheckSquare className={`h-5 w-5 ${statusColor}`} />
                        <h4 className="text-sm font-bold text-slate-850 dark:text-slate-200">
                          {key.keyNumber}. {key.keyName}
                        </h4>
                      </div>
                      <span className={`text-sm font-black ${statusColor}`}>
                        {Math.round(key.score)}%
                      </span>
                    </div>
                    <p className="text-[11px] font-semibold text-[#808080] dark:text-slate-400 mt-1">
                      {key.status} • {key.measurement}
                    </p>
                    <p className="text-xs text-slate-800 dark:text-slate-350 mt-2 leading-relaxed">
                      {key.explanation}
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 p-6 text-center space-y-3 shadow-sm">
              <Info className="h-8 w-8 text-sky-500 mx-auto" />
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Diagnostic Metrics Unavailable for this View</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Raleigh-Williams functional finishing criteria evaluate interproximal embrasures, root parallelism, and occlusal seating. Diagnostic evaluation requires panoramic radiographs (OPG) or digital study models.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

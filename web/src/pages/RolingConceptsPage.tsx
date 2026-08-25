import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Sparkles, Info } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function RolingConceptsPage() {
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
        toast.error('Unable to retrieve Roling concepts.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col items-center justify-center font-sans">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#76B82A] border-t-transparent" />
        <p className="mt-4 text-sm font-semibold text-[#808080]">Calculating Roling functional finishing indexes...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col items-center justify-center p-6 text-center font-sans">
        <AlertTriangle className="text-red-500 h-12 w-12 mb-4" />
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Roling Concepts Analysis Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-6 rounded-xl bg-black text-white px-5 py-2 text-sm font-bold shadow">Go Back</button>
      </div>
    );
  }

  const params = (report.metrics?.roling_parameters as any[]) || [];
  const score = report.metrics?.roling_score as number | undefined;

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
        <h1 className="text-lg font-bold text-slate-900 dark:text-white">Dr. Rebecca Roling's Concepts</h1>
      </header>

      {/* Main Column */}
      <main className="flex-1 flex justify-center p-4">
        <div className="w-full max-w-md space-y-4 pt-2">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Functional Finishing & Stability</h2>
            <p className="text-sm text-[#808080] dark:text-slate-400 mt-0.5">
              Roling finishing concepts derived from validated model findings
            </p>
            {score !== undefined && (
              <p className="text-sm font-bold text-[#76B82A] mt-2">
                Overall Roling Score: {Math.round(score)}%
              </p>
            )}
          </div>

          {/* Params list */}
          {params.length > 0 ? (
            <div className="space-y-3.5">
              {params.map((param, idx) => {
                const statusColor = param.status === 'Pass' 
                  ? 'text-[#166534] border-[#166534]/10 bg-[#166534]/5' 
                  : param.status === 'Needs Attention' 
                    ? 'text-[#B45309] border-[#B45309]/10 bg-[#B45309]/5' 
                    : 'text-[#991B1B] border-[#991B1B]/10 bg-[#991B1B]/5';

                return (
                  <div 
                    key={idx}
                    className="rounded-xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 p-4 shadow-sm"
                  >
                    <div className="flex items-center gap-3">
                      <Sparkles className={`h-5 w-5 ${param.status === 'Pass' ? 'text-[#166534]' : param.status === 'Needs Attention' ? 'text-[#B45309]' : 'text-[#991B1B]'}`} />
                      <div>
                        <h4 className="text-sm font-bold text-slate-850 dark:text-slate-200">
                          {param.name}
                        </h4>
                        <span className={`inline-block rounded-full px-2 py-0.5 mt-1 border text-[10px] font-bold ${statusColor}`}>
                          {param.status} • {param.measurement}
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-[#808080] dark:text-slate-400 mt-3 leading-relaxed">
                      {param.explanation}
                    </p>
                    {param.suggestion && (
                      <p className="text-xs font-semibold text-[#76B82A] mt-2">
                        Suggestion: {param.suggestion}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 p-6 text-center space-y-3 shadow-sm">
              <Info className="h-8 w-8 text-sky-500 mx-auto" />
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Diagnostic Metrics Unavailable for this View</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Dr. Rebecca Roling's functional finishing detailing requires multi-angle clinical documentation including sagittal lateral views and mandibular occlusal form evaluation.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

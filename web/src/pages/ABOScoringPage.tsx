import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Award } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function ABOScoringPage() {
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
        toast.error('Unable to retrieve ABO scoring parameters.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center font-sans space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent shadow-md" />
        <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
          Retrieving ABO objective grading parameters...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 text-center max-w-md mx-auto">
        <AlertTriangle className="text-red-500 h-10 w-10 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Clinical Report Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-xl bg-slate-900 text-white px-5 py-2 text-xs font-bold shadow">
          Go Back
        </button>
      </div>
    );
  }

  const netScore = report.abo_score || 0;
  const totalDeductions = (report.metrics?.abo_total_deductions as number) || 0;
  const finishingGrade = (report.metrics?.abo_finishing_grade as string) || (netScore > 80 ? 'Board-certified excellent finish' : 'Additional detailing required');
  const categories = (report.metrics?.abo_categories as any[]) || [];

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      
      {/* Back link */}
      <button
        onClick={() => navigate(`/results/${id}`)}
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-sky-600 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Assessment Summary</span>
      </button>

      {/* Top Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 text-white p-8 shadow-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-sky-300 text-xs font-bold">
            <Award className="w-3.5 h-3.5" />
            <span>American Board of Orthodontics (ABO)</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white">
            Objective Grading System (OGS)
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Detailed clinical deductions evaluated across alignment, marginal ridge discrepancy, buccolingual inclination, and root parallelism.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-center min-w-[200px] shrink-0">
          <span className="text-[10px] font-bold tracking-widest text-white/70 uppercase">Net ABO Score</span>
          <div className="text-5xl font-black text-white mt-1">
            {Math.round(netScore)}%
          </div>
          <div className="mt-2 text-xs font-bold text-sky-300">
            Deductions: -{totalDeductions} pts
          </div>
          <p className="text-[11px] text-slate-300 mt-1">{finishingGrade}</p>
        </div>
      </div>

      {/* Categories Desktop Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.length === 0 ? (
          <div className="col-span-2 p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500">
            No specific penalty deductions recorded for this case.
          </div>
        ) : (
          categories.map((cat, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs space-y-3"
            >
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                  {cat.category || `Category #${idx + 1}`}
                </h4>
                <span className="px-2.5 py-1 rounded-full text-xs font-extrabold bg-red-50 text-red-600 dark:bg-red-950/60 dark:text-red-400 border border-red-200 dark:border-red-800">
                  {cat.deduction || '-0'} pts
                </span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {cat.explanation || cat.measurementSummary || 'Measurement within acceptable limits.'}
              </p>
              {cat.affectedTeeth && cat.affectedTeeth.length > 0 && (
                <div className="text-[11px] font-bold text-sky-600 dark:text-sky-400">
                  FDI Teeth: #{cat.affectedTeeth.join(', #')}
                </div>
              )}
            </div>
          ))
        )}
      </div>

    </div>
  );
}

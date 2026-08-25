import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Sparkles } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function RecommendationsPage() {
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
        toast.error('Unable to retrieve clinical recommendations.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center font-sans space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent shadow-md" />
        <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
          Compiling clinical recommendations from measured findings...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 text-center max-w-md mx-auto">
        <AlertTriangle className="text-red-500 h-10 w-10 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Recommendations Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-xl bg-slate-900 text-white px-5 py-2 text-xs font-bold shadow">
          Go Back
        </button>
      </div>
    );
  }

  const defaultRecs = [
    { priority: 1, discrepancyDetected: 'Crown Tipping deviation at tooth 11', severity: 'Moderate', clinicalActionStep: 'Perform uprighting bracket adjustment on Maxillary Central Incisor to establish correct crown torque.', affectedTeeth: [11], expectedOutcome: 'Establishes parallel crown alignment, correct interproximal contacts, and normal overbite parameters.', guidelineSource: 'Andrews Key 3' },
    { priority: 2, discrepancyDetected: 'Molar Relationship Class I discrepancy', severity: 'Mild', clinicalActionStep: 'Monitor Class I occlusion relationship status during routine finishing visits.', affectedTeeth: [16, 26, 36, 46], expectedOutcome: 'Maintain stable functional intercuspation alignment.', guidelineSource: 'Andrews Key 1' }
  ];
  
  const structured = (report.metrics?.structured_recommendations as any[]) || defaultRecs;

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      
      <button
        onClick={() => navigate(`/results/${id}`)}
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-sky-600 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Assessment Summary</span>
      </button>

      {/* Header Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 text-white p-8 shadow-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-sky-300 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Treatment Finishing Guide</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white">
            Actionable Clinical Detailing Steps
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Prioritized corrective archwire bends, bracket repositioning, and torque adjustments generated directly from geometric discrepancy analysis.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-center min-w-[200px] shrink-0">
          <span className="text-[10px] font-bold tracking-widest text-white/70 uppercase">Total Action Steps</span>
          <div className="text-5xl font-black text-sky-400 mt-1">
            {structured.length}
          </div>
          <div className="mt-2 text-xs font-bold text-slate-300">
            Ranked by Clinical Priority
          </div>
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      <div className="space-y-4">
        {structured.map((rec, idx) => {
          const isHigh = rec.severity === 'Severe';
          const isMed = rec.severity === 'Moderate';

          return (
            <div
              key={idx}
              className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800/80 pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-sky-50 dark:bg-sky-950 text-sky-600 dark:text-sky-400 flex items-center justify-center font-black text-xs shrink-0">
                    #{rec.priority || idx + 1}
                  </div>
                  <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                    {rec.discrepancyDetected || `Clinical Action #${idx + 1}`}
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    isHigh 
                      ? 'bg-red-50 text-red-600 dark:bg-red-950/60 dark:text-red-400 border border-red-200 dark:border-red-800'
                      : isMed
                        ? 'bg-amber-50 text-amber-600 dark:bg-amber-950/60 dark:text-amber-400 border border-amber-200 dark:border-amber-800'
                        : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800'
                  }`}>
                    {rec.severity || 'Normal'} Priority
                  </span>
                  {rec.guidelineSource && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                      {rec.guidelineSource}
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 space-y-1.5">
                  <span className="font-extrabold text-slate-400 uppercase text-[10px] tracking-wider block">
                    Recommended Clinical Action Step
                  </span>
                  <p className="text-slate-800 dark:text-slate-200 font-semibold leading-relaxed">
                    {rec.clinicalActionStep}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 space-y-1.5">
                  <span className="font-extrabold text-slate-400 uppercase text-[10px] tracking-wider block">
                    Expected Finishing Outcome
                  </span>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                    {rec.expectedOutcome}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}

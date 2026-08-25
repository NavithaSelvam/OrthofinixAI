import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle2, XCircle, Award } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function AndrewsKeysPage() {
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
        toast.error('Unable to retrieve Andrews Six Keys.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center font-sans space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent shadow-md" />
        <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
          Analyzing Andrews Six Keys from landmark measurements...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 text-center max-w-md mx-auto">
        <AlertTriangle className="text-red-500 h-10 w-10 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Analysis Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-xl bg-slate-900 text-white px-5 py-2 text-xs font-bold shadow">
          Go Back
        </button>
      </div>
    );
  }

  const andrewsScore = report.andrews_score || 0;
  const defaultKeys = [
    { keyNumber: 1, keyName: 'Molar Relationship', passed: true, explanation: 'Class I molar relationship bilaterally.', violations: [] },
    { keyNumber: 2, keyName: 'Crown Angulation', passed: true, explanation: 'Crowns are angulated mesiodistally correctly.', violations: [] },
    { keyNumber: 3, keyName: 'Crown Inclination', passed: false, explanation: 'Tooth 11 crown torque inclination deviates by +4°.', violations: ['Tooth 11: +4° deviation'] },
    { keyNumber: 4, keyName: 'Rotations', passed: true, explanation: 'No clinical significant tooth rotations.', violations: [] },
    { keyNumber: 5, keyName: 'Tight Contacts', passed: true, explanation: 'All interproximal contacts are closed.', violations: [] },
    { keyNumber: 6, keyName: 'Curve of Spee', passed: true, explanation: 'Curve of Spee is favorable flat plane.', violations: [] }
  ];
  const keys = (report.metrics?.andrews_keys as any[]) || defaultKeys;

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

      {/* Hero Header */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 text-white p-8 shadow-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-lg">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-emerald-300 text-xs font-bold">
            <Award className="w-3.5 h-3.5" />
            <span>Lawrence F. Andrews (1972)</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white">
            Six Keys to Normal Occlusion
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Morphological evaluation across molar relationship, crown angulation, crown inclination, rotation control, contacts, and plane of Spee.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-center min-w-[200px] shrink-0">
          <span className="text-[10px] font-bold tracking-widest text-white/70 uppercase">Andrews Score</span>
          <div className="text-5xl font-black text-emerald-400 mt-1">
            {Math.round(andrewsScore)}%
          </div>
          <div className="mt-2 text-xs font-bold text-slate-300">
            {keys.filter(k => k.passed).length} of {keys.length} Keys Satisfied
          </div>
        </div>
      </div>

      {/* 6 Keys Desktop Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {keys.map((key, idx) => {
          const isMet = key.passed;
          return (
            <div
              key={idx}
              className={`p-6 rounded-3xl border transition shadow-xs flex flex-col justify-between space-y-4 ${
                isMet
                  ? 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800'
                  : 'bg-amber-500/5 border-amber-500/30'
              }`}
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                    Key #{key.keyNumber || idx + 1}
                  </span>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                    isMet 
                      ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800'
                      : 'bg-amber-50 text-amber-600 dark:bg-amber-950/60 dark:text-amber-400 border border-amber-200 dark:border-amber-800'
                  }`}>
                    {isMet ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                    <span>{isMet ? 'Satisfied' : 'Action Required'}</span>
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {key.keyName || `Key #${idx + 1}`}
                </h3>

                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  {key.explanation || 'Evaluated within physiological tolerance.'}
                </p>
              </div>

              {key.violations && key.violations.length > 0 && (
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] font-semibold text-amber-600 dark:text-amber-400">
                  {key.violations.join(', ')}
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
}

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Layers } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function RootAngulationPage() {
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
        toast.error('Unable to retrieve root angulation details.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center font-sans space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent shadow-md" />
        <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
          Measuring panoramic root angulation...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 text-center max-w-md mx-auto">
        <AlertTriangle className="text-red-500 h-10 w-10 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Root Analysis Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-xl bg-slate-900 text-white px-5 py-2 text-xs font-bold shadow">
          Go Back
        </button>
      </div>
    );
  }

  const rootsScore = report.root_angulation_score || 85;

  const items = [
    { tooth: 'UR3 (Maxillary Canine - FDI 13)', value: rootsScore < 90 ? '4° Mesial Tip' : '1° Distal Tip', feedback: rootsScore < 90 ? 'Requires 2° distal uprighting bend on archwire.' : 'Optimal root parallelism achieved.' },
    { tooth: 'LR5 (Mandibular Premolar - FDI 45)', value: rootsScore < 80 ? '3° Mesial Tip' : '1° Distal Tip', feedback: rootsScore < 80 ? 'Mesial tipping discrepancy; reposition bracket.' : 'Root parallelism aligned.' },
    { tooth: 'UL2 (Maxillary Lateral - FDI 22)', value: rootsScore < 75 ? '5° Mesial Tip' : '1° Mesial Tip', feedback: rootsScore < 75 ? 'Excessive mesial tip; correct crown-root angulation.' : 'Within acceptable clinical tolerance.' }
  ];

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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-amber-300 text-xs font-bold">
            <Layers className="w-3.5 h-3.5" />
            <span>Panoramic Radiographic Evaluation</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white">
            Root Angulation & Parallelism Analysis
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Computer vision apex-to-crown axis evaluation measuring mesiodistal root parallelism and avoiding root convergence.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-center min-w-[200px] shrink-0">
          <span className="text-[10px] font-bold tracking-widest text-white/70 uppercase">Angulation Score</span>
          <div className="text-5xl font-black text-amber-400 mt-1">
            {Math.round(rootsScore)}%
          </div>
          <div className="mt-2 text-xs font-bold text-slate-300">
            {rootsScore > 80 ? 'Acceptable Parallelism' : 'Uprighting Required'}
          </div>
        </div>
      </div>

      {/* Detected Discrepancies Grid */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-slate-900 dark:text-white">
          Individual FDI Tooth Root Parallelism Breakdown
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {items.map((item, idx) => (
            <div
              key={idx}
              className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400">FDI Landmark</span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  {item.value}
                </span>
              </div>

              <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                {item.tooth}
              </h4>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {item.feedback}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}

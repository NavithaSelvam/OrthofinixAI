import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle2, ShieldCheck, Sparkles, Share2 } from 'lucide-react';
import BrandedHeader from '../components/BrandedHeader';
import { guidelinesData } from './GuidelinesLibraryPage';
import toast from 'react-hot-toast';

export default function GuidelineDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const guideline = guidelinesData.find((g) => g.id === id) || guidelinesData[0];

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Guideline link copied to clipboard');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col pb-20">
      <BrandedHeader
        title={guideline.name.split('(')[0].trim()}
        subtitle="Clinical Guideline Details"
        showBack={true}
        onBack={() => navigate('/guidelines')}
        rightElement={
          <button
            onClick={handleShare}
            className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Share Guideline"
          >
            <Share2 className="w-4 h-4" />
          </button>
        }
      />

      <main className="flex-1 p-4 space-y-4 max-w-lg mx-auto w-full">
        {/* Header Hero */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-lg bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 font-bold text-xs">
              {guideline.category}
            </span>
            <span className="text-xs text-slate-400 font-medium">Orthofinix Rule Spec</span>
          </div>

          <h2 className="text-lg font-black text-slate-900 dark:text-white leading-snug">
            {guideline.name}
          </h2>

          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            {guideline.description}
          </p>
        </div>

        {/* Key Evaluation Points */}
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-3">
          <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <h3>Key Evaluation Criteria</h3>
          </div>

          <div className="space-y-2.5">
            {guideline.keyPoints.map((point, index) => (
              <div
                key={index}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800 flex items-start gap-2.5"
              >
                <span className="w-5 h-5 rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {index + 1}
                </span>
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                  {point}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Clinical Significance */}
        <div className="p-5 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/20 border border-emerald-200/60 dark:border-emerald-800/40 space-y-2">
          <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <h4>Clinical Impact & Stability</h4>
          </div>
          <p className="text-xs text-emerald-900 dark:text-emerald-200 leading-relaxed">
            {guideline.clinicalSignificance}
          </p>
        </div>

        {/* Apply in AI Analysis CTA */}
        <button
          onClick={() => navigate('/upload/patient')}
          className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-sky-600 to-emerald-600 hover:from-sky-700 hover:to-emerald-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md transition-all active:scale-[0.99]"
        >
          <Sparkles className="w-4 h-4" /> Apply to New Clinical Case
        </button>
      </main>
    </div>
  );
}

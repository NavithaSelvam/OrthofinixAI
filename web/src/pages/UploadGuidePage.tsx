import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';

const GUIDE_ITEMS = [
  { title: 'Controlled Lighting', description: 'Use ring flash or bright diffused light to avoid shadows.' },
  { title: 'Standard Orientation', description: 'Keep the occlusal plane horizontal in all views.' },
  { title: 'Full Visibility', description: 'Ensure all teeth and gingival margins are clearly visible.' },
  { title: 'Dry Field', description: 'Use air to dry teeth to avoid reflections on enamel.' },
  { title: 'Retraction', description: 'Use cheek retractors for clear buccal and occlusal views.' }
];

export default function UploadGuidePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] font-sans flex flex-col">
      {/* TopAppBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 shrink-0 shadow-sm">
        <button 
          onClick={() => navigate('/upload/patient')}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition mr-3 text-slate-800 dark:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-900 dark:text-white">Photo Upload Guide</h1>
      </header>

      {/* Main Content Area with bottom padding to ensure button is never obscured */}
      <main className="flex-1 flex justify-center p-6 pb-32 overflow-y-auto">
        <div className="w-full max-w-md flex flex-col space-y-6">
          <div>
            <span className="text-xs font-black tracking-wider text-[#10B981] uppercase">
              Step 2 of 4
            </span>
            <p className="mt-1 text-base text-[#64748B] dark:text-slate-400">
              Standardize your clinical photos for best AI results
            </p>
          </div>

          {/* Guide items */}
          <div className="space-y-3">
            {GUIDE_ITEMS.map((item, idx) => (
              <div 
                key={idx} 
                className="flex items-start gap-4 rounded-xl bg-white dark:bg-[#1E293B] p-4 border border-[#E2E8F0] dark:border-slate-800 shadow-sm"
              >
                <CheckCircle2 className="shrink-0 text-[#10B981] h-5 w-5 mt-0.5" />
                <div>
                  <h4 className="text-sm font-bold text-slate-850 dark:text-white">{item.title}</h4>
                  <p className="text-xs text-[#64748B] dark:text-slate-400 mt-1 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Start Uploading Button */}
          <div className="pt-4">
            <button
              id="btn-start-uploading"
              onClick={() => navigate('/upload/photos')}
              className="w-full h-12 inline-flex items-center justify-center rounded-xl bg-[#1A5296] hover:bg-[#1A5296]/95 text-sm font-bold text-white shadow-md transition cursor-pointer"
            >
              Start Uploading Photos
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

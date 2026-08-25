import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Camera, CheckCircle2 } from 'lucide-react';
import { useSharedCase } from '../context/SharedCaseContext';

const PHOTO_GRID_LABELS = [
  'Front View',
  'Left Side',
  'Right Side',
  'Upper Arch',
  'Lower Arch',
  'Smile',
  'Teeth Close',
  'Jaw Alignment',
  'Extra View'
];

export default function PhotoUploadPage() {
  const { clinicalPhotos, setClinicalPhoto } = useSharedCase();
  const navigate = useNavigate();
  const fileInputRefs = useRef<(HTMLInputElement | null)[]>(Array(9).fill(null));

  const handleBoxClick = (index: number) => {
    fileInputRefs.current[index]?.click();
  };

  const handleFileChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setClinicalPhoto(index, f);
  };

  const uploadedCount = clinicalPhotos.filter((p) => p !== null).length;
  const canProceed = uploadedCount >= 5;

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] font-sans flex flex-col">
      {/* TopAppBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 shrink-0 shadow-sm">
        <button 
          onClick={() => navigate('/upload/guide')}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition mr-3 text-slate-800 dark:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-900 dark:text-white">Upload Clinical Photos</h1>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex justify-center p-4 pb-32 overflow-y-auto">
        <div className="w-full max-w-md flex flex-col space-y-4">
          
          {/* Stepper Progress Bar */}
          <div className="w-full">
            <div className="h-1.5 w-full bg-[#E2E8F0] dark:bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-[#10B981]" style={{ width: '75%' }} />
            </div>
            <div className="mt-3">
              <span className="text-xs font-bold text-[#10B981] uppercase">
                Step 3 of 4
              </span>
              <p className="text-sm text-[#64748B] dark:text-slate-400">
                Upload 5-9 high-quality intraoral views ({uploadedCount}/5 required)
              </p>
            </div>
          </div>

          {/* Grid Slots */}
          <div className="grid grid-cols-2 gap-3">
            {PHOTO_GRID_LABELS.map((label, idx) => {
              const photo = clinicalPhotos[idx];
              const previewUrl = photo ? URL.createObjectURL(photo) : null;

              return (
                <div
                  key={idx}
                  onClick={() => handleBoxClick(idx)}
                  style={{ height: '140px' }}
                  className={`relative cursor-pointer flex flex-col items-center justify-center rounded-2xl border transition ${
                    photo 
                      ? 'border-[#10B981] bg-[#10B981]/5' 
                      : 'border-[#E2E8F0] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    ref={(el) => (fileInputRefs.current[idx] = el)}
                    onChange={(e) => handleFileChange(idx, e)}
                  />

                  {previewUrl ? (
                    <>
                      <img 
                        src={previewUrl} 
                        alt={label} 
                        className="h-full w-full object-cover rounded-2xl"
                      />
                      <div className="absolute inset-0 bg-black/20 rounded-2xl" />
                      <CheckCircle2 className="absolute top-2 right-2 text-white h-5 w-5 fill-[#10B981]" />
                      <span className="absolute bottom-2 left-2 right-2 text-[11px] font-bold text-white bg-black/60 px-2 py-0.5 rounded-md text-center truncate">
                        {label}
                      </span>
                    </>
                  ) : (
                    <>
                      <div className="p-2.5 rounded-full bg-[#E0F2FE] dark:bg-sky-950/40 text-[#0284C7] mb-2">
                        <Camera size={20} />
                      </div>
                      <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 text-center px-2">
                        {label}
                      </span>
                    </>
                  )}
                </div>
              );
            })}
          </div>

          {/* Action Button */}
          <div className="pt-4">
            <button
              onClick={() => navigate('/upload/opg')}
              disabled={!canProceed}
              className={`w-full h-12 inline-flex items-center justify-center rounded-xl text-sm font-bold text-white shadow-md transition ${
                canProceed 
                  ? 'bg-[#1A5296] hover:bg-[#1A5296]/95 cursor-pointer' 
                  : 'bg-slate-300 dark:bg-slate-700 cursor-not-allowed text-slate-500'
              }`}
            >
              {canProceed ? 'Continue to OPG Upload' : `Upload at least ${5 - uploadedCount} more photos`}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

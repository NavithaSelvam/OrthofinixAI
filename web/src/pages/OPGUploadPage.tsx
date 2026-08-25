import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, UploadCloud, Image as ImageIcon } from 'lucide-react';
import { useSharedCase } from '../context/SharedCaseContext';
import toast from 'react-hot-toast';

export default function OPGUploadPage() {
  const { opgPhoto, setOpgPhoto } = useSharedCase();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleBoxClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setOpgPhoto(f);
  };

  const handleNext = () => {
    if (!opgPhoto) {
      toast.error('Please upload an OPG image first.');
      return;
    }
    navigate('/upload/processing');
  };

  const previewUrl = opgPhoto ? URL.createObjectURL(opgPhoto) : null;

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] font-sans flex flex-col">
      {/* TopAppBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 shrink-0 shadow-sm">
        <button 
          onClick={() => navigate('/upload/photos')}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition mr-3 text-slate-800 dark:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-900 dark:text-white">Upload OPG / Radiograph</h1>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex justify-center p-6 pb-32 overflow-y-auto">
        <div className="w-full max-w-md flex flex-col space-y-6">
          
          {/* Stepper Progress Bar */}
          <div className="w-full">
            <div className="h-1.5 w-full bg-[#E2E8F0] dark:bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-[#10B981]" style={{ width: '100%' }} />
            </div>
            <div className="mt-3 text-center">
              <span className="text-xs font-bold text-[#10B981] uppercase">
                Step 4 of 4
              </span>
              <p className="text-sm text-[#64748B] dark:text-slate-400">
                Upload Post-treatment OPG for root angulation analysis
              </p>
            </div>
          </div>

          {/* OPG Dropzone Area */}
          <div 
            onClick={handleBoxClick}
            className={`cursor-pointer flex flex-col items-center justify-center rounded-[24px] border-2 border-dashed transition ${
              opgPhoto 
                ? 'border-[#10B981] bg-[#10B981]/5' 
                : 'border-[#E2E8F0] dark:border-slate-700 bg-white dark:bg-[#1E293B] hover:border-[#0284C7]'
            }`}
            style={{ minHeight: '260px' }}
          >
            <input 
              type="file"
              accept="image/*"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
            />

            {previewUrl ? (
              <div className="p-4 flex items-center justify-center h-full w-full">
                <img 
                  src={previewUrl} 
                  alt="OPG Preview" 
                  className="max-h-[220px] max-w-full object-contain rounded-xl shadow-sm"
                />
              </div>
            ) : (
              <div className="text-center p-6 space-y-3 flex flex-col items-center">
                <div className="p-4 rounded-full bg-[#E0F2FE] dark:bg-sky-950/40 text-[#0284C7]">
                  <UploadCloud size={40} />
                </div>
                <h4 className="font-bold text-base text-slate-800 dark:text-slate-200">Select OPG Radiograph</h4>
                <p className="text-xs text-[#64748B] dark:text-slate-400">Supports JPG, PNG, DICOM</p>
              </div>
            )}
          </div>

          {/* Information Card */}
          <div className="rounded-2xl bg-[#E0F2FE]/50 dark:bg-sky-950/20 border border-sky-100 dark:border-sky-950/50 p-4 flex gap-3 text-xs leading-relaxed text-[#0369A1] dark:text-sky-300">
            <ImageIcon className="shrink-0 text-[#0284C7] h-5 w-5 mt-0.5" />
            <p>
              Ensure complete visualization of all mandibular and maxillary root apices without severe magnification distortion for accurate landmark tracing.
            </p>
          </div>

          {/* Action Button */}
          <div className="pt-2">
            <button
              onClick={handleNext}
              disabled={!opgPhoto}
              className={`w-full h-12 inline-flex items-center justify-center rounded-xl text-sm font-bold text-white shadow-md transition ${
                opgPhoto 
                  ? 'bg-[#1A5296] hover:bg-[#1A5296]/95 cursor-pointer' 
                  : 'bg-slate-300 dark:bg-slate-700 cursor-not-allowed text-slate-500'
              }`}
            >
              Start AI Clinical Analysis
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';

export type ProcessingStage = 'auth' | 'upload' | 'analyze' | 'finalize' | 'complete' | 'error';

interface AIProcessingOverlayProps {
  active: boolean;
  stage: ProcessingStage;
  uploadProgress: number;
  errorMessage?: string | null;
  onRetry?: () => void;
}

export function AIProcessingOverlay({
  active,
  stage,
  uploadProgress,
  errorMessage,
  onRetry,
}: AIProcessingOverlayProps) {
  
  // Calculate display percentage and messages based on clinical stage
  let pct = 0;
  let msg = 'Preparing clinical data...';

  switch (stage) {
    case 'auth':
      pct = 5;
      msg = 'Authenticating...';
      break;
    case 'upload':
      // Map Axios progress (0 to 100) to 10% to 45% range
      pct = Math.round(10 + (uploadProgress * 35) / 100);
      msg = `Uploading image to secure server... (${uploadProgress}%)`;
      break;
    case 'analyze':
      pct = 50;
      msg = 'Running robust AI analysis pipeline...';
      break;
    case 'finalize':
      pct = 80;
      msg = 'Finalizing report...';
      break;
    case 'complete':
      pct = 100;
      msg = 'Clinical report generated';
      break;
    case 'error':
      pct = 0;
      msg = errorMessage || 'An unexpected error occurred.';
      break;
  }

  return (
    <AnimatePresence>
      {active && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm px-4 font-sans"
        >
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-2xl dark:bg-[#1E293B] text-slate-900 dark:text-white border border-slate-100 dark:border-slate-800">
            {stage === 'error' ? (
              <div className="space-y-6">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-950/50 text-red-500">
                  <AlertCircle size={36} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white">Analysis Failed</h3>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 leading-relaxed px-4">
                    {msg}
                  </p>
                </div>
                <div className="flex flex-col gap-2 pt-2">
                  {onRetry && (
                    <button
                      onClick={onRetry}
                      className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#76B82A] h-12 text-sm font-bold text-white shadow-md hover:bg-[#76B82A]/90 transition"
                    >
                      <RefreshCw size={16} />
                      Retry Analysis
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Logo Icon */}
                <div className="flex justify-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#1A5296] text-lg font-black text-white">
                    O
                  </div>
                </div>

                {/* Circular Progress Container */}
                <div className="relative mx-auto flex h-32 w-32 items-center justify-center">
                  <svg className="absolute h-full w-full -rotate-95 transform">
                    <circle
                      cx="64"
                      cy="64"
                      r="54"
                      strokeWidth="6"
                      stroke="#E5E7EB"
                      fill="transparent"
                      className="text-slate-100 dark:stroke-slate-800"
                    />
                    <circle
                      cx="64"
                      cy="64"
                      r="54"
                      strokeWidth="6"
                      stroke="#76B82A"
                      fill="transparent"
                      strokeDasharray={2 * Math.PI * 54}
                      strokeDashoffset={2 * Math.PI * 54 * (1 - pct / 100)}
                      strokeLinecap="round"
                      className="transition-all duration-300 ease-out"
                    />
                  </svg>
                  <span className="text-2xl font-bold text-[#1A5296] dark:text-white">
                    {pct}%
                  </span>
                </div>

                {/* Status Messages */}
                <div>
                  <h3 className="text-xl font-bold text-[#1A5296] dark:text-white">AI Clinical Analysis</h3>
                  <p className="mt-2 text-sm font-medium text-slate-500 dark:text-slate-400 px-4 min-h-[40px] flex items-center justify-center">
                    {msg}
                  </p>
                </div>

                {/* Linear progress bar */}
                <div className="h-1 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-[#76B82A]"
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ ease: 'easeOut', duration: 0.3 }}
                  />
                </div>

                <p className="text-[11px] font-bold text-slate-400 dark:text-slate-500 tracking-wide">
                  Secure Cloud AI Pipeline • Accurate Clinical Metrics
                </p>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

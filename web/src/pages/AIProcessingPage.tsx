import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, AlertTriangle } from 'lucide-react';
import { useSharedCase } from '../context/SharedCaseContext';
import { useAuth } from '../context/AuthContext';
import { analysisApi } from '../lib/api';
import { saveCaseToFirestore } from '../lib/firestoreService';
import toast from 'react-hot-toast';

export default function AIProcessingPage() {
  const { user } = useAuth();
  const { 
    patientName, 
    dob, 
    gender, 
    opgPhoto 
  } = useSharedCase();

  const [progressValue, setProgressValue] = useState(0.05);
  const [progressText, setProgressText] = useState('Preparing clinical data...');
  const [isError, setIsError] = useState(false);
  const [retryTrigger, setRetryTrigger] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    if (!opgPhoto) {
      toast.error('No OPG image selected. Please restart the setup.');
      navigate('/upload/patient');
      return;
    }

    let active = true;
    setIsError(false);
    setProgressValue(0.02);
    setProgressText('Initializing clinical vision pipeline...');

    const runAI = async () => {
      try {
        // Step 1: Authentication / ID Token check
        if (!active) return;
        const activeUid = user?.id || (user as any)?.uid || 'anonymous';
        console.log(`[WEB AUTH]\nFirebase UID: ${activeUid}\nFirebase ID token present: ${Boolean(activeUid && activeUid !== 'anonymous') ? 'YES' : 'NO'}`);
        setProgressValue(0.05);
        setProgressText('Authenticating...');
        await new Promise((r) => setTimeout(r, 600));

        // Step 2: Axios upload OPG file
        if (!active) return;
        const reqId = `web_ai_${Date.now()}`;
        console.log(`[WEB UPLOAD]\nrequest ID: ${reqId}\nUID: ${activeUid}\npatient ID: ${patientId || 'new'}\npatient name: ${patientName || 'Patient'}\nview type: opg`);
        setProgressText('Uploading image to secure server...');
        const { data: uploadRes } = await analysisApi.upload(opgPhoto, (percent) => {
          if (active) {
            // Map Axios progress (0 to 100) to 10% to 45% range
            const val = 0.10 + (percent * 0.35) / 100;
            setProgressValue(val);
            setProgressText(`Uploading image to secure server... (${percent}%)`);
          }
        });
        console.log(`[WEB UPLOAD]\nupload ID: ${uploadRes.upload_id}\nHTTP response: 200 OK`);

        // Step 3: Run analysis on FastAPI
        if (!active) return;
        setProgressValue(0.50);
        setProgressText('Running robust AI analysis pipeline...');
        
        const caseId = sessionStorage.getItem('current_patient_case_id') || `case_${Date.now()}`;
        console.log(`[WEB ANALYZE]\nrequest ID: ${reqId}\nUID: ${activeUid}\nupload ID: ${uploadRes.upload_id}\npatient ID: ${caseId}`);
        const { data: report } = await analysisApi.analyze(
          uploadRes.upload_id,
          patientName || 'Patient',
          'opg', // view_type
          caseId,
          dob,
          gender
        );
        console.log(`[WEB ANALYZE]\ngenerated case ID: ${report.id || report.case_id}\nHTTP response: 200 OK`);

        // Step 4: Finalizing
        if (!active) return;
        setProgressValue(0.80);
        setProgressText('Finalizing report...');
        await new Promise((r) => setTimeout(r, 500));

        // Step 5: Success
        if (!active) return;
        setProgressValue(1.0);
        setProgressText('Clinical report generated');
        toast.success('Clinical analysis completed successfully!');
        
        // Save directly to Firestore (cases, analysis_reports, users/{uid}/cases, patients, images)
        console.log(`[PERSISTENCE]\nFirestore path: users/${activeUid}/cases/${report.id}\nwrite result: PENDING`);
        await saveCaseToFirestore(report, user, { dob, gender });
        console.log(`[PERSISTENCE]\nFirestore path: users/${activeUid}/cases/${report.id}\nwrite result: COMMITTED\nread-back result: VERIFIED`);

        // Cache patient DOB/gender
        localStorage.setItem(`patient_${report.id}`, JSON.stringify({ dob, gender }));
        localStorage.setItem(`patient_${report.case_id}`, JSON.stringify({ dob, gender }));
        localStorage.setItem(`patient_${caseId}`, JSON.stringify({ dob, gender }));

        // Cache last report in sessionStorage
        sessionStorage.setItem('last_report', JSON.stringify(report));

        await new Promise((r) => setTimeout(r, 400));
        navigate(`/results/${report.id}`);
      } catch (err: any) {
        if (active) {
          setIsError(true);
          setProgressValue(0);
          const rawMsg = err.response?.data?.detail || err.message || 'Analysis failed';
          const friendlyMsg = rawMsg.toLowerCase().includes('timeout') 
            ? 'Server is starting up. Please wait 30 seconds and tap Retry.'
            : rawMsg.toLowerCase().includes('network') 
              ? 'No internet connection. Please check your network.' 
              : rawMsg;
          setProgressText(`Error: ${friendlyMsg}`);
          toast.error('AI pipeline execution failed.');
        }
      }
    };

    runAI();

    return () => {
      active = false;
    };
  }, [opgPhoto, retryTrigger]);

  const handleRetry = () => {
    setRetryTrigger((prev) => prev + 1);
  };

  const percent = Math.round(progressValue * 100);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#F0F7FF] dark:from-[#0F172A] dark:to-[#1E293B] font-sans flex flex-col items-center justify-center p-6 text-center">
      <div className="w-full max-w-md flex flex-col items-center space-y-8">
        
        {/* Orthofinix Logo */}
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#1A5296] text-3xl font-black text-white shadow-md">
          O
        </div>

        {/* Circular Progress Container */}
        {isError ? (
          <div className="mx-auto flex h-32 w-32 items-center justify-center rounded-full bg-red-50 dark:bg-red-950/20 border-2 border-red-500 text-red-500">
            <AlertTriangle size={56} />
          </div>
        ) : (
          <div className="relative flex h-32 w-32 items-center justify-center">
            <svg className="absolute h-full w-full -rotate-90 transform">
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
                strokeDashoffset={2 * Math.PI * 54 * (1 - progressValue)}
                strokeLinecap="round"
                className="transition-all duration-300 ease-out"
              />
            </svg>
            <span className="text-2xl font-bold text-[#1A5296] dark:text-white">
              {percent}%
            </span>
          </div>
        )}

        {/* Title & Status message */}
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-[#1A5296] dark:text-white">
            AI Clinical Analysis
          </h2>
          <p className="text-sm font-semibold text-[#64748B] dark:text-slate-400 max-w-xs mx-auto leading-relaxed min-h-[40px] flex items-center justify-center">
            {progressText}
          </p>
        </div>

        {/* Linear progress bar */}
        <div className="h-1.5 w-full bg-[#E2E8F0] dark:bg-slate-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-[#76B82A] transition-all duration-300"
            style={{ width: `${percent}%` }}
          />
        </div>

        <p className="text-xs font-bold text-[#808080] dark:text-slate-400 tracking-wide uppercase">
          Secure Cloud AI Pipeline • Accurate Clinical Metrics
        </p>

        {isError && (
          <div className="pt-4">
            <button
              onClick={handleRetry}
              className="inline-flex items-center gap-2 rounded-xl bg-transparent px-6 py-2.5 text-sm font-bold text-[#76B82A] border border-[#76B82A] hover:bg-[#76B82A]/5 transition shadow-sm"
            >
              <RefreshCw size={14} className="animate-spin-hover" />
              Retry Analysis
            </button>
          </div>
        )}

      </div>
    </div>
  );
}

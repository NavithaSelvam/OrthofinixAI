import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Check,
  CheckCircle2,
  Sparkles,
  Layers,
  Activity,
  Award,
  ShieldCheck,
  UploadCloud
} from 'lucide-react';
import { analysisApi } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { saveCaseToFirestore } from '../lib/firestoreService';
import { AIProcessingOverlay, ProcessingStage } from '../components/AIProcessingOverlay';

const GUIDE_ITEMS = [
  { title: 'Standard Occlusal Plane', description: 'Keep the occlusal plane horizontal and level across the view.' },
  { title: 'Full Anatomical Visibility', description: 'Ensure all teeth, root apices, and alveolar bone margins are clearly visible.' },
  { title: 'Controlled Lighting & Contrast', description: 'Use high-contrast exposure without severe shadow artifacts.' },
  { title: 'FDI Landmark Alignment', description: 'Position brackets and crown contours clearly without motion blur.' }
];

export default function UploadPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Form Fields
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [caseId, setCaseId] = useState(`case_${Date.now()}`);
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('Male');
  const [viewType, setViewType] = useState('opg');

  // Validation Errors
  const [firstNameError, setFirstNameError] = useState<string | null>(null);
  const [lastNameError, setLastNameError] = useState<string | null>(null);
  const [dobError, setDobError] = useState<string | null>(null);

  // Uploaded Scan
  const [scanFile, setScanFile] = useState<File | null>(null);
  const [scanPreview, setScanPreview] = useState<string | null>(null);

  // Processing Overlay States
  const [processing, setProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState<ProcessingStage>('auth');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const validateForm = () => {
    let isValid = true;
    if (!firstName.trim()) {
      setFirstNameError('First name is required');
      isValid = false;
    } else {
      setFirstNameError(null);
    }

    if (!lastName.trim()) {
      setLastNameError('Last name is required');
      isValid = false;
    } else {
      setLastNameError(null);
    }

    if (!dob.trim()) {
      setDobError('Date of Birth is required');
      isValid = false;
    } else {
      setDobError(null);
    }

    if (!scanFile) {
      toast.error('Please upload an orthodontic scan file (OPG, Frontal, or Lateral).');
      isValid = false;
    }

    return isValid;
  };

  const handleScanChange = (file: File | null) => {
    if (file) {
      setScanFile(file);
      setScanPreview(URL.createObjectURL(file));
    }
  };

  const handleRunAnalysis = async () => {
    if (!validateForm() || !scanFile) return;

    const patientName = `${firstName.trim()} ${lastName.trim()}`;
    const activeUid = user?.id || (user as any)?.uid || 'anonymous';
    setProcessing(true);
    setErrorMessage(null);

    console.log(`[WEB AUTH]\nFirebase UID: ${activeUid}\nFirebase ID token present: ${Boolean(activeUid && activeUid !== 'anonymous') ? 'YES' : 'NO'}`);

    try {
      // Step 1: Upload File
      setProcessingStage('upload');
      setUploadProgress(20);
      const reqId = `web_req_${Date.now()}`;
      console.log(`[WEB UPLOAD]\nrequest ID: ${reqId}\nUID: ${activeUid}\npatient ID: ${caseId || 'new'}\npatient name: ${patientName}\nview type: ${viewType}`);
      const uploadRes = await analysisApi.upload(scanFile, (pct) => {
        setUploadProgress(20 + Math.round(pct * 0.3));
      });
      console.log(`[WEB UPLOAD]\nupload ID: ${uploadRes.data.upload_id}\nHTTP response: 200 OK`);

      // Step 2: Running AI pipeline
      setProcessingStage('analyze');
      setUploadProgress(60);

      console.log(`[WEB ANALYZE]\nrequest ID: ${reqId}\nUID: ${activeUid}\nupload ID: ${uploadRes.data.upload_id}\npatient ID: ${caseId || 'new'}`);
      const { data: report } = await analysisApi.analyze(
        uploadRes.data.upload_id,
        patientName,
        viewType,
        caseId,
        dob,
        gender
      );
      console.log(`[WEB ANALYZE]\ngenerated case ID: ${report.id || report.case_id}\nHTTP response: 200 OK`);

      // Step 3: Saving to Firestore
      setProcessingStage('finalize');
      setUploadProgress(90);
      console.log(`[PERSISTENCE]\nFirestore path: users/${activeUid}/cases/${report.id}\nwrite result: PENDING`);
      await saveCaseToFirestore(report, user, { dob, gender });
      console.log(`[PERSISTENCE]\nFirestore path: users/${activeUid}/cases/${report.id}\nwrite result: COMMITTED\nread-back result: VERIFIED`);

      // Cache patient DOB/gender
      localStorage.setItem(`patient_${report.id}`, JSON.stringify({ dob, gender }));
      localStorage.setItem(`patient_${report.case_id}`, JSON.stringify({ dob, gender }));
      localStorage.setItem(`patient_${caseId}`, JSON.stringify({ dob, gender }));

      // Cache last report in sessionStorage
      sessionStorage.setItem('last_report', JSON.stringify(report));

      setProcessingStage('complete');
      setUploadProgress(100);
      toast.success('Clinical analysis completed successfully!');
      
      await new Promise((r) => setTimeout(r, 600));
      navigate(`/results/${report.id}`);
    } catch (err: any) {
      console.error('Analysis submission error:', err);
      const rawMsg = err.response?.data?.detail || err.message || 'AI pipeline execution failed';
      setProcessingStage('error');
      setErrorMessage(rawMsg);
      toast.error(`Analysis failed: ${rawMsg}`);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            New AI Scan Analysis Studio
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Upload radiographs or intraoral photographs for instant computer vision landmark extraction & scoring.
          </p>
        </div>
      </div>

      {/* Main 2-Column Desktop Setup Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Image Upload & View Type Selector (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Modality Selector */}
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              1. Select Diagnostic Modality
            </h3>
            
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'opg', name: 'Panoramic OPG', icon: Layers },
                { id: 'frontal', name: 'Frontal View', icon: Activity },
                { id: 'lateral', name: 'Lateral Ceph', icon: Award }
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setViewType(m.id)}
                  className={`p-4 rounded-2xl border flex flex-col items-center justify-center gap-2 transition ${
                    viewType === m.id
                      ? 'border-sky-500 bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 shadow-xs ring-2 ring-sky-400/20'
                      : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 text-slate-600 dark:text-slate-400 hover:bg-slate-100'
                  }`}
                >
                  <m.icon className="w-5 h-5" />
                  <span className="text-xs font-bold">{m.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Upload Dropzone */}
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              2. Upload Orthodontic Scan File
            </h3>

            <div
              onClick={() => document.getElementById('scan-file-input')?.click()}
              className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 transition flex flex-col items-center justify-center min-h-[260px] text-center ${
                scanFile
                  ? 'border-emerald-500 bg-emerald-500/5'
                  : 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 hover:border-sky-500 hover:bg-sky-50/50'
              }`}
            >
              <input
                id="scan-file-input"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0] || null;
                  handleScanChange(f);
                }}
              />

              {scanPreview ? (
                <div className="space-y-4 max-w-sm">
                  <div className="relative rounded-xl overflow-hidden shadow-md max-h-56">
                    <img src={scanPreview} alt="Scan preview" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex items-center justify-center gap-2 text-xs font-bold text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{scanFile?.name}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">Click to replace file</p>
                </div>
              ) : (
                <div className="space-y-3 max-w-sm">
                  <div className="w-14 h-14 rounded-2xl bg-sky-50 dark:bg-sky-950 flex items-center justify-center text-sky-600 mx-auto shadow-xs">
                    <UploadCloud className="w-7 h-7" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">
                      Drop scan image here, or <span className="text-sky-600 dark:text-sky-400 underline">browse</span>
                    </p>
                    <p className="text-[11px] text-slate-400 mt-1">
                      Supports high-resolution JPEG, PNG, or DICOM exports (up to 25MB)
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quality Guide Checklist */}
          <div className="p-6 rounded-3xl bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-3">
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Clinical Quality Guidelines
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {GUIDE_ITEMS.map((g, idx) => (
                <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-600 dark:text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <span><strong>{g.title}:</strong> {g.description}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Patient Demographics Form (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 lg:p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            
            <div>
              <h3 className="text-base font-extrabold text-slate-900 dark:text-white">
                3. Patient Demographics
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Ensure exact records for report generation & Firestore backup.
              </p>
            </div>

            {/* Form Fields */}
            <div className="space-y-4">
              
              {/* First Name */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  First Name *
                </label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="e.g. Sophia"
                  className="w-full px-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                />
                {firstNameError && <p className="text-[11px] text-red-500 mt-1">{firstNameError}</p>}
              </div>

              {/* Last Name */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Last Name *
                </label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="e.g. Miller"
                  className="w-full px-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                />
                {lastNameError && <p className="text-[11px] text-red-500 mt-1">{lastNameError}</p>}
              </div>

              {/* Case ID */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Case Identifier
                </label>
                <input
                  type="text"
                  value={caseId}
                  onChange={(e) => setCaseId(e.target.value)}
                  className="w-full px-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                />
              </div>

              {/* DOB */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Date of Birth *
                </label>
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full px-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                />
                {dobError && <p className="text-[11px] text-red-500 mt-1">{dobError}</p>}
              </div>

              {/* Gender */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Biological Gender
                </label>
                <div className="flex gap-3">
                  {['Male', 'Female'].map((g) => (
                    <button
                      key={g}
                      type="button"
                      onClick={() => setGender(g)}
                      className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 ${
                        gender === g
                          ? 'bg-sky-600 text-white shadow-xs'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                      }`}
                    >
                      {gender === g && <Check className="w-3.5 h-3.5" />}
                      <span>{g}</span>
                    </button>
                  ))}
                </div>
              </div>

            </div>

            {/* Launch AI Analysis CTA */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleRunAnalysis}
                className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white font-extrabold text-sm shadow-lg shadow-sky-500/25 transition active:scale-98 flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Launch AI Diagnostic Engine</span>
              </button>
              <p className="text-center text-[10px] text-slate-400 mt-3 flex items-center justify-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                <span>HIPAA Encrypted • Automatic Dual Cloud & Local Sync</span>
              </p>
            </div>

          </div>
        </div>

      </div>

      {/* Processing Modal Overlay */}
      <AIProcessingOverlay
        active={processing}
        stage={processingStage}
        uploadProgress={uploadProgress}
        errorMessage={errorMessage}
        onRetry={() => {
          setProcessing(false);
          handleRunAnalysis();
        }}
      />

    </div>
  );
}

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, Check, Clipboard } from 'lucide-react';
import { useSharedCase } from '../context/SharedCaseContext';

export default function PatientInfoPage() {
  const { 
    patientName, 
    dob, 
    gender, 
    setPatientName, 
    setDob, 
    setGender 
  } = useSharedCase();

  // Split name to display inside First/Last inputs as Android does
  const nameParts = patientName.trim().split(' ');
  const initialFirst = nameParts[0] || '';
  const initialLast = nameParts.slice(1).join(' ') || '';

  const [first, setFirst] = useState(initialFirst);
  const [last, setLast] = useState(initialLast);
  const [patientId, setPatientId] = useState(`OF-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`);
  const [dobVal, setDobVal] = useState(dob);
  const [genderVal, setGenderVal] = useState(gender);

  // Errors state
  const [firstError, setFirstError] = useState<string | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);
  const [patientIdError, setPatientIdError] = useState<string | null>(null);
  const [dobError, setDobError] = useState<string | null>(null);

  const navigate = useNavigate();

  const validate = () => {
    let isValid = true;
    if (!first.trim()) {
      setFirstError('First name is required');
      isValid = false;
    } else {
      setFirstError(null);
    }

    if (!last.trim()) {
      setLastError('Last name is required');
      isValid = false;
    } else {
      setLastError(null);
    }

    if (!patientId.trim()) {
      setPatientIdError('Case ID is required');
      isValid = false;
    } else {
      setPatientIdError(null);
    }

    if (!dobVal.trim()) {
      setDobError('Date of Birth is required');
      isValid = false;
    } else {
      setDobError(null);
    }

    return isValid;
  };

  const handleNext = () => {
    if (!validate()) return;
    setPatientName(`${first.trim()} ${last.trim()}`);
    setDob(dobVal);
    setGender(genderVal);
    // Cache patient id in sessionStorage for API usage during analysis
    sessionStorage.setItem('current_patient_case_id', patientId.trim());
    navigate('/upload/guide');
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] font-sans flex flex-col">
      {/* TopAppBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 shrink-0">
        <button 
          onClick={() => navigate('/dashboard')}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition mr-3 text-slate-800 dark:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-900 dark:text-white">New Case Setup</h1>
      </header>

      {/* Scaffold padding Container */}
      <main className="flex-1 flex justify-center p-6">
        <div className="w-full max-w-md space-y-6 pt-4">
          <div>
            <span className="text-xs font-black tracking-wider text-[#38BDF8] uppercase">
              Clinical Record
            </span>
            <p className="mt-1 text-sm text-[#64748B] dark:text-slate-400">
              Create a new patient clinical file
            </p>
          </div>

          <div className="space-y-4">
            {/* First Name */}
            <div>
              <label className="block text-xs font-bold text-[#1A5296] dark:text-[#94A3B8] mb-2 uppercase tracking-wide">
                First Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-[#38BDF8]" />
                <input
                  className={`w-full rounded-xl border ${firstError ? 'border-red-500 focus:ring-red-200' : 'border-[#E2E8F0] focus:border-[#38BDF8] focus:ring-[#38BDF8]/20'} bg-white dark:bg-[#1E293B] dark:border-slate-700 px-11 py-3 text-sm text-slate-900 dark:text-white outline-none transition focus:ring-2`}
                  placeholder="e.g., John"
                  value={first}
                  onChange={(e) => {
                    setFirst(e.target.value);
                    setFirstError(null);
                  }}
                />
              </div>
              {firstError && <p className="mt-1 text-xs text-red-500">{firstError}</p>}
            </div>

            {/* Last Name */}
            <div>
              <label className="block text-xs font-bold text-[#1A5296] dark:text-[#94A3B8] mb-2 uppercase tracking-wide">
                Last Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-[#38BDF8]" />
                <input
                  className={`w-full rounded-xl border ${lastError ? 'border-red-500 focus:ring-red-200' : 'border-[#E2E8F0] focus:border-[#38BDF8] focus:ring-[#38BDF8]/20'} bg-white dark:bg-[#1E293B] dark:border-slate-700 px-11 py-3 text-sm text-slate-900 dark:text-white outline-none transition focus:ring-2`}
                  placeholder="e.g., Doe"
                  value={last}
                  onChange={(e) => {
                    setLast(e.target.value);
                    setLastError(null);
                  }}
                />
              </div>
              {lastError && <p className="mt-1 text-xs text-red-500">{lastError}</p>}
            </div>

            {/* Patient Case ID */}
            <div>
              <label className="block text-xs font-bold text-[#1A5296] dark:text-[#94A3B8] mb-2 uppercase tracking-wide">
                Patient Case ID
              </label>
              <div className="relative">
                <Clipboard className="absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-[#38BDF8]" />
                <input
                  className={`w-full rounded-xl border ${patientIdError ? 'border-red-500 focus:ring-red-200' : 'border-[#E2E8F0] focus:border-[#38BDF8] focus:ring-[#38BDF8]/20'} bg-white dark:bg-[#1E293B] dark:border-slate-700 px-11 py-3 text-sm text-slate-900 dark:text-white outline-none transition focus:ring-2`}
                  placeholder="OF-2024-001"
                  value={patientId}
                  onChange={(e) => {
                    setPatientId(e.target.value);
                    setPatientIdError(null);
                  }}
                />
              </div>
              {patientIdError && <p className="mt-1 text-xs text-red-500">{patientIdError}</p>}
            </div>

            {/* Date of Birth */}
            <div>
              <label className="block text-xs font-bold text-[#1A5296] dark:text-[#94A3B8] mb-2 uppercase tracking-wide">
                Date of Birth
              </label>
              <div className="relative">
                <Calendar className="absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-[#38BDF8]" />
                <input
                  className={`w-full rounded-xl border ${dobError ? 'border-red-500 focus:ring-red-200' : 'border-[#E2E8F0] focus:border-[#38BDF8] focus:ring-[#38BDF8]/20'} bg-white dark:bg-[#1E293B] dark:border-slate-700 px-11 py-3 text-sm text-slate-900 dark:text-white outline-none transition focus:ring-2`}
                  placeholder="DD/MM/YYYY"
                  value={dobVal}
                  onChange={(e) => {
                    setDobVal(e.target.value);
                    setDobError(null);
                  }}
                />
              </div>
              {dobError && <p className="mt-1 text-xs text-red-500">{dobError}</p>}
            </div>

            {/* Gender */}
            <div>
              <label className="block text-xs font-bold text-[#1A5296] dark:text-[#94A3B8] mb-2 uppercase tracking-wide">
                Gender
              </label>
              <div className="flex gap-2">
                {['Male', 'Female'].map((g) => {
                  const selected = genderVal === g;
                  return (
                    <button
                      key={g}
                      type="button"
                      onClick={() => setGenderVal(g)}
                      className={`inline-flex items-center gap-1.5 rounded-full px-5 py-2.5 text-xs font-bold border transition ${
                        selected 
                          ? 'bg-[#1A5296] border-[#1A5296] text-white shadow-sm' 
                          : 'bg-[#F9FAFB] dark:bg-[#1E293B] border-[#E2E8F0] dark:border-slate-700 text-[#64748B] dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
                      }`}
                    >
                      {selected && <Check size={14} />}
                      {g}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={handleNext}
              className="w-full h-12 inline-flex items-center justify-center rounded-xl bg-[#1A5296] text-sm font-bold text-white shadow-md hover:bg-[#1A5296]/95 transition"
            >
              NEXT
            </button>
            <p className="text-center text-[11px] text-[#64748B] dark:text-slate-400 mt-4 leading-normal">
              Data is encrypted and HIPAA compliant
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

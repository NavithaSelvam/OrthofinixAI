import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User, CheckCircle2 } from 'lucide-react';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordVisible] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  
  const [loading, setLoading] = useState(false);
  
  // Validation errors
  const [nameError, setNameError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [termsError, setTermsError] = useState<string | null>(null);

  const { register } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    let isValid = true;

    if (!fullName.trim()) {
      setNameError('Full name is required');
      isValid = false;
    } else {
      setNameError(null);
    }

    const emailRegex = /^[A-Za-z](.*)([@]{1})(.{1,})(\.)(.{1,})/;
    if (!email.trim() || !emailRegex.test(email)) {
      setEmailError('Valid email is required');
      isValid = false;
    } else {
      setEmailError(null);
    }

    if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    } else {
      setPasswordError(null);
    }

    if (password !== confirmPassword) {
      setConfirmError('Passwords do not match');
      isValid = false;
    } else {
      setConfirmError(null);
    }

    if (!termsAccepted) {
      setTermsError('You must accept the terms & clinical privacy policy');
      isValid = false;
    } else {
      setTermsError(null);
    }

    return isValid;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await register(email, password, fullName || 'Doctor');
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (err: any) {
      toast.error(err.message || 'Registration failed. Email may already exist.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 min-h-0 sm:min-h-[640px] w-full">
      
      {/* Left Brand Showcase (Desktop only - 5 cols) */}
      <div className="hidden lg:flex lg:col-span-5 bg-gradient-to-br from-slate-900 via-sky-950 to-slate-900 p-8 lg:p-10 text-white flex-col justify-between relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="space-y-6 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-white font-black text-xl shadow-md">
              O
            </div>
            <div>
              <h2 className="text-xl font-extrabold tracking-tight">Orthofinix<span className="text-sky-400">AI</span></h2>
              <p className="text-[11px] text-slate-400 font-medium">Orthodontic Finishing System</p>
            </div>
          </div>

          <div className="space-y-3 pt-4">
            <h3 className="text-2xl font-black leading-tight text-white">
              Start Using AI-Powered Orthodontic Analysis
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Create your clinic profile to begin uploading and analyzing panoramic OPGs, frontal smile photos, and lateral cephalometrics.
            </p>
          </div>

          <div className="space-y-2.5 pt-2">
            {[
              'Automated ABO Objective Grading System',
              'Lawrence Andrews 6 Keys Compliance',
              'Secure Cloud & Offline Sync',
              'Exportable Board-Certified PDF Reports'
            ].map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2.5 text-xs text-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-8 text-[11px] text-slate-400 relative z-10 border-t border-slate-800">
          HIPAA & Clinical Compliance Guaranteed
        </div>
      </div>

      {/* Right Registration Form (7 cols on desktop, full-width on mobile) */}
      <div className="col-span-1 lg:col-span-7 p-6 sm:p-8 lg:p-12 flex flex-col justify-center bg-white dark:bg-slate-900">
        <div className="max-w-md mx-auto w-full space-y-6">
          
          {/* Mobile Branded Header */}
          <div className="flex lg:hidden items-center gap-3 pb-1">
            <img src="./logo.png" className="w-10 h-10 rounded-xl shadow-xs" alt="OrthofinixAI" />
            <div>
              <h1 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">
                Orthofinix<span className="text-sky-500">AI</span>
              </h1>
              <p className="text-[11px] text-slate-400 font-semibold">Doctor Registration</p>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              Create Doctor Account
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Join the OrthofinixAI orthodontic community.
            </p>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            
            {/* Full Name */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Full Doctor Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Dr. Alexander Wright, DDS"
                  className="w-full pl-10 pr-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                />
              </div>
              {nameError && <p className="text-[11px] text-red-500 mt-1">{nameError}</p>}
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="doctor@orthoclinic.com"
                  className="w-full pl-10 pr-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                />
              </div>
              {emailError && <p className="text-[11px] text-red-500 mt-1">{emailError}</p>}
            </div>

            {/* Password */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type={passwordVisible ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                  />
                </div>
                {passwordError && <p className="text-[11px] text-red-500 mt-1">{passwordError}</p>}
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type={passwordVisible ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
                  />
                </div>
                {confirmError && <p className="text-[11px] text-red-500 mt-1">{confirmError}</p>}
              </div>
            </div>

            {/* Terms Checkbox */}
            <div className="pt-1">
              <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={termsAccepted}
                  onChange={(e) => setTermsAccepted(e.target.checked)}
                  className="rounded-md border-slate-300 text-sky-600 focus:ring-sky-500 w-4 h-4"
                />
                <span>I agree to the Terms of Service and Clinical Privacy Policy</span>
              </label>
              {termsError && <p className="text-[11px] text-red-500 mt-1">{termsError}</p>}
            </div>

            {/* Submit CTA */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white font-extrabold text-xs shadow-md shadow-sky-500/20 transition flex items-center justify-center gap-2"
              >
                {loading ? 'Creating Clinic Account...' : 'Complete Registration'}
              </button>
            </div>
          </form>

          <div className="text-center text-xs text-slate-500">
            Already have a clinic account?{' '}
            <Link to="/login" className="font-bold text-sky-600 dark:text-sky-400 hover:underline">
              Sign In
            </Link>
          </div>

        </div>
      </div>

    </div>
  );
}

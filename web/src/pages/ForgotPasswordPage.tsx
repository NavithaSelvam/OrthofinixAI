import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const { resetPassword } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailError('Please enter a valid email address');
      return false;
    }
    setEmailError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setIsLoading(true);
    try {
      await resetPassword(email);
      setIsSubmitted(true);
      toast.success('Password reset email sent.');
    } catch (err: any) {
      setEmailError(err.message || 'Could not send reset link');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] font-sans flex flex-col">
      {/* Top Header Bar */}
      <header className="bg-[#1A5296] text-white h-14 flex items-center px-4 shadow-md shrink-0">
        <button 
          onClick={() => navigate('/login')}
          className="p-1 hover:bg-white/10 rounded-full transition mr-3 text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-white leading-none">Forgot Password</h1>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-start p-6">
        <div className="w-full max-w-md">
          {!isSubmitted ? (
            <form onSubmit={handleSubmit} className="space-y-6 pt-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-[#1A5296] dark:text-white">Reset Password</h2>
                <p className="mt-2 text-sm text-[#64748B] dark:text-slate-400 max-w-xs mx-auto leading-relaxed">
                  Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>

              <div className="pt-4">
                <label className="block text-xs font-bold text-[#1A5296] dark:text-[#94A3B8] uppercase tracking-wider mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-[#38BDF8]" />
                  <input
                    className={`w-full rounded-xl border ${emailError ? 'border-red-500 focus:ring-red-200' : 'border-[#E2E8F0] focus:border-[#38BDF8] focus:ring-[#38BDF8]/20'} bg-white dark:bg-[#1E293B] dark:border-slate-700 px-11 py-3.5 text-sm text-slate-900 dark:text-white outline-none transition focus:ring-2`}
                    type="email"
                    placeholder="dr.smith@orthofinix.ai"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setEmailError(null);
                    }}
                  />
                </div>
                {emailError && (
                  <p className="mt-1.5 text-xs text-red-500">
                    {emailError}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 inline-flex items-center justify-center gap-2 rounded-xl bg-[#1A5296] text-sm font-bold text-white shadow-md hover:bg-[#1A5296]/95 transition disabled:opacity-50"
              >
                {isLoading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          ) : (
            <div className="text-center space-y-6 pt-10">
              <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-[#38BDF8]/10 text-[#38BDF8]">
                <Mail size={44} />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-[#1A5296] dark:text-white">Check Your Email</h2>
                <p className="mt-2 text-sm text-[#64748B] dark:text-slate-400 leading-relaxed px-4">
                  We've sent a password reset link to <strong className="text-[#1A5296] dark:text-blue-400">{email}</strong>
                </p>
              </div>

              <button
                onClick={() => navigate('/login')}
                className="w-full h-12 inline-flex items-center justify-center gap-2 rounded-xl bg-[#1A5296] text-sm font-bold text-white shadow-md hover:bg-[#1A5296]/95 transition"
              >
                Back to Sign In
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

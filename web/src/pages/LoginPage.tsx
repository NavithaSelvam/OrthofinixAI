import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, AlertCircle, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);

  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    let isValid = true;
    if (!email.trim()) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailError('Please enter a valid email address');
      isValid = false;
    } else {
      setEmailError(null);
    }

    if (!password) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    } else if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      isValid = false;
    } else {
      setPasswordError(null);
    }

    return isValid;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    if (!validate()) return;
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err: any) {
      const errMsg = err.message || 'Login failed. Check credentials.';
      setAuthError(errMsg);
      toast.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setAuthError(null);
    setGoogleLoading(true);
    try {
      if (loginWithGoogle) {
        await loginWithGoogle();
        toast.success('Signed in with Google!');
        navigate('/dashboard');
      } else {
        toast.error('Google Sign-In is not configured for this domain.');
      }
    } catch (err: any) {
      const errMsg = err.message || 'Google sign in failed.';
      setAuthError(errMsg);
      toast.error(errMsg);
    } finally {
      setGoogleLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col items-center justify-center p-4 sm:p-6 font-sans">
      <div className="w-full max-w-md flex flex-col items-center space-y-6">
        
        {/* Android matching Logo & Title */}
        <div className="flex flex-col items-center text-center space-y-1.5 pt-4 sm:pt-0">
          <div className="flex items-center justify-center">
            <img 
              src="./logo.png" 
              className="h-16 w-auto object-contain drop-shadow-sm" 
              alt="Orthofinix Logo" 
            />
          </div>
          
          <h1 className="text-2xl font-black tracking-widest text-[#0A192F] dark:text-white uppercase mt-2">
            ORTHOFINIX.AI
          </h1>
          <p className="text-xs font-semibold text-[#64748B] dark:text-slate-400">
            Clinical-Grade Orthodontic Intelligence
          </p>
        </div>

        {/* Android matching Clinical Card (SurfaceClinical) */}
        <div className="w-full rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 shadow-md p-6 sm:p-8 space-y-5">
          
          <div>
            <h2 className="text-xl font-bold text-[#0A192F] dark:text-white">
              Welcome Back
            </h2>
          </div>

          {authError && (
            <div className="p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 flex items-center gap-2.5 text-xs text-red-600 dark:text-red-300">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{authError}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email Address */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#0A192F] dark:text-slate-200">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#0284C7] dark:text-[#38BDF8]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setEmailError(null); }}
                  placeholder="dr.smith@orthofinix.ai"
                  className="w-full pl-10 pr-4 py-3 text-xs font-medium rounded-xl bg-white dark:bg-[#0F172A] border border-[#E2E8F0] dark:border-slate-700 text-[#0A192F] dark:text-white placeholder:text-[#64748B]/50 focus:border-[#0284C7] focus:ring-1 focus:ring-[#0284C7] outline-none transition"
                />
              </div>
              {emailError && <p className="text-[11px] text-red-500">{emailError}</p>}
            </div>

            {/* Remember Me & Forgot Password Row */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded text-[#0284C7] border-slate-300 focus:ring-[#0284C7]"
                />
                <span className="text-xs text-[#64748B] dark:text-slate-400 font-medium">Remember Me</span>
              </label>
              
              <Link 
                to="/forgot-password" 
                className="text-xs font-bold text-[#0284C7] dark:text-[#38BDF8] hover:underline"
              >
                Forgot Password?
              </Link>
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-[#0A192F] dark:text-slate-200">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#0284C7] dark:text-[#38BDF8]" />
                <input
                  type={passwordVisible ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setPasswordError(null); }}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-3 text-xs font-medium rounded-xl bg-white dark:bg-[#0F172A] border border-[#E2E8F0] dark:border-slate-700 text-[#0A192F] dark:text-white placeholder:text-[#64748B]/50 focus:border-[#0284C7] focus:ring-1 focus:ring-[#0284C7] outline-none transition"
                />
                <button
                  type="button"
                  onClick={() => setPasswordVisible(!passwordVisible)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-slate-900 dark:hover:text-white"
                >
                  {passwordVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {passwordError && <p className="text-[11px] text-red-500">{passwordError}</p>}
            </div>

            {/* Sign In CTA Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#1A5296] to-[#0284C7] hover:from-[#154279] hover:to-[#0274ae] text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2 active:scale-[0.99]"
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </button>
            </div>

            {/* Google Sign In Button */}
            <div>
              <button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={googleLoading}
                className="w-full py-3 rounded-xl border border-[#E2E8F0] dark:border-slate-700 bg-white dark:bg-[#0F172A] hover:bg-slate-50 dark:hover:bg-slate-800 text-[#0A192F] dark:text-white font-bold text-xs shadow-2xs transition flex items-center justify-center gap-3"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
                <span>{googleLoading ? 'Connecting Google...' : 'Sign In with Google'}</span>
              </button>
            </div>
          </form>

          {/* Footer Navigation */}
          <div className="text-center pt-2 text-xs text-[#64748B] dark:text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-[#0284C7] dark:text-[#38BDF8] hover:underline">
              Sign Up
            </Link>
          </div>

        </div>

      </div>
    </div>
  );
}

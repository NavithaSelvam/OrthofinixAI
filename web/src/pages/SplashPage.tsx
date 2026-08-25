import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles } from 'lucide-react';

export default function SplashPage() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 5;
      });
    }, 60);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (progress === 100 && !loading) {
      const timeout = setTimeout(() => {
        if (user) {
          navigate('/dashboard', { replace: true });
        } else {
          navigate('/login', { replace: true });
        }
      }, 300);
      return () => clearTimeout(timeout);
    }
  }, [progress, loading, user, navigate]);

  const getStatusText = () => {
    if (progress < 30) return 'Initializing clinical AI engine...';
    if (progress < 60) return 'Loading orthodontic finishing models...';
    if (progress < 90) return 'Preparing analysis pipeline & Firestore...';
    return 'Ready';
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-white via-[#F0F7FF] to-[#E8F5E9] dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex flex-col items-center justify-center p-6 select-none">
      <div className="w-full max-w-sm flex flex-col items-center text-center space-y-6">
        {/* Animated Brand Logo Icon */}
        <div className="relative">
          <div className="w-24 h-24 rounded-3xl bg-gradient-to-tr from-sky-600 via-teal-500 to-emerald-400 p-0.5 shadow-xl animate-pulse">
            <div className="w-full h-full bg-white dark:bg-slate-900 rounded-[22px] flex items-center justify-center">
              <span className="text-4xl font-black bg-gradient-to-tr from-sky-600 to-emerald-500 bg-clip-text text-transparent">
                O
              </span>
            </div>
          </div>
          <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-xs">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Title and Tagline */}
        <div className="space-y-1.5">
          <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
            Orthofinix<span className="text-sky-600 dark:text-sky-400">AI</span>
          </h1>
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 tracking-wide uppercase">
            AI-Powered Orthodontic Assessment
          </p>
        </div>

        {/* Progress Bar */}
        <div className="w-full max-w-[220px] space-y-2 pt-6">
          <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-sky-500 to-emerald-500 rounded-full transition-all duration-100 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
            {getStatusText()}
          </p>
        </div>
      </div>

      {/* Footer Version Info */}
      <div className="absolute bottom-6 text-center text-[10px] text-slate-400 font-medium">
        Version 2.4.0 • Clinical CE & ABO Framework
      </div>
    </div>
  );
}

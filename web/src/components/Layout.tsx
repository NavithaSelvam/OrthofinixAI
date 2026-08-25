import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MainBottomBar from './MainBottomBar';
import InstallPWAButton from './InstallPWAButton';

export function AppLayout() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="h-full w-full bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col items-center justify-center font-sans">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#1A5296] dark:border-[#38BDF8] border-t-transparent shadow-md" />
        <p className="mt-4 text-xs font-bold text-[#1A5296] dark:text-[#38BDF8] tracking-wider uppercase">
          Initializing OrthofinixAI Platform...
        </p>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div 
      className="w-full h-full bg-[#F8FAFC] dark:bg-[#0F172A] flex flex-col font-sans antialiased relative overflow-hidden pt-8"
      style={{ paddingTop: '36px' }}
    >
      {/* 1-Tap App Install Prompt Banner for Phones */}
      <InstallPWAButton />

      {/* Main Content Area taking remaining height and scrolling independently */}
      <main className="flex-1 overflow-y-auto w-full flex flex-col overscroll-contain">
        <Outlet />
      </main>
      
      {/* Navigation Bottom Bar docked cleanly at bottom */}
      <MainBottomBar />
    </div>
  );
}

export function PublicLayout() {
  return (
    <div className="min-h-full w-full bg-white dark:bg-[#0F172A] sm:bg-gradient-to-br sm:from-slate-900 sm:via-sky-950 sm:to-slate-900 flex flex-col font-sans relative overflow-x-hidden">
      <InstallPWAButton />
      <div className="flex-1 flex items-center justify-center p-0 sm:p-6 lg:p-10 w-full h-full">
        <div className="w-full h-full sm:h-auto max-w-5xl bg-white dark:bg-[#1E293B] sm:rounded-3xl shadow-none sm:shadow-2xl sm:border border-slate-700/40 overflow-hidden flex flex-col justify-center">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

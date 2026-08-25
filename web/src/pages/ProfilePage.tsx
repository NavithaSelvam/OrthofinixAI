import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import {
  Badge,
  CheckCircle,
  CreditCard,
  HelpCircle,
  Info,
  LogOut,
  ChevronRight
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const userName = user?.display_name || 'Doctor';
  const userEmail = user?.email || 'dr.smith@orthofinix.ai';

  const handleCredentialsClick = () => {
    toast.success('Credentials Verified: Certified Orthodontic AI Clinician.');
  };

  const handleSignOut = async () => {
    await logout();
    toast.success('Signed out successfully.');
    navigate('/login');
  };

  const initialLetter = userName.charAt(0).toUpperCase();

  return (
    <div className="flex-1 flex flex-col bg-[#F8FAFC] dark:bg-[#0F172A] pb-24 font-sans">
      
      {/* TopAppBar matching Android ClinicalDeepNavy */}
      <header className="bg-[#1A5296] text-white h-14 flex items-center px-4 shadow-md shrink-0 sticky top-0 z-30">
        <h1 className="text-lg font-bold text-white leading-none">Profile</h1>
      </header>

      {/* Main Column matching Android ProfileScreen */}
      <div className="p-6 space-y-6 flex flex-col items-center">
        
        {/* Profile Avatar & Header */}
        <div className="flex flex-col items-center text-center">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-[#38BDF8]/10 border-2 border-[#38BDF8] text-4xl font-black text-[#38BDF8] shadow-xs">
            {initialLetter}
          </div>
          <h2 className="mt-4 text-xl font-bold text-[#1A5296] dark:text-white">
            Dr. {userName}
          </h2>
          <p className="text-xs text-[#64748B] dark:text-slate-400 mt-0.5">
            {userEmail}
          </p>
          <p className="text-[11px] text-[#64748B]/80 dark:text-slate-500 mt-0.5">
            Orthodontist • Clinic Associate
          </p>
        </div>

        {/* Menu Cards List matching Android */}
        <div className="w-full space-y-3">
          
          {/* Personal Info */}
          <div
            onClick={() => navigate('/settings')}
            className="cursor-pointer flex items-center justify-between rounded-xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-4 shadow-2xs hover:shadow-xs transition"
          >
            <div className="flex items-center gap-3.5">
              <Badge className="text-[#38BDF8] h-5 w-5" />
              <span className="text-xs font-semibold text-[#1A5296] dark:text-blue-300">
                Personal Information
              </span>
            </div>
            <ChevronRight className="text-[#64748B] h-4 w-4" />
          </div>

          {/* Clinical Credentials */}
          <div
            onClick={handleCredentialsClick}
            className="cursor-pointer flex items-center justify-between rounded-xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-4 shadow-2xs hover:shadow-xs transition"
          >
            <div className="flex items-center gap-3.5">
              <CheckCircle className="text-[#38BDF8] h-5 w-5" />
              <span className="text-xs font-semibold text-[#1A5296] dark:text-blue-300">
                Clinical Credentials
              </span>
            </div>
            <ChevronRight className="text-[#64748B] h-4 w-4" />
          </div>

          {/* Subscription Plan */}
          <div
            onClick={() => navigate('/subscription')}
            className="cursor-pointer flex items-center justify-between rounded-xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-4 shadow-2xs hover:shadow-xs transition"
          >
            <div className="flex items-center gap-3.5">
              <CreditCard className="text-[#38BDF8] h-5 w-5" />
              <span className="text-xs font-semibold text-[#1A5296] dark:text-blue-300">
                Subscription Plan
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-[#2BB673]">Pro Access</span>
              <ChevronRight className="text-[#64748B] h-4 w-4" />
            </div>
          </div>

          {/* Help & Support */}
          <div
            onClick={() => navigate('/help')}
            className="cursor-pointer flex items-center justify-between rounded-xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-4 shadow-2xs hover:shadow-xs transition"
          >
            <div className="flex items-center gap-3.5">
              <HelpCircle className="text-[#38BDF8] h-5 w-5" />
              <span className="text-xs font-semibold text-[#1A5296] dark:text-blue-300">
                Help & Support
              </span>
            </div>
            <ChevronRight className="text-[#64748B] h-4 w-4" />
          </div>

          {/* About */}
          <div
            onClick={() => navigate('/about')}
            className="cursor-pointer flex items-center justify-between rounded-xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-4 shadow-2xs hover:shadow-xs transition"
          >
            <div className="flex items-center gap-3.5">
              <Info className="text-[#38BDF8] h-5 w-5" />
              <span className="text-xs font-semibold text-[#1A5296] dark:text-blue-300">
                About OrthofinixAI
              </span>
            </div>
            <ChevronRight className="text-[#64748B] h-4 w-4" />
          </div>

          {/* Sign Out */}
          <div
            onClick={handleSignOut}
            className="cursor-pointer flex items-center justify-between rounded-xl border border-red-100 dark:border-red-950/50 bg-white dark:bg-[#1E293B] p-4 shadow-2xs hover:bg-red-50/30 transition mt-6"
          >
            <div className="flex items-center gap-3.5">
              <LogOut className="text-red-500 h-5 w-5" />
              <span className="text-xs font-bold text-red-500">
                Sign Out
              </span>
            </div>
            <ChevronRight className="text-red-400 h-4 w-4" />
          </div>

        </div>

      </div>

    </div>
  );
}

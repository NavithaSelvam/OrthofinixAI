import { useState } from 'react';
import { Info, Cpu } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { dark, toggle } = useTheme();
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const handleNotificationsToggle = () => {
    setNotificationsEnabled(!notificationsEnabled);
    toast.success(`Push notifications ${!notificationsEnabled ? 'enabled' : 'disabled'}`);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#F8FAFC] dark:bg-[#0F172A] pb-24 font-sans">
      
      {/* TopAppBar matching Android BrandedTopBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 sticky top-0 z-30 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#1A5296] text-white font-black text-sm">
            O
          </div>
          <span className="text-base font-bold text-slate-900 dark:text-white">
            Settings
          </span>
        </div>
      </header>

      {/* Main Column matching Android SettingsScreen */}
      <div className="p-5 space-y-6">
        
        {/* General Section */}
        <div>
          <h3 className="text-sm font-bold text-[#76B82A] tracking-wide uppercase mb-3">
            General
          </h3>
          <div className="space-y-2 divide-y divide-slate-100 dark:divide-slate-800">
            <div className="flex items-center justify-between py-3">
              <span className="text-slate-800 dark:text-slate-200 text-sm font-medium">
                Push Notifications
              </span>
              <button
                onClick={handleNotificationsToggle}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notificationsEnabled ? 'bg-[#76B82A]' : 'bg-slate-300 dark:bg-slate-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notificationsEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between py-3">
              <span className="text-slate-800 dark:text-slate-200 text-sm font-medium">
                Dark Mode
              </span>
              <button
                onClick={toggle}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  dark ? 'bg-[#76B82A]' : 'bg-slate-300 dark:bg-slate-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    dark ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* About Section */}
        <div>
          <h3 className="text-sm font-bold text-[#76B82A] tracking-wide uppercase mb-3">
            About
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-4 py-2 text-slate-700 dark:text-slate-300">
              <Info size={20} className="text-[#64748B] shrink-0" />
              <span className="text-sm font-medium">OrthofinixAI v2.4.0 • Clinical Edition</span>
            </div>

            <div className="flex items-center gap-4 py-2 text-slate-700 dark:text-slate-300">
              <Cpu size={20} className="text-[#64748B] shrink-0" />
              <span className="text-sm font-medium">ABO Objective Grading System & Andrews' Six Keys</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}

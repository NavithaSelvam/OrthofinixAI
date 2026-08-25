import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface BrandedHeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightElement?: React.ReactNode;
}

export default function BrandedHeader({
  title,
  subtitle = 'OrthofinixAI',
  showBack = false,
  onBack,
  rightElement,
}: BrandedHeaderProps) {
  const navigate = useNavigate();
  const { dark, toggle } = useTheme();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(-1);
    }
  };

  return (
    <header className="sticky top-0 left-0 right-0 w-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3 z-30 flex items-center justify-between shadow-xs">
      <div className="flex items-center gap-3">
        {showBack && (
          <button
            onClick={handleBack}
            className="p-2 -ml-1 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Back"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
        )}

        <div className="flex items-center gap-2.5">
          <img src="./logo.png" className="w-8 h-8 rounded-xl shadow-xs" alt="OrthofinixAI" />
          <div>
            <h1 className="text-base font-bold text-slate-900 dark:text-white leading-tight">
              {title}
            </h1>
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              {subtitle}
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        {rightElement}
        <button
          onClick={toggle}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Toggle Theme"
        >
          {dark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>
        <button
          onClick={() => navigate('/notifications')}
          className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </button>
      </div>
    </header>
  );
}

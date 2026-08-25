import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Search,
  Bell,
  Sun,
  Moon,
  Plus,
  ChevronRight
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function DesktopHeader() {
  const navigate = useNavigate();
  const location = useLocation();
  const { dark, toggle } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard' || path === '/') return 'Clinical Dashboard';
    if (path === '/upload' || path.startsWith('/upload')) return 'New AI Scan Analysis';
    if (path === '/history' || path === '/cases') return 'Clinical Cases Registry';
    if (path === '/patients') return 'Patients Directory';
    if (path.startsWith('/results/')) return 'Case Assessment & Finishing Score';
    if (path.startsWith('/guidelines')) return 'Orthodontic Protocols & Guidelines';
    if (path === '/settings') return 'Settings & Clinic Configuration';
    if (path === '/profile') return 'Doctor Profile';
    if (path === '/about') return 'STAR Orthodontic System';
    if (path === '/help') return 'Clinical Support & Documentation';
    if (path.startsWith('/export/')) return 'Export Clinical PDF Report';
    return 'OrthofinixAI Platform';
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/history?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="h-18 px-6 lg:px-8 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between z-20 shrink-0 select-none">
      
      {/* Page Title & Breadcrumbs */}
      <div className="flex flex-col">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 dark:text-slate-500">
          <span>OrthofinixAI</span>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-sky-600 dark:text-sky-400 font-bold">{getPageTitle()}</span>
        </div>
        <h1 className="text-lg lg:text-xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          {getPageTitle()}
        </h1>
      </div>

      {/* Center Search Bar */}
      <form onSubmit={handleSearchSubmit} className="hidden md:flex items-center flex-1 max-w-md mx-8">
        <div className="relative w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search cases by patient name, ID, or view type..."
            className="w-full pl-10 pr-4 py-2 text-xs font-medium rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-transparent focus:border-sky-500 dark:focus:border-sky-400 focus:bg-white dark:focus:bg-slate-900 outline-none transition text-slate-900 dark:text-white placeholder-slate-400"
          />
        </div>
      </form>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        
        {/* System Status Pill */}
        <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-[11px] font-semibold text-emerald-700 dark:text-emerald-300">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>AI Engine Connected</span>
        </div>

        {/* Action Button: New Case */}
        <button
          onClick={() => navigate('/upload')}
          className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white text-xs font-bold shadow-md shadow-sky-500/20 hover:shadow-lg transition active:scale-98"
        >
          <Plus className="w-4 h-4" />
          <span>New Analysis</span>
        </button>

        {/* Theme Toggle Button */}
        <button
          onClick={toggle}
          title={dark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
          {dark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* Notifications */}
        <button
          onClick={() => navigate('/notifications')}
          title="Clinical Notifications"
          className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition relative"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
        </button>

      </div>
    </header>
  );
}

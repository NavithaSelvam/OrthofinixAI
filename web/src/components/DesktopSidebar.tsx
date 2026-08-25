import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  FolderOpen,
  Users,
  BookOpen,
  Settings,
  User,
  HelpCircle,
  Info,
  LogOut,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function DesktopSidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navGroups = [
    {
      group: 'Workspace',
      items: [
        { route: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { route: '/upload', label: 'New Analysis', icon: PlusCircle, badge: 'AI' },
        { route: '/history', label: 'Clinical Cases', icon: FolderOpen },
        { route: '/patients', label: 'Patients Directory', icon: Users },
      ],
    },
    {
      group: 'Clinical Intelligence',
      items: [
        { route: '/guidelines', label: 'Guidelines & Protocols', icon: BookOpen },
        { route: '/about', label: 'About STAR System', icon: Info },
      ],
    },
    {
      group: 'Preferences',
      items: [
        { route: '/settings', label: 'Clinic Settings', icon: Settings },
        { route: '/profile', label: 'Doctor Profile', icon: User },
        { route: '/help', label: 'Help & Support', icon: HelpCircle },
      ],
    },
  ];

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch {
      navigate('/login');
    }
  };

  const initialLetter = user?.display_name ? user.display_name.charAt(0).toUpperCase() : 'D';

  return (
    <aside className="w-64 xl:w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0 select-none transition-all duration-200 z-30">
      
      {/* Brand Header */}
      <div className="h-18 px-6 flex items-center gap-3 border-b border-slate-100 dark:border-slate-800/80">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-emerald-400 flex items-center justify-center text-white font-black text-lg shadow-md shadow-sky-500/20">
          O
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">
              Orthofinix<span className="text-sky-600 dark:text-sky-400">AI</span>
            </span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              PRO
            </span>
          </div>
          <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500">
            Orthodontic Finishing
          </span>
        </div>
      </div>

      {/* Navigation Groups */}
      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6">
        {navGroups.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {group.group}
            </p>
            <div className="space-y-0.5 pt-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive =
                  location.pathname === item.route ||
                  (item.route === '/dashboard' && location.pathname === '/') ||
                  (item.route === '/history' && location.pathname.startsWith('/results/')) ||
                  (item.route === '/guidelines' && location.pathname.startsWith('/guidelines')) ||
                  (item.route === '/upload' && location.pathname.startsWith('/upload'));

                return (
                  <button
                    key={item.route}
                    onClick={() => navigate(item.route)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150 group ${
                      isActive
                        ? 'bg-sky-50 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300 shadow-xs'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`w-4 h-4 transition-colors ${
                          isActive
                            ? 'text-sky-600 dark:text-sky-400'
                            : 'text-slate-400 dark:text-slate-500 group-hover:text-slate-700 dark:group-hover:text-slate-300'
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>

                    {item.badge && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gradient-to-r from-sky-500 to-emerald-400 text-white shadow-xs">
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        {/* Quick CTA Card */}
        <div className="rounded-2xl p-4 bg-gradient-to-br from-slate-900 to-sky-950 text-white shadow-md border border-slate-800/80 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-sky-500/10 rounded-full blur-xl pointer-events-none" />
          <div className="flex items-center gap-2 text-sky-400 mb-1.5">
            <Sparkles className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-wider">AI Engine</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Ready to analyze lateral, frontal, or OPG orthodontic finishing views.
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="mt-3 w-full py-2 px-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-1.5"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Upload Scan</span>
          </button>
        </div>
      </div>

      {/* User Profile Footer */}
      <div className="p-4 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="flex items-center justify-between">
          <div 
            onClick={() => navigate('/profile')}
            className="flex items-center gap-3 cursor-pointer group flex-1 min-w-0 pr-2"
          >
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-sky-500 to-sky-700 flex items-center justify-center text-white font-bold text-sm shadow-xs shrink-0 group-hover:ring-2 ring-sky-400/50 transition">
              {initialLetter}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-slate-900 dark:text-white truncate group-hover:text-sky-600 transition">
                {user?.display_name || 'Dr. Orthodontist'}
              </p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 truncate">
                {user?.email || 'doctor@orthofinix.ai'}
              </p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-2 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

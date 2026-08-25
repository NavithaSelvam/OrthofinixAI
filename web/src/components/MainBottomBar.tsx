import { useLocation, useNavigate } from 'react-router-dom';
import { Home, FolderOpen, BookOpen, Settings, User } from 'lucide-react';

interface NavItem {
  route: string;
  label: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { route: '/dashboard', label: 'Home', icon: Home },
  { route: '/history', label: 'Cases', icon: FolderOpen },
  { route: '/guidelines', label: 'Guidelines', icon: BookOpen },
  { route: '/settings', label: 'Settings', icon: Settings },
  { route: '/profile', label: 'Profile', icon: User },
];

export default function MainBottomBar() {
  const location = useLocation();
  const navigate = useNavigate();

  // Do not display bottom bar on analysis processing or full screen report export
  if (
    location.pathname.includes('/upload/processing') ||
    location.pathname.includes('/export/')
  ) {
    return null;
  }

  return (
    <nav className="shrink-0 w-full bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 pt-1.5 px-3 z-50 flex items-center justify-around pb-[max(8px,env(safe-area-inset-bottom))] shadow-lg">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive =
          location.pathname === item.route ||
          (item.route === '/dashboard' && location.pathname === '/') ||
          (item.route === '/history' && location.pathname.startsWith('/results/')) ||
          (item.route === '/guidelines' && location.pathname.startsWith('/guidelines'));

        return (
          <button
            key={item.route}
            onClick={() => navigate(item.route)}
            className={`flex flex-col items-center justify-center flex-1 py-1 transition-all duration-200 relative ${
              isActive
                ? 'text-[#0284C7] dark:text-[#38BDF8] font-semibold scale-105'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            <div
              className={`p-1 rounded-xl transition-colors ${
                isActive ? 'bg-sky-50 dark:bg-sky-950/50' : 'bg-transparent'
              }`}
            >
              <Icon className="w-5 h-5" />
            </div>
            <span className="text-[11px] mt-0.5 tracking-tight">{item.label}</span>
            {isActive && (
              <span className="absolute -bottom-1 w-1.5 h-1.5 rounded-full bg-[#0284C7] dark:bg-[#38BDF8]" />
            )}
          </button>
        );
      })}
    </nav>
  );
}

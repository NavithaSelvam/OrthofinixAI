import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCircle2, Sparkles, FileText, Trash2, Clock } from 'lucide-react';
import BrandedHeader from '../components/BrandedHeader';
import toast from 'react-hot-toast';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: 'analysis' | 'system' | 'report';
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

const initialNotifications: NotificationItem[] = [
  {
    id: 'notif-1',
    title: 'AI Analysis Pipeline Connected',
    message: 'OrthofinixAI cloud assessment models & Firebase Firestore persistence are fully active.',
    type: 'system',
    timestamp: 'Just now',
    read: false,
  },
  {
    id: 'notif-2',
    title: 'ABO OGS Scoring Engine Updated',
    message: 'New deduction thresholds for marginal ridge alignment and root parallelism have been enabled.',
    type: 'analysis',
    timestamp: '1 hour ago',
    read: false,
    actionUrl: '/guidelines/abo-ogs',
  },
  {
    id: 'notif-3',
    title: 'Clinical PDF Export Available',
    message: 'You can now export and print board-certified orthodontic finishing reports directly from your dashboard.',
    type: 'report',
    timestamp: '2 hours ago',
    read: true,
    actionUrl: '/history',
  }
];

export default function NotificationsPage() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>(initialNotifications);

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    toast.success('All notifications marked as read');
  };

  const clearAll = () => {
    setNotifications([]);
    toast.success('Notifications cleared');
  };

  const getIcon = (type: NotificationItem['type']) => {
    switch (type) {
      case 'analysis':
        return <Sparkles className="w-4 h-4 text-sky-500" />;
      case 'report':
        return <FileText className="w-4 h-4 text-emerald-500" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-indigo-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col pb-20">
      <BrandedHeader
        title="Notifications"
        subtitle="Activity & Clinical Alerts"
        showBack={true}
        onBack={() => navigate(-1)}
        rightElement={
          notifications.length > 0 ? (
            <button
              onClick={clearAll}
              className="p-2 rounded-xl text-slate-500 hover:text-red-500 dark:hover:text-red-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Clear All"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          ) : undefined
        }
      />

      <main className="flex-1 p-4 space-y-4 max-w-lg mx-auto w-full">
        {notifications.length > 0 && (
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              {notifications.filter((n) => !n.read).length} Unread Updates
            </span>
            <button
              onClick={markAllAsRead}
              className="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:underline"
            >
              Mark all read
            </button>
          </div>
        )}

        {notifications.length === 0 ? (
          <div className="text-center py-16 space-y-3 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-8">
            <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
              <Bell className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-sm text-slate-800 dark:text-white">No notifications</h3>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              You are all caught up! New case reports and analysis completions will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {notifications.map((notif) => (
              <div
                key={notif.id}
                onClick={() => {
                  if (notif.actionUrl) navigate(notif.actionUrl);
                }}
                className={`p-4 rounded-2xl border transition-all ${
                  notif.read
                    ? 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 opacity-80'
                    : 'bg-white dark:bg-slate-900 border-sky-300 dark:border-sky-800 shadow-xs'
                } ${notif.actionUrl ? 'cursor-pointer hover:border-sky-500' : ''}`}
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/60 flex items-center justify-center shrink-0 mt-0.5">
                    {getIcon(notif.type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                        {notif.title}
                      </h4>
                      {!notif.read && (
                        <span className="w-2 h-2 rounded-full bg-sky-500 shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                      {notif.message}
                    </p>
                    <div className="flex items-center gap-1 text-[10px] text-slate-400 mt-2">
                      <Clock className="w-3 h-3" /> {notif.timestamp}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Check } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SubscriptionPage() {
  const navigate = useNavigate();

  const handleUpgradeClick = (planName: string) => {
    toast.success(`${planName} upgrade requested. Corporate billing registry setup required.`);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] font-sans flex flex-col pb-10">
      
      {/* TopAppBar */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 shrink-0">
        <button 
          onClick={() => navigate('/profile')}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition mr-3 text-slate-850 dark:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-bold text-slate-905 dark:text-white">Subscription Plans</h1>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="mx-auto max-w-md space-y-6">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white text-center leading-snug">
            Choose the right plan for your practice
          </h2>

          {/* Basic Plan Card */}
          <div className="rounded-2xl border-2 border-[#E5E7EB] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-6 shadow-sm flex flex-col space-y-4">
            <div>
              <h3 className="text-base font-bold text-slate-850 dark:text-white">Basic</h3>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-3xl font-extrabold text-slate-900 dark:text-white">$49</span>
                <span className="text-xs text-[#808080] dark:text-slate-400">/month</span>
              </div>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-850 dark:text-slate-200">
              {['5 AI Assessments', 'ABO OGS Scoring', 'PDF Export'].map((f, i) => (
                <li key={i} className="flex gap-3 items-center">
                  <Check className="text-[#76B82A] h-4 w-4 shrink-0" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleUpgradeClick('Basic')}
              className="w-full h-11 inline-flex items-center justify-center rounded-xl bg-gray-100 dark:bg-slate-800 text-sm font-bold text-slate-800 dark:text-slate-200 hover:bg-gray-200 transition"
            >
              Upgrade Now
            </button>
          </div>

          {/* Professional Plan Card (Selected / Best Value) */}
          <div className="rounded-2xl border-2 border-[#76B82A] bg-[#F0FDF4] dark:bg-emerald-950/20 p-6 shadow-md flex flex-col space-y-4 relative">
            <span className="absolute top-4 right-4 bg-[#76B82A] text-white text-[9px] font-black tracking-widest px-2.5 py-1 rounded-full uppercase">
              BEST VALUE
            </span>
            <div>
              <h3 className="text-base font-bold text-slate-855 dark:text-white">Professional</h3>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-3xl font-extrabold text-slate-900 dark:text-white">$129</span>
                <span className="text-xs text-[#808080] dark:text-slate-400">/month</span>
              </div>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-850 dark:text-slate-200">
              {['Unlimited Assessments', 'All Finishing Keys', 'Visual Overlays', 'Priority Support'].map((f, i) => (
                <li key={i} className="flex gap-3 items-center">
                  <Check className="text-[#76B82A] h-4 w-4 shrink-0" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <button
              disabled
              className="w-full h-11 inline-flex items-center justify-center rounded-xl bg-[#76B82A] text-sm font-bold text-white shadow transition cursor-default"
            >
              Current Plan
            </button>
          </div>

          {/* Institutional Plan Card */}
          <div className="rounded-2xl border-2 border-[#E5E7EB] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-6 shadow-sm flex flex-col space-y-4">
            <div>
              <h3 className="text-base font-bold text-slate-855 dark:text-white">Institutional</h3>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-3xl font-extrabold text-slate-900 dark:text-white">Custom</span>
              </div>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-850 dark:text-slate-200">
              {['Team Collaboration', 'API Access', 'SSO Integration', 'Dedicated Account Manager'].map((f, i) => (
                <li key={i} className="flex gap-3 items-center">
                  <Check className="text-[#76B82A] h-4 w-4 shrink-0" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleUpgradeClick('Institutional')}
              className="w-full h-11 inline-flex items-center justify-center rounded-xl bg-gray-100 dark:bg-slate-800 text-sm font-bold text-slate-800 dark:text-slate-200 hover:bg-gray-200 transition"
            >
              Upgrade Now
            </button>
          </div>

        </div>
      </main>
    </div>
  );
}

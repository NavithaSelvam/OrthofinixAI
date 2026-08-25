import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MessageSquare, Mail, HelpCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function HelpSupportPage() {
  const navigate = useNavigate();

  const handleChat = () => {
    toast.success('Opening real-time chat support console...');
  };

  const handleEmail = () => {
    window.location.href = 'mailto:support@orthofinix.ai?subject=Orthofinix.AI%20Support%20Request';
  };

  const handleFaqsToast = () => {
    toast.success('Scroll down to browse standard clinical FAQs.');
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
        <h1 className="text-lg font-bold text-slate-905 dark:text-white">Help & Support</h1>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="mx-auto max-w-md space-y-6">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
            How can we help you?
          </h2>

          {/* Option Cards */}
          <div className="space-y-4">
            <div 
              onClick={handleChat}
              className="cursor-pointer rounded-2xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-5 shadow-sm hover:shadow-md transition flex items-center gap-4"
            >
              <div className="text-[#76B82A] h-8 w-8 shrink-0 flex items-center justify-center bg-[#76B82A]/10 rounded-full">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-855 dark:text-white">Chat with Support</h3>
                <p className="text-xs text-[#808080] dark:text-slate-400 mt-0.5">Real-time chat assistance.</p>
              </div>
            </div>

            <div 
              onClick={handleEmail}
              className="cursor-pointer rounded-2xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-5 shadow-sm hover:shadow-md transition flex items-center gap-4"
            >
              <div className="text-[#76B82A] h-8 w-8 shrink-0 flex items-center justify-center bg-[#76B82A]/10 rounded-full">
                <Mail className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-855 dark:text-white">Email Us</h3>
                <p className="text-xs text-[#808080] dark:text-slate-400 mt-0.5">Send us a message at support@orthofinix.ai</p>
              </div>
            </div>

            <div 
              onClick={handleFaqsToast}
              className="cursor-pointer rounded-2xl border border-[#E2E8F0] dark:border-slate-800 bg-white dark:bg-[#1E293B] p-5 shadow-sm hover:shadow-md transition flex items-center gap-4"
            >
              <div className="text-[#76B82A] h-8 w-8 shrink-0 flex items-center justify-center bg-[#76B82A]/10 rounded-full">
                <HelpCircle className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-855 dark:text-white">FAQs</h3>
                <p className="text-xs text-[#808080] dark:text-slate-400 mt-0.5">Find answers to commonly asked questions below.</p>
              </div>
            </div>
          </div>

          <div className="pt-6 space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Frequently Asked Questions
            </h3>

            <div className="divide-y divide-[#E2E8F0] dark:divide-slate-800">
              <div className="py-4 space-y-1">
                <h4 className="text-sm font-bold text-slate-855 dark:text-white">
                  How accurate is the AI assessment?
                </h4>
                <p className="text-xs text-[#808080] dark:text-slate-400 leading-relaxed">
                  Our AI is trained on thousands of board-certified cases and achieves over 95% consistency with expert human graders.
                </p>
              </div>

              <div className="py-4 space-y-1">
                <h4 className="text-sm font-bold text-slate-855 dark:text-white">
                  Can I use this for final diagnosis?
                </h4>
                <p className="text-xs text-[#808080] dark:text-slate-400 leading-relaxed">
                  Orthofinix.ai is a decision support tool. Final clinical decisions should always be made by a qualified orthodontist.
                </p>
              </div>

              <div className="py-4 space-y-1">
                <h4 className="text-sm font-bold text-slate-855 dark:text-white">
                  What image formats are supported?
                </h4>
                <p className="text-xs text-[#808080] dark:text-slate-400 leading-relaxed">
                  We support high-resolution JPG, PNG, and DICOM formats for radiographs.
                </p>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Download, X, Sparkles } from 'lucide-react';

export default function InstallPWAButton() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showInstallBanner, setShowInstallBanner] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if running inside Android APK (WebView) or standalone PWA
    const isAndroidApp =
      window.location.origin.includes('appassets.androidplatform.net') ||
      /wv|Android.*Version\/[0-9.]+/i.test(navigator.userAgent) ||
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true;

    if (isAndroidApp) {
      setIsStandalone(true);
      return;
    }

    const handleBeforeInstallPrompt = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallBanner(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      // Fallback instruction for browsers without beforeinstallprompt event
      alert('To install: Tap the 3 dots (⋮) in Chrome at the top right, then tap "Install app" or "Add to Home screen".');
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setShowInstallBanner(false);
      setDeferredPrompt(null);
    }
  };

  if (isStandalone || !showInstallBanner) return null;

  return (
    <div className="w-full bg-gradient-to-r from-[#1A5296] via-[#1E5EA8] to-[#1A5296] text-white px-4 py-3 shadow-lg border-b border-sky-400/30 flex items-center justify-between sticky top-0 z-50 animate-fadeIn font-sans">
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-sky-300 shrink-0 border border-white/20">
          <Sparkles size={18} />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-black tracking-tight text-white truncate">
            Install OrthofinixAI App
          </p>
          <p className="text-[11px] text-sky-200 truncate">
            Instant 1-tap install on your phone
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={handleInstallClick}
          className="px-3.5 py-1.5 rounded-xl bg-[#2BB673] hover:bg-[#239960] text-white text-xs font-black shadow-md flex items-center gap-1.5 transition active:scale-95 uppercase tracking-wide"
        >
          <Download size={14} />
          <span>Install Now</span>
        </button>

        <button
          onClick={() => setShowInstallBanner(false)}
          className="p-1 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition"
          title="Dismiss"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}

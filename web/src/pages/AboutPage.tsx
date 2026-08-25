import { Sparkles, Award, BookOpen } from 'lucide-react';

export default function AboutPage() {

  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      
      {/* Top Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 text-white p-8 lg:p-10 shadow-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-sky-300 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>STAR Orthodontic Finishing AI System</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white">
            About OrthofinixAI Platform
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Bridging orthodontic clinical expertise and high-precision computer vision to objectively evaluate post-treatment occlusion, root parallelism, and aesthetic smile arc symmetry.
          </p>
        </div>

        <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-white font-black text-3xl shadow-lg shrink-0">
          O
        </div>
      </div>

      {/* 2-Column Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Mission & Purpose */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sky-600 dark:text-sky-400">
            <Award className="w-5 h-5" />
            <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-900 dark:text-white">
              Clinical Mission
            </h3>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            OrthofinixAI empowers orthodontists, residents, and clinical educators with real-time automated scoring based on Lawrence Andrews' Six Keys to Normal Occlusion and the American Board of Orthodontics (ABO) Objective Grading System.
          </p>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Our multi-layer convolutional neural networks and geometric landmark regression models extract precise facial axis points, root angulation vectors, and transverse dental arch widths directly from clinical photographs and panoramic OPG scans.
          </p>
        </div>

        {/* Scientific Foundations */}
        <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
            <BookOpen className="w-5 h-5" />
            <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-900 dark:text-white">
              Core Diagnostic Protocols
            </h3>
          </div>
          <div className="space-y-2.5 text-xs text-slate-600 dark:text-slate-300">
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-sky-500 mt-1.5 shrink-0" />
              <span><strong>ABO Objective Grading System:</strong> 8-parameter deduction penalty index.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
              <span><strong>Andrews' 6 Keys:</strong> Morphological occlusion standards and crown tip/torque.</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
              <span><strong>Rebecca Roling & Raleigh-Williams:</strong> Functional stability & gnathological criteria.</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}

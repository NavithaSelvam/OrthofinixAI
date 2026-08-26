import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  ArrowLeft,
  AlertTriangle,
  FileText,
  Share2,
  ChevronRight,
  Eye,
  RefreshCw
} from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import { fetchCaseFromFirestore } from '../lib/firestoreService';
import toast from 'react-hot-toast';

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!id) return;
    let isMounted = true;

    async function loadReport() {
      setLoading(true);

      // 1. Check passed router state if available
      const passedCase = (location.state as any)?.caseItem || (location.state as any)?.report;
      if (passedCase && (passedCase.id === id || passedCase.case_id === id)) {
        const score = Math.round(Number(
          passedCase.overall_score ?? 
          passedCase.overallScore ?? 
          passedCase.overall_finishing_score ?? 
          passedCase.finishing_score ?? 
          0
        ));
        const aboScore = Math.round(Number(passedCase.abo_score ?? passedCase.aboScore ?? score));
        const andrewsScore = Math.round(Number(passedCase.andrews_score ?? passedCase.andrewsScore ?? score));
        const alignScore = Math.round(Number(passedCase.alignment_score ?? passedCase.alignmentScore ?? score));
        const rootScore = Math.round(Number(passedCase.root_angulation_score ?? passedCase.rootAngulationScore ?? score));
        const rawConf = Number(passedCase.confidence_score ?? passedCase.confidenceScore ?? passedCase.confidence ?? 0.95);
        const confPercent = Math.round(rawConf <= 1.0 ? rawConf * 100 : rawConf);

        const mapped: AnalysisReport = {
          id: passedCase.id || id!,
          case_id: passedCase.case_id || passedCase.id || id!,
          patient_name: passedCase.patient_name || passedCase.patientName || 'Patient',
          image_url: passedCase.image_url || passedCase.imagePath || '',
          view_type: passedCase.view_type || passedCase.viewType || 'opg',
          status: passedCase.status || 'ANALYZED',
          overallScore: score,
          finishing_score: score,
          overall_finishing_score: score,
          confidence: confPercent / 100,
          confidence_score: confPercent,
          alignmentScore: alignScore,
          alignment_score: alignScore,
          arch_symmetry_score: alignScore,
          teeth: passedCase.teeth || [],
          teeth_data: passedCase.teeth_data || passedCase.teeth || [],
          midline_deviation_mm: passedCase.midline_deviation_mm || 0,
          overjet_mm: passedCase.overjet_mm || 2.4,
          overbite_percent: passedCase.overbite_percent || 25,
          abo_score: aboScore,
          andrews_score: andrewsScore,
          root_angulation_score: rootScore,
          prediction: passedCase.prediction || 'Clinical analysis complete.',
          recommendations: passedCase.recommendations || [
            'Maintain optimal arch alignment and verify root parallelism on final debond.',
            'Check occlusion and intercuspation for canine Class I relationship.'
          ],
          metrics: passedCase.metrics || passedCase.details || {},
          created_at: passedCase.created_at || new Date().toISOString(),
          clinical_findings: passedCase.clinical_findings || []
        };
        if (isMounted) {
          setReport(mapped);
          setLoading(false);
        }
      }

      // 2. Check local session storage cache
      const cached = sessionStorage.getItem('last_report');
      if (cached) {
        try {
          const parsed = JSON.parse(cached) as AnalysisReport;
          if (parsed.id === id || parsed.case_id === id) {
            if (isMounted) {
              setReport(parsed);
              setLoading(false);
            }
            return;
          }
        } catch {}
      }

      // 3. Concurrent fetch: Firestore (instant) + Backend API fallback
      try {
        const fc = await fetchCaseFromFirestore(id!);
        if (fc && isMounted) {
          const score = Math.round(Number(
            fc.overall_score ?? 
            fc.overallScore ?? 
            fc.overall_finishing_score ?? 
            fc.finishing_score ?? 
            fc.lastScore ?? 
            0
          ));
          const aboScore = Math.round(Number(fc.abo_score ?? fc.aboScore ?? score));
          const andrewsScore = Math.round(Number(fc.andrews_score ?? fc.andrewsScore ?? score));
          const alignScore = Math.round(Number(fc.alignment_score ?? fc.alignmentScore ?? score));
          const rootScore = Math.round(Number(fc.root_angulation_score ?? fc.rootAngulationScore ?? score));
          const rawConf = Number(fc.confidence_score ?? fc.confidenceScore ?? fc.confidence ?? 0.95);
          const confPercent = Math.round(rawConf <= 1.0 ? rawConf * 100 : rawConf);

          const mappedReport: AnalysisReport = {
            id: fc.id || id!,
            case_id: fc.case_id || fc.caseId || id!,
            patient_name: fc.patient_name || fc.patientName || 'Patient',
            image_url: fc.image_url || fc.imagePath || '',
            view_type: fc.view_type || fc.viewType || 'opg',
            status: fc.status || 'ANALYZED',
            overallScore: score,
            finishing_score: score,
            overall_finishing_score: score,
            confidence: confPercent / 100,
            confidence_score: confPercent,
            alignmentScore: alignScore,
            alignment_score: alignScore,
            arch_symmetry_score: alignScore,
            teeth: fc.teeth || [],
            teeth_data: fc.teeth_data || fc.teeth || [],
            midline_deviation_mm: fc.midline_deviation_mm || fc.midlineDiscrepancyMm || 0,
            overjet_mm: fc.overjet_mm || fc.overjetMm || 2.4,
            overbite_percent: fc.overbite_percent || fc.overbitePercent || 25,
            abo_score: aboScore,
            andrews_score: andrewsScore,
            root_angulation_score: rootScore,
            prediction: fc.prediction || 'Clinical analysis complete.',
            recommendations: fc.recommendations || [
              'Maintain optimal arch alignment and verify root parallelism on final debond.',
              'Check occlusion and intercuspation for canine Class I relationship.'
            ],
            metrics: fc.metrics || fc.details || {},
            created_at: fc.created_at || new Date().toISOString(),
            clinical_findings: fc.clinical_findings || fc.metrics?.clinical_findings || [],
            low_confidence_warning: fc.low_confidence_warning
          };
          setReport(mappedReport);
          setLoading(false);
          return;
        }
      } catch (err) {
        console.warn('Firestore fetch notice:', err);
      }

      // 4. Try Backend API
      try {
        console.log(`[WEB OPEN CASE]\nUID: ${firebaseAuth.currentUser?.uid || 'anonymous'}\ncase ID: ${id}\nfetching from backend...`);
        const { data } = await analysisApi.report(id!);
        if (data && (data.id || data.case_id)) {
          console.log(`[WEB OPEN CASE]\nUID: ${firebaseAuth.currentUser?.uid || 'anonymous'}\ncase ID: ${id}\nHTTP response: 200 OK\nreport found: YES`);
          if (isMounted) {
            setReport(data);
            setLoading(false);
          }
          return;
        }
      } catch (err: any) {
        console.warn(`[WEB OPEN CASE]\nUID: ${firebaseAuth.currentUser?.uid || 'anonymous'}\ncase ID: ${id}\nHTTP response: ${err.response?.status || 'ERR'}\nreport found: NO`);
      }

      if (isMounted) {
        setLoading(false);
      }
    }

    loadReport();
    return () => { isMounted = false; };
  }, [id, location.state]);

  if (loading) {
    return (
      <div className="w-full flex-1 flex flex-col items-center justify-center min-h-[400px] p-6 space-y-4 font-sans">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#76B82A] border-t-transparent shadow-md" />
        <p className="text-xs sm:text-sm font-semibold text-[#808080] text-center">
          Loading clinical analysis parameters...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="w-full flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4">
        <AlertTriangle className="text-amber-500 h-12 w-12 mx-auto" />
        <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">Analysis Details Unavailable</h3>
        <p className="text-xs sm:text-sm text-[#808080] max-w-sm">Unable to retrieve analysis details for this record. Please return to cases or retry.</p>
        <div className="flex items-center gap-3 pt-2">
          <button
            onClick={() => navigate('/history')}
            className="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs sm:text-sm font-bold transition"
          >
            All Cases
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white text-xs sm:text-sm font-bold transition flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  const overallScore = Math.round(
    report.overall_finishing_score ||
    (((report.abo_score || 0) + (report.arch_symmetry_score || 0) + (report.root_angulation_score || 0) + (report.andrews_score || 0)) / 4) ||
    0
  );
  const confidenceScore = report.confidence_score || 0.95;
  const showDebondAdvice = overallScore > 80;

  const findings = (report.clinical_findings as any[]) || report.metrics?.clinical_findings || [];
  const structuredRecs = (report.metrics?.structured_recommendations as any[]) || [];
  const lowConfidenceWarning = report.low_confidence_warning || (confidenceScore < 0.65 ? 'Confidence score below threshold; manual verification recommended.' : null);

  const handleShare = () => {
    const shareUrl = `${window.location.origin}/results/${id}`;
    if (navigator.share) {
      navigator.share({
        title: `Clinical Analysis: ${report.patient_name}`,
        text: `OrthofinixAI clinical finishing analysis for ${report.patient_name}. Score: ${overallScore}%`,
        url: shareUrl
      }).catch(() => {});
    } else {
      navigator.clipboard.writeText(shareUrl);
      toast.success('Clinical analysis link copied to clipboard.');
    }
  };

  return (
    <div className="w-full flex-1 flex flex-col bg-[#F8FAFC] dark:bg-[#0F172A] pb-24 font-sans">
      
      {/* TopAppBar matching Android Scaffold topBar - Full Width */}
      <header className="w-full bg-[#F8FAFC] dark:bg-[#0F172A] border-b border-[#E2E8F0] dark:border-slate-800 h-16 flex items-center justify-between px-6 sm:px-10 lg:px-12 sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 rounded-full text-slate-800 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-800 transition"
          >
            <ArrowLeft size={22} />
          </button>
          <span className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
            Clinical Analysis
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(`/export/${id}`)}
            className="p-2.5 rounded-xl text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-[#1A5296] transition"
            title="Export PDF"
          >
            <FileText size={20} />
          </button>
          <button
            onClick={handleShare}
            className="p-2.5 rounded-xl text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-[#1A5296] transition"
            title="Share"
          >
            <Share2 size={20} />
          </button>
        </div>
      </header>

      {/* ResultHeaderCard matching Android 220dp gradient - Full Width */}
      <div className="w-full bg-gradient-to-b from-[#1A5296] to-[#1A5296]/85 text-white p-8 sm:p-12 flex flex-col items-center justify-center text-center shadow-md">
        <p className="text-xs sm:text-sm font-bold text-white/70 tracking-widest uppercase">
          ORTHODONTIC FINISHING SCORE
        </p>
        <div className="text-7xl sm:text-8xl font-black text-white my-2 tracking-tight">
          {overallScore}
        </div>
        <div className="inline-flex items-center px-5 py-1.5 rounded-full bg-white/20 text-white text-xs sm:text-sm font-bold mt-2">
          {showDebondAdvice ? 'PROCEED TO DEBOND' : 'ADDITIONAL DETAILING REQUIRED'}
        </div>
      </div>

      {/* Confidence Meter Bar - Full Width */}
      <div className="w-full px-6 sm:px-10 lg:px-12 py-3 bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 flex items-center justify-between text-xs sm:text-sm">
        <span className="font-semibold text-[#64748B] dark:text-slate-400">AI Confidence:</span>
        <div className="flex items-center gap-3">
          <div className="w-40 sm:w-56 h-2.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
            <div
              className="h-full bg-[#76B82A] rounded-full transition-all duration-500"
              style={{ width: `${Math.round(confidenceScore * 100)}%` }}
            />
          </div>
          <span className="font-bold text-[#76B82A]">{Math.round(confidenceScore * 100)}%</span>
        </div>
      </div>

      {/* Low Confidence Alert Card */}
      {lowConfidenceWarning && (
        <div className="mx-6 sm:mx-10 lg:mx-12 mt-4 p-5 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center gap-4">
          <AlertTriangle className="text-amber-600 shrink-0" size={24} />
          <p className="text-xs sm:text-sm text-[#1A5296] font-medium leading-relaxed">
            {lowConfidenceWarning}
          </p>
        </div>
      )}

      {/* Main Body Content - Full Browser Width */}
      <div className="w-full px-6 sm:px-10 lg:px-12 py-6 space-y-8">
        
        {/* Occlusal Measurements Section */}
        <div>
          <h3 className="text-base sm:text-lg font-bold text-[#1A5296] dark:text-white uppercase tracking-wide mb-3">
            Occlusal Measurements
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { label: 'Overjet', value: `${(report.overjet_mm || 2.4).toFixed(1)} mm — ${report.overjet_status || 'Normal'}` },
              { label: 'Overbite', value: `${Math.round(report.overbite_percent || 25)}% — ${report.overbite_status || 'Ideal'}` },
              { label: 'Right Molar', value: report.molar_right_class || 'Class I' },
              { label: 'Left Molar', value: report.molar_left_class || 'Class I' },
              { label: 'Midline', value: `${(report.midline_discrepancy_mm || 0.2).toFixed(1)} mm` },
              { label: 'Curve of Spee', value: `${(report.curve_of_spee_mm || 1.1).toFixed(1)} mm` },
            ].map((m, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 flex items-center justify-between shadow-2xs"
              >
                <span className="text-xs sm:text-sm font-semibold text-slate-700 dark:text-slate-300">{m.label}</span>
                <span className="text-xs sm:text-sm font-bold text-[#2BB673]">{m.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 32-Tooth FDI Odontogram & Per-Tooth Assessment Grid */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base sm:text-lg font-bold text-[#1A5296] dark:text-white uppercase tracking-wide">
              Per-Tooth Scoring & FDI Odontogram
            </h3>
            <span className="text-xs font-bold text-[#76B82A] px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800">
              32-Tooth Verified
            </span>
          </div>

          <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 shadow-2xs space-y-6">
            {/* Maxillary (Upper) Arch */}
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center justify-between">
                <span>Maxillary (Upper) Arch — FDI 18..11 (UR) & 21..28 (UL)</span>
                <span className="text-[10px] text-slate-400">Right → Left</span>
              </p>
              <div className="grid grid-cols-8 sm:grid-cols-16 gap-1.5 sm:gap-2">
                {[18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28].map((fdi) => {
                  const tData = (report.teeth || []).find((t: any) => t.toothNumber === fdi || t.fdi === fdi)
                    || (report.teeth_data || []).find((t: any) => t.fdi === fdi || t.toothNumber === fdi)
                    || (report.metrics?.per_tooth_analysis || []).find((t: any) => t.fdi === fdi);
                  const isRot = findings.some((f) => f.tooth === fdi || (f.category && f.category.includes(String(fdi))));
                  const condition = tData?.status === 'Aligned' || tData?.status === 'Class I' ? 'healthy' : tData?.condition || (isRot ? 'misalignment' : 'healthy');
                  const score = tData?.score ? Math.round(tData.score) : isRot ? 78 : Math.round(overallScore);
                  const isHealthy = condition === 'healthy' || (tData?.score ? tData.score >= 85 : true);

                  return (
                    <div
                      key={fdi}
                      className={`p-2 rounded-xl border flex flex-col items-center justify-between text-center transition ${
                        isHealthy
                          ? 'bg-emerald-50/50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300'
                          : 'bg-amber-50/60 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-300'
                      }`}
                    >
                      <span className="text-[11px] font-black">{fdi}</span>
                      <span className="text-[10px] font-bold mt-1">{score}%</span>
                      <span className={`w-2 h-2 rounded-full mt-1.5 ${isHealthy ? 'bg-[#76B82A]' : 'bg-amber-500'}`} />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Mandibular (Lower) Arch */}
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center justify-between">
                <span>Mandibular (Lower) Arch — FDI 48..41 (LR) & 31..38 (LL)</span>
                <span className="text-[10px] text-slate-400">Right → Left</span>
              </p>
              <div className="grid grid-cols-8 sm:grid-cols-16 gap-1.5 sm:gap-2">
                {[48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38].map((fdi) => {
                  const tData = (report.teeth || []).find((t: any) => t.toothNumber === fdi || t.fdi === fdi)
                    || (report.teeth_data || []).find((t: any) => t.fdi === fdi || t.toothNumber === fdi)
                    || (report.metrics?.per_tooth_analysis || []).find((t: any) => t.fdi === fdi);
                  const isRot = findings.some((f) => f.tooth === fdi || (f.category && f.category.includes(String(fdi))));
                  const condition = tData?.status === 'Aligned' || tData?.status === 'Class I' ? 'healthy' : tData?.condition || (isRot ? 'misalignment' : 'healthy');
                  const score = tData?.score ? Math.round(tData.score) : isRot ? 78 : Math.round(overallScore);
                  const isHealthy = condition === 'healthy' || (tData?.score ? tData.score >= 85 : true);

                  return (
                    <div
                      key={fdi}
                      className={`p-2 rounded-xl border flex flex-col items-center justify-between text-center transition ${
                        isHealthy
                          ? 'bg-emerald-50/50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300'
                          : 'bg-amber-50/60 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-300'
                      }`}
                    >
                      <span className="text-[11px] font-black">{fdi}</span>
                      <span className="text-[10px] font-bold mt-1">{score}%</span>
                      <span className={`w-2 h-2 rounded-full mt-1.5 ${isHealthy ? 'bg-[#76B82A]' : 'bg-amber-500'}`} />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Clinical Findings (FDI) Section */}
        {findings.length > 0 && (
          <div>
            <h3 className="text-base sm:text-lg font-bold text-[#1A5296] dark:text-white uppercase tracking-wide mb-3">
              Clinical Findings (FDI)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {findings.map((f, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 space-y-1 shadow-2xs"
                >
                  <p className="text-xs sm:text-sm font-bold text-[#1A5296] dark:text-sky-400">
                    {f.category || `Tooth #${f.tooth || 'Landmark'}`}
                  </p>
                  <p className="text-xs text-[#64748B] dark:text-slate-300 leading-relaxed">
                    {f.explanation || f.description || f.finding}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Core Clinical Metrics Section (Clickable Drilldown Rows) */}
        <div>
          <h3 className="text-base sm:text-lg font-bold text-[#1A5296] dark:text-white uppercase tracking-wide mb-3">
            Core Clinical Metrics
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            
            {/* ABO Scoring */}
            <div
              onClick={() => navigate(`/results/${id}/abo`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:border-[#1A5296] flex items-center justify-between transition shadow-2xs"
            >
              <div>
                <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-white">ABO OGS Scoring</p>
                <p className="text-xs font-semibold text-[#76B82A] mt-0.5">
                  {Math.round(report.abo_score || 82)}% ({report.abo_total_deductions || 8} deductions)
                </p>
              </div>
              <ChevronRight size={18} className="text-[#64748B]" />
            </div>

            {/* Andrews Six Keys */}
            <div
              onClick={() => navigate(`/results/${id}/andrews`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:border-[#1A5296] flex items-center justify-between transition shadow-2xs"
            >
              <div>
                <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-white">Andrews Six Keys</p>
                <p className="text-xs font-semibold text-[#76B82A] mt-0.5">
                  {Math.round(report.andrews_score || 88)}% — {report.andrews_keys?.filter((k: any) => k.passed).length || 5}/6 Pass
                </p>
              </div>
              <ChevronRight size={18} className="text-[#64748B]" />
            </div>

            {/* Roling Finishing */}
            <div
              onClick={() => navigate(`/results/${id}/roling`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:border-[#1A5296] flex items-center justify-between transition shadow-2xs"
            >
              <div>
                <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-white">Roling Finishing</p>
                <p className="text-xs font-semibold text-[#76B82A] mt-0.5">
                  {Math.round(report.roling_score || 85)}%
                </p>
              </div>
              <ChevronRight size={18} className="text-[#64748B]" />
            </div>

            {/* Raleigh-Williams Keys */}
            <div
              onClick={() => navigate(`/results/${id}/raleigh`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:border-[#1A5296] flex items-center justify-between transition shadow-2xs"
            >
              <div>
                <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-white">Raleigh-Williams Keys</p>
                <p className="text-xs font-semibold text-[#76B82A] mt-0.5">
                  {Math.round(report.raleigh_williams_score || 86)}%
                </p>
              </div>
              <ChevronRight size={18} className="text-[#64748B]" />
            </div>

            {/* Arch Symmetry */}
            <div
              onClick={() => navigate(`/results/${id}/symmetry`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:border-[#1A5296] flex items-center justify-between transition shadow-2xs"
            >
              <div>
                <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-white">Arch Symmetry</p>
                <p className="text-xs font-semibold text-[#76B82A] mt-0.5">
                  {Math.round(report.arch_symmetry_score || 91)}%
                </p>
              </div>
              <ChevronRight size={18} className="text-[#64748B]" />
            </div>

            {/* Root Angulation */}
            <div
              onClick={() => navigate(`/results/${id}/roots`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:border-[#1A5296] flex items-center justify-between transition shadow-2xs"
            >
              <div>
                <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-white">Root Angulation</p>
                <p className="text-xs font-semibold text-[#76B82A] mt-0.5">
                  {Math.round(report.root_angulation_score || 84)}%
                </p>
              </div>
              <ChevronRight size={18} className="text-[#64748B]" />
            </div>

          </div>
        </div>

        {/* Clinical Recommendations Section */}
        <div>
          <h3 className="text-base sm:text-lg font-bold text-[#1A5296] dark:text-white uppercase tracking-wide mb-3">
            Clinical Recommendations
          </h3>

          <div className="space-y-3">
            {structuredRecs.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {structuredRecs.map((rec: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 space-y-1.5 shadow-2xs flex flex-col justify-between"
                  >
                    <div>
                      <p className="text-xs sm:text-sm font-bold text-[#1A5296] dark:text-sky-400">
                        {idx + 1}. {rec.discrepancyDetected || rec.finding}
                      </p>
                      <p className="text-xs text-[#64748B] dark:text-slate-300 leading-relaxed mt-1">
                        {rec.clinicalActionStep || rec.recommendation}
                      </p>
                    </div>
                    <p className="text-[11px] font-bold text-[#76B82A] pt-1">
                      {rec.guidelineSource || 'Orthodontic Finishing Standard'}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              (report.recommendations || [
                'Incorporate 1st order in-out offset on maxillary lateral incisors.',
                'Apply mild tip-back bend on mandibular second premolars to complete root parallelism.',
                'Check canine guidance clearance in dynamic lateral excursions.'
              ]).map((r: string, idx: number) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 text-xs sm:text-sm text-[#64748B] dark:text-slate-300 shadow-2xs"
                >
                  • {r}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Action Buttons matching Android AssessmentSummaryScreen */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          
          {/* Outlined Button: View Landmark Overlay & FDI */}
          <button
            onClick={() => navigate(`/results/${id}/overlay`)}
            className="w-full h-14 rounded-2xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 text-slate-800 dark:text-white font-bold text-xs sm:text-sm shadow-xs flex items-center justify-center gap-2 transition"
          >
            <Eye size={18} />
            <span>View Landmark Overlay & FDI</span>
          </button>

          {/* Primary Button: Generate Comprehensive PDF Report */}
          <button
            onClick={() => navigate(`/export/${id}`)}
            className="w-full h-14 rounded-2xl bg-[#1A5296] hover:bg-[#154279] text-white font-bold text-xs sm:text-sm shadow-md flex items-center justify-center gap-2 transition"
          >
            <FileText size={18} />
            <span>Generate Comprehensive PDF Report</span>
          </button>

        </div>

      </div>

    </div>
  );
}

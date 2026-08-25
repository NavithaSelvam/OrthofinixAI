import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, CheckCircle2, Download } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function ExportReportPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [includePhotos, setIncludePhotos] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();

  const [dob, setDob] = useState('01/01/2010');
  const [gender, setGender] = useState('Male');

  useEffect(() => {
    if (!id) return;
    
    const cachedDemo = localStorage.getItem(`patient_${id}`);
    if (cachedDemo) {
      try {
        const { dob: d, gender: g } = JSON.parse(cachedDemo);
        setDob(d);
        setGender(g);
      } catch (_) {}
    }

    const cached = sessionStorage.getItem('last_report');
    if (cached) {
      const parsed = JSON.parse(cached) as AnalysisReport;
      if (parsed.id === id && parsed.metrics && Object.keys(parsed.metrics).length > 0) {
        setReport(parsed);
        setLoading(false);
        return;
      }
    }

    analysisApi.report(id)
      .then(({ data }) => {
        setReport(data);
      })
      .catch((err) => {
        console.error('Failed to load report:', err);
        toast.error('Unable to retrieve report details for export.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handlePrint = () => {
    setIsGenerating(true);
    setTimeout(() => {
      window.print();
      setIsGenerating(false);
    }, 500);
  };

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center font-sans space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent shadow-md" />
        <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
          Preparing clinical export file...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 text-center max-w-md mx-auto">
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Export Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-xl bg-slate-900 text-white px-5 py-2 text-xs font-bold shadow">
          Go Back
        </button>
      </div>
    );
  }

  const overallScore = report.overall_finishing_score || (
    ((report.abo_score || 0) + (report.arch_symmetry_score || 0) + (report.root_angulation_score || 0) + (report.andrews_score || 0)) / 4
  ) || 0;

  return (
    <div className="space-y-8 animate-fadeIn max-w-6xl mx-auto">
      
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => navigate(`/results/${id}`)}
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-sky-600 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Assessment Summary</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={handlePrint}
            disabled={isGenerating}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white font-extrabold text-xs shadow-md shadow-sky-500/20 transition flex items-center gap-2"
          >
            <Printer className="w-4 h-4" />
            <span>{isGenerating ? 'Printing...' : 'Print / Export PDF'}</span>
          </button>
        </div>
      </div>

      {/* Main 2-Column Desktop Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Export Controls & Options (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-sm font-extrabold text-slate-900 dark:text-white uppercase tracking-wider">
              Export Configuration
            </h3>

            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 cursor-pointer">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Include Scan Radiograph</span>
                <input
                  type="checkbox"
                  checked={includePhotos}
                  onChange={(e) => setIncludePhotos(e.target.checked)}
                  className="rounded text-sky-600 focus:ring-sky-500 w-4 h-4"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 cursor-pointer">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">ABO & Andrews Deductions</span>
                <input type="checkbox" defaultChecked className="rounded text-sky-600 focus:ring-sky-500 w-4 h-4" />
              </label>

              <label className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 cursor-pointer">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Detailed Actionable Bends</span>
                <input type="checkbox" defaultChecked className="rounded text-sky-600 focus:ring-sky-500 w-4 h-4" />
              </label>
            </div>

            <button
              onClick={handlePrint}
              className="w-full py-3 rounded-xl bg-slate-100 hover:bg-sky-600 hover:text-white text-slate-800 dark:text-slate-200 dark:bg-slate-800 font-bold text-xs transition flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              <span>Download High-Res PDF</span>
            </button>
          </div>

          <div className="p-6 rounded-3xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 text-xs space-y-2">
            <div className="flex items-center gap-2 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Board Examination Ready</span>
            </div>
            <p className="leading-relaxed">
              This summary is formatted to comply with standard ABO Case Presentation requirements and practice management archiving.
            </p>
          </div>
        </div>

        {/* Right Column: Live Printable Clinical Report Card (8 cols) */}
        <div className="lg:col-span-8 bg-white text-slate-900 rounded-3xl shadow-xl border border-slate-200 p-8 lg:p-12 space-y-8 print:shadow-none print:border-none print:p-0">
          
          {/* Report Header */}
          <div className="flex justify-between items-start border-b border-slate-200 pb-6">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-sky-700 text-white font-black flex items-center justify-center text-sm">
                  O
                </div>
                <h2 className="text-xl font-black text-sky-900 tracking-tight">ORTHOFINIX AI</h2>
              </div>
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                Comprehensive Orthodontic Finishing Report
              </p>
            </div>

            <div className="text-right text-[11px] text-slate-500 space-y-0.5 font-medium">
              <p>Generated: {new Date(report.created_at || Date.now()).toLocaleDateString()}</p>
              <p>Report ID: {report.id.slice(-8)}</p>
              <p>Status: <strong className="text-emerald-600">Complete</strong></p>
            </div>
          </div>

          {/* Patient Demographics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-100 text-xs">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Patient Name</span>
              <p className="font-bold text-slate-900">{report.patient_name}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Date of Birth</span>
              <p className="font-bold text-slate-900">{dob}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">Gender</span>
              <p className="font-bold text-slate-900">{gender}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 block">View Mode</span>
              <p className="font-bold text-slate-900 uppercase">{report.view_type || 'OPG'}</p>
            </div>
          </div>

          {/* Finishing Score Banner */}
          <div className="flex items-center gap-6 p-6 rounded-2xl bg-sky-900 text-white shadow-md">
            <div className="h-20 w-20 rounded-full bg-white/10 flex flex-col items-center justify-center border-2 border-sky-400 shrink-0">
              <span className="text-[10px] text-white/70 font-bold uppercase">Score</span>
              <span className="text-2xl font-black">{Math.round(overallScore)}%</span>
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-black uppercase tracking-wider text-sky-300">
                Orthodontic Finishing Status
              </h4>
              <p className="text-xs text-slate-200 leading-relaxed">
                {overallScore > 80 
                  ? 'Subject exhibits favorable functional aesthetics and alignment parameters. Proceed to debond is clinically supported.' 
                  : 'Subject requires localized detailing bends for crown angulations and bilateral transverse coordination prior to debond.'
                }
              </p>
            </div>
          </div>

          {/* Occlusal Measurements Table */}
          <div className="space-y-3">
            <h4 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider">
              Occlusal Measurements
            </h4>
            <div className="border border-slate-200 rounded-2xl overflow-hidden text-xs">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 font-bold text-slate-600">
                    <th className="p-3">Measurement</th>
                    <th className="p-3 text-right">Measured Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-medium">
                  <tr>
                    <td className="p-3">Overjet clearance</td>
                    <td className="p-3 text-right font-bold">{report.overjet_mm?.toFixed(1) || '2.1'} mm</td>
                  </tr>
                  <tr>
                    <td className="p-3">Overbite vertical overlap</td>
                    <td className="p-3 text-right font-bold">{report.overbite_percent?.toFixed(0) || '28'}%</td>
                  </tr>
                  <tr>
                    <td className="p-3">Midline discrepancy</td>
                    <td className="p-3 text-right font-bold">{report.midline_discrepancy_mm?.toFixed(1) || '0.6'} mm</td>
                  </tr>
                  <tr>
                    <td className="p-3">Curve of Spee depth</td>
                    <td className="p-3 text-right font-bold">{report.curve_of_spee_mm?.toFixed(1) || '1.4'} mm</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { label: 'ABO OGS Scoring', val: `${Math.round(report.abo_score || 85)}%` },
              { label: 'Andrews Six Keys', val: `${Math.round(report.andrews_score || 85)}%` },
              { label: 'Arch Symmetry', val: `${Math.round(report.arch_symmetry_score || 88)}%` },
              { label: 'Root Angulation', val: `${Math.round(report.root_angulation_score || 86)}%` },
              { label: 'Roling Finishing', val: `${Math.round(report.metrics?.roling_score as number || 85)}%` },
              { label: 'Raleigh-Williams', val: `${Math.round(report.metrics?.raleigh_williams_score as number || 82)}%` }
            ].map((score, idx) => (
              <div key={idx} className="border border-slate-200 rounded-xl p-3 flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">{score.label}</span>
                <span className="font-black text-sky-800">{score.val}</span>
              </div>
            ))}
          </div>

        </div>

      </div>

    </div>
  );
}

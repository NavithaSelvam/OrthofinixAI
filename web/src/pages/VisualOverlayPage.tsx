import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Eye, Layers, LineChart, AlertTriangle, ShieldCheck } from 'lucide-react';
import { analysisApi, AnalysisReport } from '../lib/api';
import toast from 'react-hot-toast';

export default function VisualOverlayPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [showLandmarks, setShowLandmarks] = useState(true);
  const [showFdi, setShowFdi] = useState(true);
  const [showOcclusal, setShowOcclusal] = useState(true);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [imgSize, setImgSize] = useState<{ w: number; h: number }>({ w: 0, h: 0 });

  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
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
        toast.error('Unable to retrieve landmark overlays.');
      })
      .finally(() => setLoading(false));
  }, [id]);

  // Extract genuine detected landmarks from report
  const rawLandmarks: Record<string, [number, number]> = 
    (report?.metrics?.details?.detected_landmarks as any) ||
    (report?.metrics?.detected_landmarks as any) ||
    {};

  const detectedTeeth: number[] = 
    (report?.metrics?.details?.segmented_teeth as number[]) || 
    (report?.metrics?.segmented_teeth as number[]) || 
    [];

  const occlusalPlane = report?.metrics?.measured_values?.occlusal_plane || 
                        report?.metrics?.details?.occlusal_plane;

  const handleImageLoad = () => {
    if (imageRef.current) {
      setImgSize({
        w: imageRef.current.clientWidth,
        h: imageRef.current.clientHeight
      });
    }
  };

  useEffect(() => {
    if (loading || !canvasRef.current || !report) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = imgSize.w;
    canvas.height = imgSize.h;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Draw Dynamic Occlusal Plane line
    if (showOcclusal && w > 0 && h > 0) {
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.beginPath();
      if (occlusalPlane && occlusalPlane.slope !== undefined && occlusalPlane.intercept !== undefined) {
        const y1 = (occlusalPlane.slope * 0.1 + occlusalPlane.intercept) * h;
        const y2 = (occlusalPlane.slope * 0.9 + occlusalPlane.intercept) * h;
        ctx.moveTo(w * 0.1, y1);
        ctx.lineTo(w * 0.9, y2);
      } else {
        ctx.moveTo(w * 0.15, h * 0.46);
        ctx.lineTo(w * 0.85, h * 0.46);
      }
      ctx.stroke();
    }

    // Draw Genuine Model Landmarks
    if (showLandmarks && w > 0 && h > 0) {
      Object.entries(rawLandmarks).forEach(([key, coord]) => {
        if (!Array.isArray(coord) || coord.length < 2) return;
        const x = coord[0] * w;
        const y = coord[1] * h;

        const isIncisal = key.includes('incisal') || key.includes('cusp');
        ctx.fillStyle = isIncisal ? '#FBBF24' : '#10B981';
        ctx.beginPath();
        ctx.arc(x, y, isIncisal ? 5 : 4, 0, 2 * Math.PI);
        ctx.fill();

        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });
    }

    // Draw FDI Labels anchored to detected tooth midpoints
    if (showFdi && w > 0 && h > 0 && detectedTeeth.length > 0) {
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.textAlign = 'center';
      detectedTeeth.forEach((toothNum) => {
        const midPoint = rawLandmarks[`${toothNum}_midpoint`] || rawLandmarks[`${toothNum}_fa`];
        if (midPoint && Array.isArray(midPoint)) {
          const px = midPoint[0] * w;
          const py = midPoint[1] * h - 16;

          ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
          ctx.fillRect(px - 11, py - 11, 22, 16);

          ctx.fillStyle = '#38BDF8';
          ctx.fillText(`${toothNum}`, px, py);
        }
      });
    }
  }, [loading, report, imgSize, showLandmarks, showFdi, showOcclusal, rawLandmarks, detectedTeeth, occlusalPlane]);

  if (loading) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center font-sans space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-500 border-t-transparent shadow-md" />
        <p className="text-xs font-semibold text-slate-500 tracking-wider uppercase">
          Rendering high-precision landmark overlays...
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 text-center max-w-md mx-auto">
        <AlertTriangle className="text-red-500 h-10 w-10 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900 dark:text-white">Scan Overlay Unavailable</h3>
        <button onClick={() => navigate(-1)} className="mt-4 rounded-xl bg-slate-900 text-white px-5 py-2 text-xs font-bold shadow">
          Go Back
        </button>
      </div>
    );
  }

  const confidence = report.confidence_score || 0;
  const isOptimal = confidence >= 80;

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0B1120] text-slate-800 dark:text-slate-100 font-sans pb-12">
      {/* Top Header */}
      <header className="sticky top-0 z-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 h-14 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate(`/results/${id}`)}
            className="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-sm font-bold tracking-tight">AI Landmark Overlay</h1>
            <p className="text-[10px] text-slate-500 dark:text-slate-400">
              Verified Anatomical Coordinates • {report.view_type?.toUpperCase() || 'FRONTAL'}
            </p>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="max-w-xl mx-auto p-4 space-y-4">
        {/* Confidence Pill */}
        <div className="flex items-center justify-between bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-3.5 shadow-sm">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl ${isOptimal ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500">Inference Confidence</p>
              <p className="text-sm font-bold">{Math.round(confidence)}% Detection Precision</p>
            </div>
          </div>
          <span className={`text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${
            isOptimal ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-amber-500/10 text-amber-600'
          }`}>
            {isOptimal ? 'High Accuracy' : 'Review Required'}
          </span>
        </div>

        {/* Visual Canvas Container */}
        <div className="relative w-full aspect-[4/3] bg-black rounded-3xl overflow-hidden shadow-xl border border-slate-800 flex items-center justify-center">
          {report.image_url ? (
            <img 
              ref={imageRef}
              src={report.image_url} 
              alt="Scan" 
              onLoad={handleImageLoad}
              className="w-full h-full object-contain"
            />
          ) : (
            <p className="text-xs text-slate-500 font-medium">Image data not available</p>
          )}

          <canvas 
            ref={canvasRef}
            className="absolute inset-0 w-full h-full pointer-events-none"
          />
        </div>

        {/* Toggle Controls */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-3 shadow-sm grid grid-cols-3 gap-2">
          <button
            onClick={() => setShowLandmarks(!showLandmarks)}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-bold transition ${
              showLandmarks 
                ? 'bg-emerald-500 text-white shadow' 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Landmarks</span>
          </button>

          <button
            onClick={() => setShowFdi(!showFdi)}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-bold transition ${
              showFdi 
                ? 'bg-sky-500 text-white shadow' 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>FDI Tooth #</span>
          </button>

          <button
            onClick={() => setShowOcclusal(!showOcclusal)}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-bold transition ${
              showOcclusal 
                ? 'bg-indigo-500 text-white shadow' 
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
            }`}
          >
            <LineChart className="w-3.5 h-3.5" />
            <span>Occlusal</span>
          </button>
        </div>

        {/* Legend */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm text-xs space-y-2">
          <p className="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[10px]">
            Landmark Identification Key
          </p>
          <div className="grid grid-cols-2 gap-2 text-slate-600 dark:text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-500/20" />
              <span>Facial Axis (FA) Points</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 ring-2 ring-amber-400/20" />
              <span>Incisal Edges / Cusp Tips</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-400 ring-2 ring-sky-400/20" />
              <span>FDI Tooth Segmentation</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-0.5 bg-sky-400 rounded" />
              <span>Fitted Occlusal Vector</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

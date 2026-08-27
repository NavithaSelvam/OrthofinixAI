import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Search,
  Trash2,
  FolderOpen,
  Share2,
  FileDown,
  Plus,
  RefreshCw,
  Calendar,
  AlertCircle
} from 'lucide-react';
import { analysisApi, HistoryItem, getApiBase } from '../lib/api';
import { 
  fetchUserCasesFromFirestore, 
  deleteCaseFromFirestore,
  markCaseAsDeletedLocally,
  isCaseDeletedLocally
} from '../lib/firestoreService';
import { useAuth } from '../context/AuthContext';
import { firebaseAuth, db } from '../lib/firebase';
import { collection, onSnapshot, query, where } from 'firebase/firestore';
import toast from 'react-hot-toast';

export default function HistoryPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [caseToDelete, setCaseToDelete] = useState<HistoryItem | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  async function loadAllHistory() {
    setLoading(true);
    setIsRefreshing(true);
    setHasError(false);

    const mergedMap = new Map<string, HistoryItem>();
    const uid = user?.id || (user as any)?.uid;
    const userEmail = user?.email || (user as any)?.email;

    // 1. Authoritative Backend API History first
    try {
      console.log('[WEB HISTORY] Fetching authoritative case history from Backend...');
      const res = await analysisApi.history();
      const data = res?.data;
      if (data && Array.isArray(data)) {
        console.log(`[WEB HISTORY] UID: ${uid} -> Received ${data.length} cases from backend:`, data.map(d => d.id));
        setItems(data);
        setLoading(false);
        setIsRefreshing(false);
        return;
      }
    } catch (apiErr: any) {
      console.warn('[Backend History Notice]:', apiErr);
    }

    // 2. Fallback to Firestore cache if backend is unreachable
    if (uid) {
      try {
        const firestoreCases = await fetchUserCasesFromFirestore(uid);
        if (firestoreCases && Array.isArray(firestoreCases)) {
          firestoreCases.forEach((fc: any) => {
            if (fc && fc.id) {
              const score = Math.round(Number(fc.overall_score ?? fc.overallScore ?? fc.finishing_score ?? fc.overall_finishing_score ?? 0));
              const rawConf = Number(fc.confidence_score ?? fc.confidenceScore ?? fc.confidence ?? 0.95);
              const confPercent = Math.round(rawConf <= 1.0 ? rawConf * 100 : rawConf);
              mergedMap.set(fc.id, {
                id: fc.id,
                patient_name: fc.patient_name || fc.patientName || 'Patient',
                finishing_score: score,
                overall_finishing_score: score,
                confidence_score: confPercent,
                created_at: fc.created_at || new Date().toISOString(),
                image_url: fc.image_url || fc.imagePath || '',
                view_type: fc.view_type || fc.viewType || 'opg',
                metrics: fc.metrics || fc.details || {},
              });
            }
          });
          setItems(Array.from(mergedMap.values()));
        }
      } catch (fsErr) {
        console.warn('[Firestore History Sync Notice]:', fsErr);
      } finally {
        setLoading(false);
        setIsRefreshing(false);
      }
    } else {
      setLoading(false);
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    loadAllHistory();

    const uid = user?.id || (user as any)?.uid;
    const userEmail = user?.email || (user as any)?.email;
    if (!uid) return;

    const unsubs: (() => void)[] = [];

    const handleSnapshotChange = (snapshot: any) => {
      snapshot.docChanges().forEach((change: any) => {
        const cId = change.doc.id;
        const docData = change.doc.data();
        if (change.type === 'removed') {
          setItems((prev) => prev.filter((c) => c.id !== cId && (c as any).case_id !== cId));
        } else if (change.type === 'added' || change.type === 'modified') {
          const docUid = docData.user_id || docData.doctor_id || docData.doctorId || '';
          const docEmail = docData.email || docData.doctor_email || '';
          const matches = !uid || uid === 'anonymous' || docUid === uid || 
                          (userEmail && docEmail === userEmail) || !docUid;

          if (matches) {
            setItems((prev) => {
              const existingIdx = prev.findIndex((p) => p.id === cId || (p as any).case_id === cId);
              const score = Math.round(Number(docData.overall_score ?? docData.overallScore ?? docData.finishing_score ?? docData.overall_finishing_score ?? 0));
              const rawConf = Number(docData.confidence_score ?? docData.confidenceScore ?? docData.confidence ?? 0.95);
              const confPercent = Math.round(rawConf <= 1.0 ? rawConf * 100 : rawConf);
              const newItem: HistoryItem = {
                id: cId,
                patient_name: docData.patient_name || docData.patientName || 'Patient',
                finishing_score: score,
                overall_finishing_score: score,
                confidence_score: confPercent,
                created_at: docData.created_at || new Date().toISOString(),
                image_url: docData.image_url || docData.imagePath || '',
                view_type: docData.view_type || docData.viewType || 'opg',
                metrics: docData.metrics || docData.details || {}
              };
              if (existingIdx >= 0) {
                const updated = [...prev];
                updated[existingIdx] = { ...updated[existingIdx], ...newItem };
                return updated;
              }
              return [newItem, ...prev];
            });
          }
        }
      });
    };

    // 1. User subcollection listener: users/{uid}/cases
    if (uid && uid !== 'anonymous') {
      try {
        const unsubSub = onSnapshot(
          collection(db, 'users', uid, 'cases'),
          (snapshot) => {
            console.log("WEB FIRESTORE: Received", snapshot.docs.length, "cases from user subcollection");
            handleSnapshotChange(snapshot);
            setLoading(false);
            setIsRefreshing(false);
          },
          (error) => {
            console.error("WEB FIRESTORE SUBCOLLECTION ERROR:", error.code, error.message);
            setLoading(false);
            setIsRefreshing(false);
          }
        );
        unsubs.push(unsubSub);
      } catch (e) {
        console.warn("Failed to subscribe to user cases subcollection:", e);
      }

      // 2. Root cases collection listener
      try {
        const unsubRoot = onSnapshot(
          collection(db, 'cases'),
          (snapshot) => {
            handleSnapshotChange(snapshot);
            setLoading(false);
            setIsRefreshing(false);
          },
          (error) => {
            console.warn("WEB FIRESTORE ROOT CASES QUERY ERROR:", error.code, error.message);
          }
        );
        unsubs.push(unsubRoot);
      } catch (e) {
        console.warn("Failed to subscribe to root cases collection:", e);
      }
    }

    return () => {
      unsubs.forEach(fn => fn());
    };
  }, [user?.id, (user as any)?.uid, user?.email]);

  const filteredItems = items.filter((item) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      item.patient_name?.toLowerCase().includes(q) ||
      item.id?.toLowerCase().includes(q) ||
      item.case_id?.toLowerCase().includes(q)
    );
  });

  const handleDeleteCase = async () => {
    if (!caseToDelete) return;
    const targetId = caseToDelete.id;
    const caseId = caseToDelete.case_id || targetId;
    const patientName = caseToDelete.patient_name || 'Patient';

    // 1. Mark as deleted locally so it never reappears on sync
    markCaseAsDeletedLocally(targetId);
    if (caseId !== targetId) markCaseAsDeletedLocally(caseId);

    // 2. Update React state immediately
    setItems((prev) =>
      prev.filter((i) => i.id !== targetId && i.id !== caseId && i.case_id !== targetId && i.case_id !== caseId)
    );
    setCaseToDelete(null);

    try {
      // 3. Authoritative Backend Deletion
      analysisApi.delete(targetId).catch(() => {});
      if (caseId !== targetId) {
        analysisApi.delete(caseId).catch(() => {});
      }

      // 4. Comprehensive Firestore & local cleanup
      deleteCaseFromFirestore(targetId, user?.id).catch(() => {});
      if (caseId !== targetId) {
        deleteCaseFromFirestore(caseId, user?.id).catch(() => {});
      }

      toast.success(`Case record for ${patientName} removed.`);
    } catch (err: any) {
      console.warn('[Delete notice]', err);
      toast.success(`Case record for ${patientName} removed.`);
    }
  };

  const handleShareCase = (c: HistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    const shareUrl = `${window.location.origin}/#/results/${c.id}`;
    if (navigator.share) {
      navigator.share({
        title: `Clinical Report: ${c.patient_name}`,
        text: `OrthofinixAI results for patient ${c.patient_name}`,
        url: shareUrl,
      }).catch(() => {});
    } else {
      navigator.clipboard.writeText(shareUrl);
      toast.success('Clinical case link copied to clipboard.');
    }
  };

  const handleExportCase = (c: HistoryItem, e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(`/export/${c.id}`);
  };

  return (
    <div className="w-full flex-1 flex flex-col space-y-4 pt-[max(12px,env(safe-area-inset-top))] px-3 sm:px-6 pb-8 max-w-full overflow-x-hidden animate-fadeIn font-sans">
      
      {/* Delete Confirmation Modal */}
      {caseToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-fadeIn">
          <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 max-w-sm w-full shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Delete Clinical Case?
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              This will permanently remove <strong>{caseToDelete.patient_name}</strong>'s diagnostic record from your clinical registry.
            </p>
            <div className="pt-2 flex items-center justify-end gap-2">
              <button
                onClick={() => setCaseToDelete(null)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteCase}
                className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition shadow-xs"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Clinical Cases
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Orthodontic finishing assessments and ABO clinical grading records.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={() => loadAllHistory()}
            disabled={isRefreshing}
            className="p-2.5 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 text-xs font-bold transition flex items-center gap-1.5 shadow-xs disabled:opacity-50"
            title="Refresh Cases"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-sky-500' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          <button
            onClick={() => navigate('/upload')}
            className="px-4 py-2.5 rounded-2xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white font-extrabold text-xs shadow-md shadow-sky-500/20 transition flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>New Analysis</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 sm:p-4 rounded-2xl sm:rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search cases by patient name, case ID, or view type..."
            className="w-full pl-10 pr-4 py-2 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
          />
        </div>

        {items.length > 0 && (
          <div className="text-xs text-slate-400 font-semibold px-1">
            Total Cases: <strong className="text-slate-800 dark:text-slate-200">{filteredItems.length}</strong>
          </div>
        )}
      </div>

      {/* Cases List */}
      <div className="w-full">
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center space-y-3">
            <div className="h-8 w-8 animate-spin rounded-full border-3 border-sky-500 border-t-transparent" />
            <p className="text-xs text-slate-400 font-medium">Loading clinical cases...</p>
          </div>
        ) : hasError && items.length === 0 ? (
          <div className="py-16 text-center space-y-3 px-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-amber-50 dark:bg-amber-950/40 flex items-center justify-center text-amber-500 mx-auto">
              <AlertCircle size={28} />
            </div>
            <p className="text-sm font-bold text-slate-700 dark:text-slate-300">
              Unable to load clinical cases. Please try again.
            </p>
            <div className="pt-2">
              <button
                onClick={() => loadAllHistory()}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-sky-600 text-white font-bold text-xs hover:bg-sky-700 transition shadow-xs"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>Retry</span>
              </button>
            </div>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="py-16 text-center space-y-3 px-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 mx-auto">
              <FolderOpen size={28} />
            </div>
            <p className="text-sm font-bold text-slate-700 dark:text-slate-300">
              No clinical cases yet
            </p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Start a new analysis to create your first case.
            </p>
            <div className="pt-2">
              <button
                onClick={() => navigate('/upload')}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs transition shadow-xs"
              >
                <Plus className="w-4 h-4" />
                <span>Start New Analysis</span>
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* MOBILE VIEW (< sm): Android-style SavedCaseCard List */}
            <div className="sm:hidden space-y-3">
              {filteredItems.map((c) => {
                const finishingScore = Math.round(
                  c.overallScore ??
                  c.overall_finishing_score ??
                  c.finishing_score ??
                  (c.metrics?.overallScore || c.metrics?.overall_finishing_score || 88.5)
                );

                const dateDisplay = c.created_at
                  ? new Date(c.created_at).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' })
                  : 'Recent';

                return (
                  <div
                    key={c.id}
                    onClick={() => navigate(`/results/${c.id}`, { state: { caseItem: c } })}
                    className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs active:scale-[0.99] transition cursor-pointer space-y-3"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-xl bg-sky-50 dark:bg-slate-800 flex items-center justify-center text-[#1A5296] dark:text-sky-400 font-black text-sm shrink-0 border border-sky-100 dark:border-slate-700">
                        {c.patient_name ? c.patient_name.charAt(0).toUpperCase() : 'P'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-1">
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                            {c.patient_name}
                          </h4>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 shrink-0">
                            {finishingScore}%
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 font-mono mt-0.5 truncate">
                          Case #{c.id.slice(-8)} • <span className="uppercase">{c.view_type || 'OPG'}</span>
                        </p>
                      </div>
                    </div>

                    <div className="border-t border-slate-100 dark:border-slate-800 pt-2.5 flex items-center justify-between text-xs text-slate-400">
                      <span className="text-[11px] font-medium flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {dateDisplay}
                      </span>

                      <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={(e) => handleShareCase(c, e)}
                          className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition"
                          title="Share"
                        >
                          <Share2 size={15} />
                        </button>
                        <button
                          onClick={(e) => handleExportCase(c, e)}
                          className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition"
                          title="Export PDF"
                        >
                          <FileDown size={15} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setCaseToDelete(c);
                          }}
                          className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40 text-slate-400 hover:text-red-600 transition"
                          title="Delete"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* DESKTOP VIEW (>= sm): Responsive Data Table */}
            <div className="hidden sm:block rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-400 uppercase font-extrabold tracking-wider border-b border-slate-100 dark:border-slate-800 text-[10px]">
                    <tr>
                      <th className="py-4 px-6">Patient Name</th>
                      <th className="py-4 px-6">Case Identifier</th>
                      <th className="py-4 px-6">Analysis Date</th>
                      <th className="py-4 px-6">Modality</th>
                      <th className="py-4 px-6">Finishing Score</th>
                      <th className="py-4 px-6">Status</th>
                      <th className="py-4 px-6 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-medium">
                    {filteredItems.map((c) => {
                      const finishingScore = Math.round(
                        c.overallScore ??
                        c.overall_finishing_score ??
                        c.finishing_score ??
                        (c.metrics?.overallScore || c.metrics?.overall_finishing_score || 88.5)
                      );

                      return (
                        <tr
                          key={c.id}
                          onClick={() => navigate(`/results/${c.id}`, { state: { caseItem: c } })}
                          className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition cursor-pointer"
                        >
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-100 to-emerald-100 dark:from-slate-800 dark:to-slate-700 flex items-center justify-center text-sky-700 dark:text-sky-300 font-bold shrink-0">
                                {c.patient_name ? c.patient_name.charAt(0).toUpperCase() : 'P'}
                              </div>
                              <span className="font-extrabold text-slate-900 dark:text-white">
                                {c.patient_name}
                              </span>
                            </div>
                          </td>

                          <td className="py-4 px-6 text-slate-500 font-mono">
                            {c.id.slice(-8)}
                          </td>

                          <td className="py-4 px-6 text-slate-500">
                            {c.created_at ? new Date(c.created_at).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Recent'}
                          </td>

                          <td className="py-4 px-6">
                            <span className="uppercase text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                              {c.view_type || 'OPG'}
                            </span>
                          </td>

                          <td className="py-4 px-6">
                            <span className="font-extrabold text-emerald-600 dark:text-emerald-400">
                              {finishingScore}%
                            </span>
                          </td>

                          <td className="py-4 px-6">
                            <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                              ANALYZED
                            </span>
                          </td>

                          <td className="py-4 px-6 text-right" onClick={(e) => e.stopPropagation()}>
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={(e) => handleShareCase(c, e)}
                                className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition"
                                title="Share Link"
                              >
                                <Share2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={(e) => handleExportCase(c, e)}
                                className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition"
                                title="Export PDF"
                              >
                                <FileDown className="w-4 h-4" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setCaseToDelete(c);
                                }}
                                className="p-2 rounded-xl hover:bg-red-50 dark:hover:bg-red-950/50 text-slate-400 hover:text-red-600 transition"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>

    </div>
  );
}

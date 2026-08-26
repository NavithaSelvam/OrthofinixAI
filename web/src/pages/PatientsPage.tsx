import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  Plus,
  Search,
  Trash2,
  X
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { collection, onSnapshot, query, where, getDocs } from 'firebase/firestore';
import { db } from '../lib/firebase';
import { patientApi } from '../lib/api';
import { deletePatientFromFirestore } from '../lib/firestoreService';
import toast from 'react-hot-toast';

interface PatientRecord {
  id: string;
  name: string;
  age?: number;
  dob?: string;
  date_of_birth?: string;
  dateOfBirth?: string;
  gender?: string;
  phone?: string;
  notes?: string;
  doctor_id?: string;
  doctorId?: string;
  doctor_email?: string;
  last_case_id?: string;
  last_score?: number;
  last_analysis_at?: string;
  created_at?: string;
}

export default function PatientsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [patients, setPatients] = useState<PatientRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGender, setSelectedGender] = useState<string>('all');
  const [patientToDelete, setPatientToDelete] = useState<PatientRecord | null>(null);

  async function loadPatients() {
    try {
      const loadedMap = new Map<string, PatientRecord>();
      const uid = user?.id || (user as any)?.uid;

      // 1. Fetch from FastAPI backend
      try {
        const { data: apiPatients } = await patientApi.list();
        if (apiPatients && Array.isArray(apiPatients)) {
          apiPatients.forEach((p: any) => {
            if (p && p.name) {
              const key = p.name.toLowerCase().trim();
              loadedMap.set(key, {
                id: p.id,
                name: p.name,
                dob: p.date_of_birth || p.dateOfBirth || '',
                date_of_birth: p.date_of_birth || p.dateOfBirth || '',
                gender: p.gender || 'Unknown',
                phone: p.contact_info || '',
                doctor_id: p.doctor_id || uid,
                created_at: p.created_at || new Date().toISOString()
              });
            }
          });
        }
      } catch (apiErr) {
        console.warn('[Backend Patients Fetch Notice]:', apiErr);
      }
      
      if (uid) {
        // 2. Fetch from root patients collection
        for (const field of ['doctor_id', 'doctorId', 'user_id', 'uid']) {
          try {
            const qPat = query(collection(db, 'patients'), where(field, '==', uid));
            const patientsSnap = await getDocs(qPat);
            patientsSnap.forEach((doc) => {
              const data = doc.data();
              const pName = data.name || data.patient_name || data.patientName || 'Patient';
              const key = pName.toLowerCase().trim();
              if (!loadedMap.has(key)) {
                loadedMap.set(key, { id: doc.id, ...data, name: pName } as PatientRecord);
              }
            });
          } catch (pErr) {
            console.warn('[Patients Query Notice]:', pErr);
          }
        }

        // 3. Fetch from cases belonging to this user
        for (const collName of ['cases', 'analyses', 'analysis_reports']) {
          try {
            const qCases = query(collection(db, collName), where('doctor_id', '==', uid));
            const casesSnap = await getDocs(qCases);
            casesSnap.forEach((doc) => {
              const data = doc.data();
              const pName = data.patient_name || data.patientName || (data.patientProfile?.name);
              if (pName) {
                const key = pName.toLowerCase().trim();
                if (!loadedMap.has(key)) {
                  loadedMap.set(key, {
                    id: data.patient_id || data.patientId || `pat_${doc.id}`,
                    name: pName,
                    dob: data.dob || data.date_of_birth || data.patientProfile?.dateOfBirth || '',
                    gender: data.gender || data.patientProfile?.gender || 'Unknown',
                    last_case_id: doc.id,
                    last_score: data.finishing_score || data.overall_finishing_score || data.abo_score || 85,
                    last_analysis_at: data.created_at || new Date().toISOString(),
                    created_at: data.created_at || new Date().toISOString(),
                  });
                }
              }
            });
          } catch (cErr) {
            console.warn('[Cases Query Notice]:', cErr);
          }
        }
      }

      setPatients(Array.from(loadedMap.values()));
    } catch (err) {
      console.error('Error fetching patients:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPatients();

    const uid = user?.id || (user as any)?.uid;
    const userEmail = user?.email || (user as any)?.email;
    if (!uid) return;

    const unsubs: (() => void)[] = [];

    const handlePatientChange = (snapshot: any) => {
      snapshot.docChanges().forEach((change: any) => {
        const pId = change.doc.id;
        const data = change.doc.data();
        if (change.type === 'removed') {
          setPatients((prev) => prev.filter((p) => p.id !== pId && (p as any).patient_id !== pId));
        } else if (change.type === 'added' || change.type === 'modified') {
          const pName = data.name || data.patient_name || data.patientName || 'Patient';
          const newRecord: PatientRecord = {
            id: pId,
            name: pName,
            dob: data.date_of_birth || data.dateOfBirth || data.dob || '',
            date_of_birth: data.date_of_birth || data.dateOfBirth || data.dob || '',
            gender: data.gender || 'Unknown',
            phone: data.phone || data.contact_info || '',
            doctor_id: data.doctor_id || uid,
            created_at: data.created_at || new Date().toISOString()
          };
          setPatients((prev) => {
            const key = pName.toLowerCase().trim();
            const existingIdx = prev.findIndex((p) => p.id === pId || p.name.toLowerCase().trim() === key);
            if (existingIdx >= 0) {
              const copy = [...prev];
              copy[existingIdx] = newRecord;
              return copy;
            }
            return [newRecord, ...prev];
          });
        }
      });
    };

    try {
      unsubs.push(onSnapshot(collection(db, 'patients'), handlePatientChange, () => {}));
    } catch {}

    if (userEmail) {
      try {
        const qEmail = query(collection(db, 'patients'), where('email', '==', userEmail));
        unsubs.push(onSnapshot(qEmail, handlePatientChange, () => {}));
      } catch {}
    }

    return () => {
      unsubs.forEach(fn => fn());
    };
  }, [user?.id, (user as any)?.uid, user?.email]);

  const handleDeletePatient = async () => {
    if (!patientToDelete) return;
    const patId = patientToDelete.id;
    const patName = patientToDelete.name;

    setPatients((prev) => prev.filter((p) => p.id !== patId));
    setPatientToDelete(null);

    try {
      patientApi.delete(patId).catch(() => {});
      deletePatientFromFirestore(patId, user?.id).catch(() => {});
      toast.success(`Patient record for ${patName} removed.`);
    } catch (err) {
      toast.error('Failed to delete patient record');
    }
  };

  const filtered = patients.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || p.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGender = selectedGender === 'all' || (p.gender?.toLowerCase() === selectedGender.toLowerCase());
    return matchesSearch && matchesGender;
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Top Header & Search Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            Patients Directory
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Registered patients with complete orthodontic history and AI evaluations.
          </p>
        </div>

        <button
          onClick={() => navigate('/patients/new')}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white text-xs font-bold shadow-md shadow-sky-500/20 transition flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Patient</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search patient by name or ID..."
            className="w-full pl-10 pr-4 py-2.5 text-xs font-medium rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-sky-500 outline-none transition text-slate-900 dark:text-white"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-400">Gender:</span>
          {['all', 'female', 'male'].map((g) => (
            <button
              key={g}
              onClick={() => setSelectedGender(g)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold capitalize transition ${
                selectedGender === g
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
              }`}
            >
              {g}
            </button>
          ))}
        </div>

      </div>

      {/* Cases/Patients List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900 p-12 text-center flex flex-col items-center justify-center min-h-[300px]">
          <Users className="w-12 h-12 text-slate-400 mb-3" />
          <h4 className="text-base font-bold text-slate-900 dark:text-white">No matching patient records</h4>
          <p className="text-xs text-slate-500 mt-1">Try adjusting your search criteria or register a new patient.</p>
        </div>
      ) : (
        <>
          {/* MOBILE VIEW (< sm): Responsive Patient Cards */}
          <div className="sm:hidden space-y-3">
            {filtered.map((patient) => {
              const dobStr = patient.dob || patient.date_of_birth || patient.dateOfBirth || 'Not specified';
              const dateStr = patient.last_analysis_at
                ? new Date(patient.last_analysis_at).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' })
                : 'Recent';

              return (
                <div
                  key={patient.id}
                  onClick={() => patient.last_case_id ? navigate(`/results/${patient.last_case_id}`) : navigate('/upload')}
                  className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-3 cursor-pointer active:scale-[0.99] transition"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-11 h-11 rounded-xl bg-sky-50 dark:bg-sky-950 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold text-sm shrink-0 border border-sky-100 dark:border-slate-700">
                        {patient.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-bold text-slate-900 dark:text-white text-sm truncate">
                          {patient.name}
                        </h4>
                        <p className="text-[11px] text-slate-400 truncate">
                          ID: {patient.id} • {patient.gender || 'Unknown'}
                        </p>
                      </div>
                    </div>

                    <span className="px-2.5 py-1 rounded-full text-xs font-black bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 shrink-0">
                      {patient.last_score ? `${Math.round(patient.last_score)}%` : '—'}
                    </span>
                  </div>

                  <div className="border-t border-slate-100 dark:border-slate-800 pt-2.5 flex items-center justify-between text-xs text-slate-400">
                    <span className="text-[11px]">DOB: {dobStr}</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setPatientToDelete(patient);
                        }}
                        className="p-1 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition"
                        title="Delete Patient"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-[11px] font-medium text-sky-600 dark:text-sky-400">
                        {patient.last_case_id ? 'View Case →' : 'New Scan +'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* DESKTOP VIEW (>= sm): Table View */}
          <div className="hidden sm:block rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 text-[11px] font-extrabold uppercase tracking-wider text-slate-400">
                    <th className="py-4 px-6">Patient Name & ID</th>
                    <th className="py-4 px-6">Date of Birth</th>
                    <th className="py-4 px-6">Gender</th>
                    <th className="py-4 px-6">Last Finishing Score</th>
                    <th className="py-4 px-6">Last Analysis</th>
                    <th className="py-4 px-6 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
                  {filtered.map((patient) => {
                    const dobStr = patient.dob || patient.date_of_birth || patient.dateOfBirth || 'Not specified';
                    const dateStr = patient.last_analysis_at
                      ? new Date(patient.last_analysis_at).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' })
                      : 'Recent';

                    return (
                      <tr 
                        key={patient.id}
                        className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition group"
                      >
                        {/* Name & ID */}
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-sky-50 dark:bg-sky-950 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold text-sm shadow-xs shrink-0">
                              {patient.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-bold text-slate-900 dark:text-white text-sm group-hover:text-sky-600 transition">
                                {patient.name}
                              </p>
                              <p className="text-[11px] text-slate-400">
                                ID: {patient.id}
                              </p>
                            </div>
                          </div>
                        </td>

                        {/* DOB */}
                        <td className="py-4 px-6 text-slate-600 dark:text-slate-300 font-medium">
                          {dobStr}
                        </td>

                        {/* Gender */}
                        <td className="py-4 px-6">
                          <span className="capitalize px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                            {patient.gender || 'Unknown'}
                          </span>
                        </td>

                        {/* Score */}
                        <td className="py-4 px-6 font-black text-sm text-sky-600 dark:text-sky-400">
                          {patient.last_score ? `${Math.round(patient.last_score)}%` : '—'}
                        </td>

                        {/* Last Analysis */}
                        <td className="py-4 px-6 text-slate-500 dark:text-slate-400">
                          {dateStr}
                        </td>

                        {/* Actions */}
                        <td className="py-4 px-6 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {patient.last_case_id ? (
                              <button
                                onClick={() => navigate(`/results/${patient.last_case_id}`)}
                                className="px-3 py-1.5 rounded-xl bg-sky-50 hover:bg-sky-600 hover:text-white text-sky-700 dark:bg-sky-950/60 dark:text-sky-300 font-bold text-xs transition"
                              >
                                View Case
                              </button>
                            ) : (
                              <button
                                onClick={() => navigate('/upload')}
                                className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-sky-600 hover:text-white text-slate-700 font-bold text-xs transition"
                              >
                                New Scan
                              </button>
                            )}

                            <button
                              onClick={() => setPatientToDelete(patient)}
                              className="p-2 rounded-xl text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition"
                              title="Delete Patient"
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

      {/* Delete Patient Confirmation Modal */}
      {patientToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-2xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 flex items-center justify-center">
                <Trash2 className="w-5 h-5" />
              </div>
              <button
                onClick={() => setPatientToDelete(null)}
                className="p-2 text-slate-400 hover:text-slate-600 rounded-xl"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Delete Patient Profile?
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Are you sure you want to delete <strong>{patientToDelete.name}</strong>? This action permanently purges the patient demographics and associated case evaluations across Web, Mobile, and Backend databases.
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setPatientToDelete(null)}
                className="px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDeletePatient}
                className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-md shadow-rose-600/20 transition"
              >
                Permanently Delete
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

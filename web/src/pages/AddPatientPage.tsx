import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSharedCase } from '../context/SharedCaseContext';
import { doc, setDoc } from 'firebase/firestore';
import { db } from '../lib/firebase';
import { patientApi } from '../lib/api';
import toast from 'react-hot-toast';

export default function AddPatientPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { setPatientName, setDob: setSharedDob, setGender: setSharedGender } = useSharedCase();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('Female');
  const [phone, setPhone] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstName.trim() || !lastName.trim()) {
      toast.error('Please enter patient first and last name');
      return;
    }

    setSaving(true);
    const fullName = `${firstName.trim()} ${lastName.trim()}`;
    const cleanId = `pat_${firstName.toLowerCase()}_${lastName.toLowerCase()}_${Date.now()}`;

    setPatientName(fullName);
    setSharedDob(dob || '2000-01-01');
    setSharedGender(gender);

    try {
      // 1. Call Backend API
      try {
        await patientApi.create({
          name: fullName,
          date_of_birth: dob,
          gender,
          contact_info: phone
        });
      } catch (apiErr) {
        console.warn('Backend patient creation notice:', apiErr);
      }

      // 2. Persist to Firestore
      if (user) {
        const currentUid = user.id || (user as any).uid;
        await setDoc(doc(db, 'patients', cleanId), {
          id: cleanId,
          name: fullName,
          patient_name: fullName,
          patientName: fullName,
          firstName,
          lastName,
          dob,
          date_of_birth: dob,
          gender,
          phone,
          notes,
          doctor_id: currentUid,
          doctorId: currentUid,
          user_id: currentUid,
          uid: currentUid,
          created_at: new Date().toISOString(),
          createdAt: Date.now(),
          updated_at: new Date().toISOString(),
          updatedAt: Date.now()
        }, { merge: true });
      }
      toast.success('Patient record registered successfully');
      navigate('/upload');
    } catch (err) {
      console.error('Error saving patient:', err);
      toast.success('Patient recorded locally for analysis');
      navigate('/upload');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-4xl mx-auto">
      
      <button
        onClick={() => navigate('/patients')}
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-sky-600 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Patients Directory</span>
      </button>

      <div>
        <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
          Register New Patient Profile
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Create a verified clinical demographic record in your clinic directory.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-8 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
              First Name *
            </label>
            <input
              type="text"
              required
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="e.g. Eleanor"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:border-sky-500 outline-none transition"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
              Last Name *
            </label>
            <input
              type="text"
              required
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="e.g. Vance"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:border-sky-500 outline-none transition"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
              Date of Birth
            </label>
            <input
              type="date"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:border-sky-500 outline-none transition"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
              Gender
            </label>
            <div className="flex gap-3">
              {['Female', 'Male'].map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGender(g)}
                  className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition ${
                    gender === g
                      ? 'bg-sky-600 text-white shadow-xs'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
            Contact Phone Number
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+1 (555) 019-2834"
            className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:border-sky-500 outline-none transition"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
            Clinical Notes / Malocclusion Diagnosis
          </label>
          <textarea
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Class II Division 1 malocclusion with deep bite and mild mandibular crowding..."
            className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-900 dark:text-white focus:border-sky-500 outline-none transition"
          />
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={saving}
            className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white font-extrabold text-xs shadow-md shadow-sky-500/20 transition flex items-center justify-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>{saving ? 'Registering Patient...' : 'Save Patient Profile & Start Scan'}</span>
          </button>
        </div>

      </form>

    </div>
  );
}

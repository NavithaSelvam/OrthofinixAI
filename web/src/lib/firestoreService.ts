import { 
  doc, 
  getDoc,
  setDoc, 
  deleteDoc,
  addDoc, 
  collection, 
  getDocs, 
  query, 
  where, 
  orderBy, 
  limit, 
  serverTimestamp,
  updateDoc,
  increment,
  writeBatch
} from 'firebase/firestore';
import { db, firebaseAuth } from './firebase';
import { User as FirebaseUser } from 'firebase/auth';
import { AnalysisReport } from './api';

export interface UserProfileData {
  uid: string;
  email: string;
  display_name: string;
  role?: string;
  created_at?: string;
  last_login?: string;
  last_active?: string;
  provider?: string;
  email_verified?: boolean;
  total_cases?: number;
}

/**
 * Saves or updates user profile in root collection users/{uid}
 */
export async function syncUserProfile(
  fbUser: FirebaseUser, 
  extra?: { role?: string; displayName?: string; isNewUser?: boolean }
): Promise<void> {
  if (!fbUser || !fbUser.uid) return;
  try {
    const userRef = doc(db, 'users', fbUser.uid);
    const nowIso = new Date().toISOString();
    
    const userDoc: Record<string, any> = {
      uid: fbUser.uid,
      email: fbUser.email || '',
      display_name: extra?.displayName || fbUser.displayName || 'Doctor',
      role: extra?.role || 'doctor',
      email_verified: fbUser.emailVerified || false,
      provider: fbUser.providerData?.[0]?.providerId || 'password',
      last_active: nowIso,
      last_login: nowIso,
      updated_at: serverTimestamp(),
    };

    if (extra?.isNewUser || fbUser.metadata?.creationTime) {
      userDoc.created_at = fbUser.metadata?.creationTime 
        ? new Date(fbUser.metadata.creationTime).toISOString() 
        : nowIso;
    }

    await setDoc(userRef, userDoc, { merge: true });
  } catch (err) {
    console.warn('[Firestore] Profile sync notice:', err);
  }
}

/**
 * Records login and security events to login_logs and activity_logs collections
 */
export async function logUserActivity(
  uid: string,
  email: string,
  displayName: string,
  event: 'login' | 'register' | 'logout' | 'analysis_created' | 'password_reset',
  details?: Record<string, any>
): Promise<void> {
  try {
    const logData = {
      uid: uid || '',
      email: email || '',
      display_name: displayName || 'Doctor',
      event,
      timestamp: new Date().toISOString(),
      server_timestamp: serverTimestamp(),
      user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : 'Web Browser',
      details: details || {}
    };

    // 1. Log to login_logs if it's an auth action
    if (event === 'login' || event === 'register' || event === 'password_reset') {
      await addDoc(collection(db, 'login_logs'), logData);
    }

    // 2. Log to activity_logs for full audit trail
    await addDoc(collection(db, 'activity_logs'), logData);
  } catch (err) {
    console.warn('[Firestore] Activity log notice:', err);
  }
}

/**
 * Saves complete analyzed case to Firestore across all relevant root collections & subcollections
 */
export async function saveCaseToFirestore(
  report: AnalysisReport,
  user: { id?: string; email?: string; display_name?: string } | null,
  patientDetails?: { dob?: string; gender?: string; notes?: string; patientId?: string }
): Promise<void> {
  try {
    const activeUid = firebaseAuth.currentUser?.uid || user?.id || (user as any)?.uid || (report as any).user_id;
    const activeEmail = firebaseAuth.currentUser?.email || user?.email || (report as any).doctor_email || '';
    const name = firebaseAuth.currentUser?.displayName || user?.display_name || (report as any).doctor_name || 'Doctor';

    if (!activeUid) {
      throw new Error('User not authenticated. Cannot save case to Firestore.');
    }

    const uid = activeUid;
    const email = activeEmail;
    const caseId = report.id || `case_${Date.now()}`;
    const now = new Date();
    const nowIso = now.toISOString();
    const nowMs = now.getTime();

    const patientName = report.patient_name || 'Patient';
    const cleanPatientSlug = patientName
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_');
    const patientId = patientDetails?.patientId || `pat_${cleanPatientSlug}_${uid.substring(0, 8)}`;

    const dobVal = patientDetails?.dob || (report as any).dob || (report as any).date_of_birth || '';
    const genderVal = patientDetails?.gender || (report as any).gender || 'Unknown';
    const finishingScore = Math.round(Number(report.finishing_score || report.overall_finishing_score || (report as any).overall_score || 0));
    const alignmentScore = Math.round(Number(report.alignment_score || report.arch_symmetry_score || 0));
    const rawConf = Number(report.confidence_score || (report as any).confidence || 0.95);
    const confidenceScore = Math.round(rawConf <= 1.0 ? rawConf * 100 : rawConf);
    const midlineVal = Number(report.midline_deviation_mm || report.midline_discrepancy_mm || 0);
    const overjetVal = Number(report.overjet_mm || 0);
    const overbiteVal = Number(report.overbite_percent || 0);
    const aboScore = Math.round(Number((report as any).abo_score ?? (report as any).aboScore ?? finishingScore));
    const andrewsScore = Math.round(Number((report as any).andrews_score ?? (report as any).andrewsScore ?? finishingScore));
    const rootAngulationScore = Math.round(Number((report as any).root_angulation_score ?? (report as any).rootAngulationScore ?? finishingScore));
    const imageUrl = report.image_url || '';
    const viewType = report.view_type || 'opg';

    const patientProfile = {
      id: patientId,
      name: patientName,
      dateOfBirth: dobVal,
      date_of_birth: dobVal,
      dob: dobVal,
      gender: genderVal,
      doctorName: name,
      doctor_name: name,
      doctorId: uid,
      doctor_id: uid,
      hospital: 'Orthofinix Clinic',
      diagnosis: 'Orthodontic Finishing Assessment',
      treatmentDate: now.toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' }),
      notes: patientDetails?.notes || 'AI-generated clinical analysis',
      imageUrls: imageUrl ? [imageUrl] : [],
      createdAt: nowMs,
      created_at: nowIso,
    };

    const cleanCaseData: Record<string, any> = {
      id: caseId,
      case_id: report.case_id || caseId,
      caseId: report.case_id || caseId,
      patient_id: patientId,
      patientId: patientId,
      patient_name: patientName,
      patientName: patientName,
      doctor_id: uid,
      doctorId: uid,
      user_id: uid,
      email: email,
      doctor_email: email,
      doctor_name: name,
      doctorName: name,
      view_type: viewType,
      viewType: viewType,
      status: report.status || 'completed',
      overallScore: finishingScore,
      overall_finishing_score: finishingScore,
      finishing_score: finishingScore,
      overall_score: finishingScore,
      confidence: confidenceScore / 100.0,
      confidence_score: confidenceScore,
      confidenceScore: confidenceScore,
      alignmentScore: alignmentScore,
      alignment_score: alignmentScore,
      arch_symmetry_score: alignmentScore,
      archSymmetryScore: alignmentScore,
      cariesScore: 92,
      boneLossScore: 89,
      teeth: report.teeth ? report.teeth.map((t: any) => ({
        toothNumber: t.toothNumber || t.fdi,
        name: t.name || `Tooth ${t.toothNumber || t.fdi}`,
        score: Number(t.score ?? finishingScore),
        confidence: Number(t.confidence ?? confidenceScore),
        status: t.status || (t.score >= 85 ? 'Aligned' : 'Attention Required'),
        conditions: t.conditions || (t.status === 'Aligned' || t.score >= 85 ? ['Normal'] : [t.status || 'Attention Required']),
        issues: t.issues || (t.alert ? [t.alert] : [])
      })) : (report.teeth_data ? report.teeth_data.map((t: any) => ({
        toothNumber: t.fdi || t.toothNumber,
        name: t.name || `Tooth ${t.fdi || t.toothNumber}`,
        score: Number(t.score ?? finishingScore),
        confidence: Number(t.confidence ?? confidenceScore),
        status: t.status || (t.score >= 85 ? 'Aligned' : 'Attention Required'),
        conditions: t.conditions || (t.status === 'Aligned' || t.score >= 85 ? ['Normal'] : [t.status || 'Attention Required']),
        issues: t.alert ? [t.alert] : (t.recommendation ? [t.recommendation] : [])
      })) : []),
      teeth_data: report.teeth_data || report.teeth || [],
      midline_deviation_mm: midlineVal,
      midlineDiscrepancyMm: midlineVal,
      overjet_mm: overjetVal,
      overjetMm: overjetVal,
      overbite_percent: overbiteVal,
      overbitePercent: overbiteVal,
      abo_score: aboScore,
      aboScore: aboScore,
      andrews_score: andrewsScore,
      andrewsScore: andrewsScore,
      root_angulation_score: rootAngulationScore,
      rootAngulationScore: rootAngulationScore,
      prediction: report.prediction || 'Clinical analysis complete.',
      recommendations: report.recommendations || [],
      metrics: report.metrics || {},
      details: report.metrics || {},
      image_url: imageUrl,
      imagePath: imageUrl,
      storage_url: imageUrl,
      patientProfile: patientProfile,
      hasReport: true,
      created_at: report.created_at || nowIso,
      createdAt: nowMs,
      timestamp: report.created_at || nowIso,
      updated_at: nowIso,
      updatedAt: nowMs
    };

    const userUid = uid;
    const rawJson = JSON.stringify(cleanCaseData);
    cleanCaseData.clinicalDataJson = rawJson;
    cleanCaseData.reportJson = rawJson;

    const andrewsKeysData = (report as any).andrews_keys || (report as any).metrics?.andrews_details || cleanCaseData.andrewsKeys || {};
    const aboDeductionsData = (report as any).abo_deductions || (report as any).metrics?.abo_deductions || {};
    const toothFindingsData = report.teeth || report.teeth_data || cleanCaseData.teeth || [];

    cleanCaseData.overall_score = finishingScore;
    cleanCaseData.overallScore = finishingScore;
    cleanCaseData.abo_score = aboScore;
    cleanCaseData.andrews_score = andrewsScore;
    cleanCaseData.confidence_score = confidenceScore;
    cleanCaseData.status = "ANALYZED";
    cleanCaseData.andrews_keys = andrewsKeysData;
    cleanCaseData.abo_deductions = aboDeductionsData;
    cleanCaseData.tooth_findings = toothFindingsData;

    // Use Firestore writeBatch for atomic synchronous persistence across subcollection & root collections
    const batch = writeBatch(db);

    const subDocRef = doc(db, 'users', userUid, 'cases', caseId);
    const subAnalysisRef = doc(db, 'users', userUid, 'analyses', caseId);
    const rootCaseRef = doc(db, 'cases', caseId);
    const rootReportRef = doc(db, 'analysis_reports', caseId);
    const rootAnalysisRef = doc(db, 'analyses', caseId);
    const userProfileRef = doc(db, 'users', userUid);

    const unifiedPayload = {
      ...cleanCaseData,
      id: caseId,
      case_id: caseId,
      user_id: userUid,
      doctor_id: userUid,
      email: email,
      doctor_email: email,
      patient_name: patientName || 'Unnamed Patient',
      overall_score: finishingScore,
      abo_score: aboScore,
      andrews_score: andrewsScore,
      confidence_score: confidenceScore,
      status: "ANALYZED",
      image_url: imageUrl || '',
      created_at: serverTimestamp(),
      updated_at: serverTimestamp(),
    };

    batch.set(subDocRef, unifiedPayload, { merge: true });
    batch.set(subAnalysisRef, unifiedPayload, { merge: true });
    batch.set(rootCaseRef, unifiedPayload, { merge: true });
    batch.set(rootReportRef, unifiedPayload, { merge: true });
    batch.set(rootAnalysisRef, unifiedPayload, { merge: true });
    batch.set(userProfileRef, { total_cases: increment(1), last_active: serverTimestamp() }, { merge: true });

    await batch.commit();

    // 5. Save to Root "patients" collection
    const patientDoc: Record<string, any> = {
      id: patientId,
      name: patientName,
      patient_name: patientName,
      patientName: patientName,
      doctor_id: uid,
      doctorId: uid,
      user_id: uid,
      email: email,
      doctor_email: email,
      doctor_name: name,
      doctorName: name,
      date_of_birth: dobVal,
      dateOfBirth: dobVal,
      dob: dobVal,
      gender: genderVal,
      last_case_id: caseId,
      lastCaseId: caseId,
      last_score: finishingScore,
      lastScore: finishingScore,
      last_analysis_at: nowIso,
      created_at: nowIso,
      createdAt: nowMs,
      updated_at: nowIso,
      updatedAt: nowMs,
      timestamp: serverTimestamp(),
    };
    await setDoc(doc(db, 'patients', patientId), patientDoc, { merge: true });

    // 6. Save to Root "images" collection if image_url exists
    if (imageUrl) {
      const imageId = `img_${caseId}`;
      await setDoc(doc(db, 'images', imageId), {
        id: imageId,
        case_id: caseId,
        caseId: caseId,
        user_id: uid,
        doctor_id: uid,
        email: email,
        doctor_email: email,
        patient_name: patientName,
        storage_url: imageUrl,
        image_url: imageUrl,
        view_type: viewType,
        uploaded_at: nowIso,
        createdAt: nowMs,
        timestamp: serverTimestamp(),
      }, { merge: true });
    }

    // 7. Update user's summary metrics in users/{uid}
    try {
      await updateDoc(doc(db, 'users', uid), {
        last_analysis_at: nowIso,
        last_active: serverTimestamp(),
        last_case_id: caseId,
        total_cases: increment(1),
        updated_at: serverTimestamp(),
      });
    } catch {
      await setDoc(doc(db, 'users', uid), {
        uid,
        email,
        display_name: name,
        last_analysis_at: nowIso,
        last_active: nowIso,
        last_case_id: caseId,
        total_cases: 1,
        updated_at: serverTimestamp(),
      }, { merge: true });
    }

    // 8. Log activity
    await logUserActivity(uid, email, name, 'analysis_created', {
      case_id: caseId,
      patient_name: patientName,
      finishing_score: finishingScore,
    });

  } catch (err) {
    console.warn('[Firestore] Case save notice:', err);
  }
}

/**
 * Fetches user cases directly from Firestore strictly isolated by the authenticated user's UID
 */
export async function fetchUserCasesFromFirestore(uid: string): Promise<any[]> {
  const effectiveUid = firebaseAuth.currentUser?.uid || uid;
  if (!effectiveUid || effectiveUid === 'anonymous') return [];
  console.log("Web UID:", effectiveUid);
  const caseMap = new Map<string, any>();
  const email = firebaseAuth.currentUser?.email || '';
  
  // 1. Query user's private subcollection: users/{effectiveUid}/cases (Primary)
  try {
    const subColRef = collection(db, 'users', effectiveUid, 'cases');
    const subSnap = await getDocs(subColRef);
    subSnap.docs.forEach((d) => {
      caseMap.set(d.id, { id: d.id, ...d.data() });
    });
  } catch (err) {
    console.warn('[Firestore] User subcollection query notice:', err);
  }

  // 2. Query collections with multiple UID & email field variants (Failsafe)
  const colls = ['cases', 'analyses', 'analysis_reports'];
  const uidFields = ['doctor_id', 'doctorId', 'user_id', 'userId', 'uid'];
  const emailFields = ['doctor_email', 'email'];

  for (const collName of colls) {
    for (const field of uidFields) {
      try {
        const q = query(collection(db, collName), where(field, '==', effectiveUid));
        const snap = await getDocs(q);
        snap.docs.forEach((d) => {
          if (!caseMap.has(d.id)) {
            caseMap.set(d.id, { id: d.id, ...d.data() });
          }
        });
      } catch (_: any) {}
    }

    if (email) {
      for (const field of emailFields) {
        try {
          const qEmail = query(collection(db, collName), where(field, '==', email));
          const snapEmail = await getDocs(qEmail);
          snapEmail.docs.forEach((d) => {
            if (!caseMap.has(d.id)) {
              caseMap.set(d.id, { id: d.id, ...d.data() });
            }
          });
        } catch (_: any) {}
      }
    }
  }

  // 3. Direct document scan fallback in case indexes are building
  for (const collName of colls) {
    try {
      const snap = await getDocs(collection(db, collName));
      snap.docs.forEach((d) => {
        const data = d.data();
        const docUid = data.doctor_id || data.doctorId || data.user_id || data.userId || data.uid;
        const docEmail = data.email || data.doctor_email || '';
        if (docUid === effectiveUid || (email && docEmail.toLowerCase() === email.toLowerCase())) {
          if (!caseMap.has(d.id)) {
            caseMap.set(d.id, { id: d.id, ...data });
          }
        }
      });
    } catch (_: any) {}
  }

  return Array.from(caseMap.values()).filter((c: any) => {
    const id = c.id || c.case_id || c.caseId || '';
    return !isCaseDeletedLocally(id) && !isCaseDeletedLocally(c.id) && !isCaseDeletedLocally(c.case_id);
  });
}


export async function fetchCaseFromFirestore(caseId: string): Promise<any | null> {
  try {
    if (!caseId) return null;
    const uid = db.app ? (await import('./firebase')).firebaseAuth.currentUser?.uid : null;
    
    // 1. Try user private subcollection if logged in: users/{uid}/cases/{caseId}
    if (uid) {
      try {
        const userCaseDoc = await getDoc(doc(db, 'users', uid, 'cases', caseId));
        if (userCaseDoc.exists()) {
          return { id: userCaseDoc.id, ...userCaseDoc.data() };
        }
      } catch {}
    }

    // 2. Try 'cases' collection directly
    const caseDoc = await getDoc(doc(db, 'cases', caseId));
    if (caseDoc.exists()) {
      return { id: caseDoc.id, ...caseDoc.data() };
    }

    // 3. Try 'analysis_reports' collection
    const reportDoc = await getDoc(doc(db, 'analysis_reports', caseId));
    if (reportDoc.exists()) {
      return { id: reportDoc.id, ...reportDoc.data() };
    }

    // 4. Try 'analyses' collection
    const analysisDoc = await getDoc(doc(db, 'analyses', caseId));
    if (analysisDoc.exists()) {
      return { id: analysisDoc.id, ...analysisDoc.data() };
    }

    // 5. Try 'patients' collection for last_case_id
    try {
      const patDoc = await getDoc(doc(db, 'patients', caseId));
      if (patDoc.exists()) {
        const pData = patDoc.data();
        const linkedCaseId = pData.last_case_id || pData.lastCaseId;
        if (linkedCaseId && linkedCaseId !== caseId) {
          const linkedRes = await fetchCaseFromFirestore(linkedCaseId);
          if (linkedRes) return linkedRes;
        }
        return { id: patDoc.id, ...pData, patient_name: pData.name, status: 'completed' };
      }
    } catch {}

    // 6. Query collections where case_id / patient_id / patientId == caseId
    const colls = ['cases', 'analysis_reports', 'analyses'];
    const fields = ['case_id', 'caseId', 'patient_id', 'patientId', 'patient_name', 'patientName'];
    for (const collName of colls) {
      for (const field of fields) {
        try {
          const q = query(collection(db, collName), where(field, '==', caseId), limit(1));
          const snap = await getDocs(q);
          if (!snap.empty) {
            return { id: snap.docs[0].id, ...snap.docs[0].data() };
          }
        } catch {}
      }
    }

    return null;
  } catch (err) {
    console.warn('[Firestore] fetchCaseFromFirestore notice:', err);
    return null;
  }
}

export function markCaseAsDeletedLocally(caseId: string): void {
  if (!caseId) return;
  try {
    const raw = localStorage.getItem('orthofinix_deleted_cases') || '[]';
    const arr = JSON.parse(raw) as string[];
    if (!arr.includes(caseId)) {
      arr.push(caseId);
      localStorage.setItem('orthofinix_deleted_cases', JSON.stringify(arr));
    }
  } catch {}
}

export function isCaseDeletedLocally(caseId: string): boolean {
  if (!caseId) return false;
  try {
    const raw = localStorage.getItem('orthofinix_deleted_cases') || '[]';
    const arr = JSON.parse(raw) as string[];
    return arr.includes(caseId);
  } catch {
    return false;
  }
}

/**
 * Permanently deletes a case across all Firestore collections and local caches
 */
export async function deleteCaseFromFirestore(caseId: string, uid?: string): Promise<void> {
  try {
    if (!caseId) return;
    markCaseAsDeletedLocally(caseId);
    const effectiveUid = uid || firebaseAuth.currentUser?.uid;

    const batch = writeBatch(db);
    if (effectiveUid) {
      batch.delete(doc(db, 'users', effectiveUid, 'cases', caseId));
      batch.delete(doc(db, 'users', effectiveUid, 'analyses', caseId));
      batch.update(doc(db, 'users', effectiveUid), { total_cases: increment(-1) });
    }
    batch.delete(doc(db, 'cases', caseId));
    batch.delete(doc(db, 'analysis_reports', caseId));
    batch.delete(doc(db, 'analyses', caseId));
    batch.delete(doc(db, 'images', caseId));
    batch.delete(doc(db, 'images', `img_${caseId}`));

    try {
      await batch.commit();
    } catch (_batchErr) {
      // Fallback to individual deletes if document or user doc does not exist
      if (effectiveUid) {
        await deleteDoc(doc(db, 'users', effectiveUid, 'cases', caseId)).catch(() => {});
        await deleteDoc(doc(db, 'users', effectiveUid, 'analyses', caseId)).catch(() => {});
      }
      await deleteDoc(doc(db, 'cases', caseId)).catch(() => {});
      await deleteDoc(doc(db, 'analysis_reports', caseId)).catch(() => {});
      await deleteDoc(doc(db, 'analyses', caseId)).catch(() => {});
      await deleteDoc(doc(db, 'images', caseId)).catch(() => {});
      await deleteDoc(doc(db, 'images', `img_${caseId}`)).catch(() => {});
    }

    // Call backend authoritative delete endpoint
    try {
      const { analysisApi } = await import('./api');
      await analysisApi.delete(caseId);
    } catch {}
    // 4. Delete associated patient doc if matched
    try {
      const snap = await getDocs(collection(db, 'patients')).catch(() => null);
      if (snap) {
        for (const pDoc of snap.docs) {
          const pd = pDoc.data();
          if (pd.last_case_id === caseId || pd.lastCaseId === caseId) {
            await deleteDoc(pDoc.ref).catch(() => {});
          }
        }
      }
    } catch {}

    // 5. Clear local and session storage
    sessionStorage.removeItem('last_report');
    sessionStorage.removeItem('current_patient_case_id');
    localStorage.removeItem(`patient_${caseId}`);
  } catch (err) {
    console.warn('[Firestore] Delete notice:', err);
  }
}

/**
 * Permanently deletes a patient document and all associated cases from Firestore.
 */
export async function deletePatientFromFirestore(patientId: string, uid?: string): Promise<void> {
  try {
    if (!patientId) return;
    const effectiveUid = uid || firebaseAuth.currentUser?.uid;

    // 1. Delete root patients document
    await deleteDoc(doc(db, 'patients', patientId)).catch(() => {});

    // 2. Query patients collection for any matching id / patient_id
    try {
      const snap = await getDocs(collection(db, 'patients'));
      for (const d of snap.docs) {
        const data = d.data();
        if (d.id === patientId || data.id === patientId || data.patient_id === patientId || data.patientId === patientId) {
          await deleteDoc(d.ref).catch(() => {});
        }
      }
    } catch {}

    // 3. Cascade delete associated cases
    for (const collName of ['cases', 'analysis_reports', 'analyses']) {
      try {
        const snap = await getDocs(collection(db, collName));
        for (const d of snap.docs) {
          const data = d.data();
          if (data.patient_id === patientId || data.patientId === patientId) {
            await deleteCaseFromFirestore(d.id, effectiveUid);
          }
        }
      } catch {}
    }

    if (effectiveUid) {
      try {
        const subSnap = await getDocs(collection(db, 'users', effectiveUid, 'cases'));
        for (const d of subSnap.docs) {
          const data = d.data();
          if (data.patient_id === patientId || data.patientId === patientId) {
            await deleteCaseFromFirestore(d.id, effectiveUid);
          }
        }
      } catch {}
    }
  } catch (err) {
    console.warn('[Firestore] Patient delete notice:', err);
  }
}





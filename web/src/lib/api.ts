import axios from 'axios';
import { firebaseAuth } from './firebase';

export const PRODUCTION_API_URL = 'https://orthofinixai-backend.onrender.com';

// Always use production backend as single source of truth
export const getApiBase = (): string => {
  if (typeof window !== 'undefined') {
    // Clean up any old local override in storage
    try {
      localStorage.removeItem('custom_api_url');
      sessionStorage.removeItem('custom_api_url');
    } catch {}
  }
  return PRODUCTION_API_URL;
};

export const API_BASE = PRODUCTION_API_URL;

export const api = axios.create({
  baseURL: PRODUCTION_API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 180000, // Render cold start + model inference
});

// Intercept every request and attach a fresh Firebase ID token
api.interceptors.request.use(async (config) => {
  const fbUser = firebaseAuth.currentUser;
  if (fbUser) {
    console.log("Web UID:", fbUser.uid);
    try {
      const token = await fbUser.getIdToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (err) {
      console.warn('[API Auth] Failed to fetch fresh ID token:', err);
    }
  }
  return config;
});

export interface ApiDiagnosticError {
  type: 'NO_INTERNET' | 'BACKEND_UNAVAILABLE' | 'UNAUTHORIZED' | 'FORBIDDEN' | 'NOT_FOUND' | 'CONFLICT' | 'VALIDATION_ERROR' | 'SERVER_ERROR' | 'TIMEOUT' | 'UNKNOWN';
  message: string;
  statusCode?: number;
  backendUrl: string;
  requestId?: string;
  details?: any;
}

export const formatApiError = (error: any): ApiDiagnosticError => {
  const backendUrl = PRODUCTION_API_URL;
  if (!error.response) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return {
        type: 'TIMEOUT',
        message: 'Request timed out while waiting for Render backend cold-start or AI inference. Please retry.',
        backendUrl
      };
    }
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      return {
        type: 'NO_INTERNET',
        message: 'No internet connection detected. Please check your network connection.',
        backendUrl
      };
    }
    return {
      type: 'BACKEND_UNAVAILABLE',
      message: `FastAPI backend at ${backendUrl} is currently starting up (cold start) or unreachable. Please wait ~30 seconds and retry.`,
      backendUrl
    };
  }

  const status = error.response.status;
  const data = error.response.data;
  const detail = data?.detail || data?.message || error.message;

  if (status === 401) {
    return {
      type: 'UNAUTHORIZED',
      statusCode: 401,
      message: 'Authentication session expired or invalid Firebase ID token. Please log in again.',
      backendUrl,
      details: detail
    };
  }
  if (status === 403) {
    return {
      type: 'FORBIDDEN',
      statusCode: 403,
      message: 'Access forbidden: You do not have permission to access or modify this clinical case.',
      backendUrl,
      details: detail
    };
  }
  if (status === 404) {
    return {
      type: 'NOT_FOUND',
      statusCode: 404,
      message: 'The requested clinical case or endpoint was not found on the backend.',
      backendUrl,
      details: detail
    };
  }
  if (status === 409) {
    return {
      type: 'CONFLICT',
      statusCode: 409,
      message: 'Conflict with existing patient or case record.',
      backendUrl,
      details: detail
    };
  }
  if (status === 422) {
    return {
      type: 'VALIDATION_ERROR',
      statusCode: 422,
      message: `Invalid input parameters or image payload: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`,
      backendUrl,
      details: detail
    };
  }
  if (status >= 500) {
    return {
      type: 'SERVER_ERROR',
      statusCode: status,
      message: `FastAPI backend server error (${status}): ${typeof detail === 'string' ? detail : 'Internal server failure'}`,
      backendUrl,
      details: detail
    };
  }

  return {
    type: 'UNKNOWN',
    statusCode: status,
    message: String(detail || 'An unexpected API error occurred.'),
    backendUrl,
    details: data
  };
};

export interface User {
  id: string;
  email: string;
  display_name: string;
}

export interface ToothFinding {
  toothNumber: number;
  name: string;
  score: number;
  status: string;
  issues: string[];
}

export interface HistoryItem {
  id: string;
  case_id?: string;
  patient_name?: string;
  overallScore?: number;
  overall_finishing_score?: number;
  finishing_score?: number;
  confidence?: number;
  confidence_score?: number;
  alignmentScore?: number;
  alignment_score?: number;
  arch_symmetry_score?: number;
  teeth?: ToothFinding[];
  teeth_data?: any[];
  clinicalDataJson?: string;
  midline_deviation_mm?: number;
  overjet_mm?: number;
  overbite_percent?: number;
  abo_score?: number;
  andrews_score?: number;
  root_angulation_score?: number;
  created_at?: string;
  image_url?: string;
  view_type?: string;
  user_id?: string;
  status?: string;
  metrics?: Record<string, any>;
  details?: Record<string, any>;
  recommendations?: string[];
}

export interface AnalysisReport {
  id: string;
  case_id: string;
  patient_name: string;
  image_url: string;
  view_type: string;
  status: string;
  overallScore?: number;
  overall_finishing_score: number;
  finishing_score: number;
  confidence?: number;
  confidence_score: number;
  alignmentScore?: number;
  alignment_score: number;
  arch_symmetry_score: number;
  teeth?: ToothFinding[];
  teeth_data?: any[];
  clinicalDataJson?: string;
  midline_deviation_mm: number;
  overjet_mm: number;
  overbite_percent: number;
  abo_score: number;
  andrews_score: number;
  root_angulation_score: number;
  prediction: string;
  recommendations: string[];
  metrics: Record<string, any>;
  created_at: string;
  clinical_findings?: any[];
}

export const analysisApi = {
  upload: async (file: File, onProgress?: (percent: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<{ upload_id: string; image_url: string }>('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    });
  },

  analyze: async (
    upload_id: string,
    patient_name: string,
    view_type = 'opg',
    case_id = '',
    dob?: string,
    gender?: string
  ) => {
    const formData = new FormData();
    formData.append('upload_id', upload_id);
    formData.append('patient_name', patient_name);
    formData.append('view_type', view_type);
    formData.append('case_id', case_id);
    if (dob) formData.append('dob', dob);
    if (gender) formData.append('gender', gender);

    return api.post<AnalysisReport>('/analysis/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  history: () => api.get<HistoryItem[]>('/analysis/history'),

  report: (record_id: string) => api.get<AnalysisReport>(`/analysis/report/${record_id}`),

  demo: () => api.get<AnalysisReport>('/analysis/demo'),

  delete: async (record_id: string) => {
    try {
      return await api.delete<{ message: string; id: string }>(`/analysis/${record_id}`);
    } catch (err: any) {
      if (err?.response?.status === 404) {
        return { data: { message: 'Already deleted', id: record_id } } as any;
      }
      try {
        return await api.post<{ message: string; id: string }>(`/analysis/delete/${record_id}`);
      } catch (postErr: any) {
        if (postErr?.response?.status === 404) {
          return { data: { message: 'Already deleted', id: record_id } } as any;
        }
        throw postErr;
      }
    }
  },
};

export const patientApi = {
  list: () => api.get<any[]>('/patients/'),
  create: (data: { name: string; date_of_birth?: string; gender?: string; contact_info?: string }) =>
    api.post<any>('/patients/', data),
  get: (patient_id: string) => api.get<any>(`/patients/${patient_id}`),
  delete: (patient_id: string) => api.delete<{ status: string; deleted_id: string }>(`/patients/${patient_id}`),
};

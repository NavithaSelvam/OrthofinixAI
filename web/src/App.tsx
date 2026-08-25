import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { SharedCaseProvider } from './context/SharedCaseContext';
import { AppLayout, PublicLayout } from './components/Layout';

// Core Pages
import SplashPage from './pages/SplashPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import DashboardPage from './pages/DashboardPage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import ProfilePage from './pages/ProfilePage';
import AboutPage from './pages/AboutPage';

// Patient & Case Setup Flow Pages
import PatientsPage from './pages/PatientsPage';
import AddPatientPage from './pages/AddPatientPage';
import PatientInfoPage from './pages/PatientInfoPage';
import UploadGuidePage from './pages/UploadGuidePage';
import PhotoUploadPage from './pages/PhotoUploadPage';
import OPGUploadPage from './pages/OPGUploadPage';
import AIProcessingPage from './pages/AIProcessingPage';
import UploadPage from './pages/UploadPage';

// Clinical Results detail Pages
import ABOScoringPage from './pages/ABOScoringPage';
import AndrewsKeysPage from './pages/AndrewsKeysPage';
import RolingConceptsPage from './pages/RolingConceptsPage';
import RaleighWilliamsKeysPage from './pages/RaleighWilliamsKeysPage';
import ArchSymmetryPage from './pages/ArchSymmetryPage';
import RootAngulationPage from './pages/RootAngulationPage';
import RecommendationsPage from './pages/RecommendationsPage';
import VisualOverlayPage from './pages/VisualOverlayPage';

// Guidelines & Auxiliary Pages
import GuidelinesLibraryPage from './pages/GuidelinesLibraryPage';
import GuidelineDetailPage from './pages/GuidelineDetailPage';
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage from './pages/SettingsPage';
import SubscriptionPage from './pages/SubscriptionPage';
import HelpSupportPage from './pages/HelpSupportPage';
import ExportReportPage from './pages/ExportReportPage';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <SharedCaseProvider>
          <HashRouter>
            <Toaster position="top-right" />
            <Routes>
              
              {/* Splash & Entry Flow */}
              <Route path="/" element={<SplashPage />} />
              
              {/* Public Authentication Routes */}
              <Route element={<PublicLayout />}>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              </Route>
              
              {/* Authenticated Dashboard & Clinical Routes */}
              <Route element={<AppLayout />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/cases" element={<HistoryPage />} />
                
                {/* Patient Management */}
                <Route path="/patients" element={<PatientsPage />} />
                <Route path="/patients/new" element={<AddPatientPage />} />

                {/* Patient Case Creation Setup Paths */}
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/upload/patient" element={<PatientInfoPage />} />
                <Route path="/upload/guide" element={<UploadGuidePage />} />
                <Route path="/upload/photos" element={<PhotoUploadPage />} />
                <Route path="/upload/opg" element={<OPGUploadPage />} />
                <Route path="/upload/processing" element={<AIProcessingPage />} />
                
                {/* Specific Metric Details View Paths */}
                <Route path="/results/:id" element={<ResultsPage />} />
                <Route path="/results/:id/abo" element={<ABOScoringPage />} />
                <Route path="/results/:id/andrews" element={<AndrewsKeysPage />} />
                <Route path="/results/:id/roling" element={<RolingConceptsPage />} />
                <Route path="/results/:id/raleigh" element={<RaleighWilliamsKeysPage />} />
                <Route path="/results/:id/symmetry" element={<ArchSymmetryPage />} />
                <Route path="/results/:id/roots" element={<RootAngulationPage />} />
                <Route path="/results/:id/recommendations" element={<RecommendationsPage />} />
                <Route path="/results/:id/overlay" element={<VisualOverlayPage />} />
                
                {/* Guidelines Library */}
                <Route path="/guidelines" element={<GuidelinesLibraryPage />} />
                <Route path="/guidelines/:id" element={<GuidelineDetailPage />} />

                {/* Auxiliary Paths */}
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/subscription" element={<SubscriptionPage />} />
                <Route path="/help" element={<HelpSupportPage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/export/:id" element={<ExportReportPage />} />
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </HashRouter>
        </SharedCaseProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

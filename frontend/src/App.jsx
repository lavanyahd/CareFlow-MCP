import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import DashboardPage from "./pages/DashboardPage";
import PatientDetailPage from "./pages/PatientDetailPage";
import ReferralUploadPage from "./pages/ReferralUploadPage";
import AuditLogPage from "./pages/AuditLogPage";
import ClinicianReviewPage from "./pages/ClinicianReviewPage";
import FhirViewerPage from "./pages/FhirViewerPage";
import ModelMonitoringPage from "./pages/ModelMonitoringPage";
import RagAssistantPage from "./pages/RagAssistantPage";
import SlmSummaryPage from "./pages/SlmSummaryPage";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route
          path="/"
          element={<DashboardPage />}
        />

        <Route
          path="/referrals/new"
          element={<ReferralUploadPage />}
        />

        <Route
          path="/referrals/:referralId"
          element={<PatientDetailPage />}
        />

        <Route
          path="/audit-logs"
          element={<AuditLogPage />}
        />

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />

        <Route
          path="/reviews/:referralId"
          element={<ClinicianReviewPage />}
        />

        <Route
  path="/fhir/:referralId"
  element={<FhirViewerPage />}
/>

<Route
  path="/monitoring"
  element={<ModelMonitoringPage />}
/>
        
        <Route
  path="/assistant/:referralId"
  element={<RagAssistantPage />}
/>

<Route
  path="/slm/:referralId"
  element={<SlmSummaryPage />}
/>

      </Routes>
    </BrowserRouter>
  );
}

export default App;
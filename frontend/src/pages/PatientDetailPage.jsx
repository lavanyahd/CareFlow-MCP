import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getReferral } from "../services/referralService";
import {
  getTriageResults,
  predictTriage,
} from "../services/triageService";
import {
  getDNAResults,
  predictDNA,
} from "../services/dnaService";
import { downloadReferralReport } from "../services/reportService";


function getUrgencyBadgeClass(urgency) {
  if (urgency === "Emergency") {
    return "text-bg-danger";
  }

  if (urgency === "Urgent") {
    return "text-bg-warning";
  }

  if (urgency === "Soon") {
    return "text-bg-info";
  }

  if (urgency === "Routine") {
    return "text-bg-primary";
  }

  return "text-bg-success";
}


function getDNABadgeClass(dnaRisk) {
  if (dnaRisk === "High") {
    return "text-bg-danger";
  }

  if (dnaRisk === "Medium") {
    return "text-bg-warning";
  }

  return "text-bg-success";
}


function PatientDetailPage() {
  const { referralId } = useParams();

  const [referral, setReferral] = useState(null);
  const [triageResult, setTriageResult] = useState(null);
  const [dnaResult, setDnaResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [triageLoading, setTriageLoading] = useState(false);
  const [dnaLoading, setDnaLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);

  const [error, setError] = useState("");
  const [triageError, setTriageError] = useState("");
  const [dnaError, setDnaError] = useState("");
  const [reportError, setReportError] = useState("");


  useEffect(() => {
    async function loadReferralData() {
      try {
        const referralData = await getReferral(referralId);
        setReferral(referralData);

        const triageResults = await getTriageResults(referralId);

        if (triageResults.length > 0) {
          setTriageResult(triageResults[0]);
        }

        const dnaResults = await getDNAResults(referralId);

        if (dnaResults.length > 0) {
          setDnaResult(dnaResults[0]);
        }
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadReferralData();
  }, [referralId]);


  async function handleRunTriagePrediction() {
    setTriageLoading(true);
    setTriageError("");

    try {
      const result = await predictTriage(referralId);
      setTriageResult(result);
    } catch (requestError) {
      setTriageError(requestError.message);
    } finally {
      setTriageLoading(false);
    }
  }


  async function handleRunDNAPrediction() {
    setDnaLoading(true);
    setDnaError("");

    try {
      const result = await predictDNA(referralId);
      setDnaResult(result);
    } catch (requestError) {
      setDnaError(requestError.message);
    } finally {
      setDnaLoading(false);
    }
  }


  async function handleDownloadReport() {
    setReportLoading(true);
    setReportError("");

    try {
      await downloadReferralReport(referralId);
    } catch (requestError) {
      setReportError(requestError.message);
    } finally {
      setReportLoading(false);
    }
  }


  if (loading) {
    return (
      <div className="container py-5">
        <p>Loading patient referral...</p>
      </div>
    );
  }


  if (error) {
    return (
      <div className="container py-5">
        <div className="alert alert-danger">
          {error}
        </div>

        <Link
          className="btn btn-outline-primary"
          to="/"
        >
          Return to Dashboard
        </Link>
      </div>
    );
  }


  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3">
            Patient Referral Details
          </h1>

          <p className="text-muted mb-0">
            Referral number: {referral.id}
          </p>
        </div>

        <div className="d-flex gap-2">
          <Link
            className="btn btn-outline-primary"
            to="/"
          >
            Back to Dashboard
          </Link>

          <Link
            className="btn btn-success"
            to={`/reviews/${referralId}`}
          >
            Clinician Review
          </Link>

          <button
            className="btn btn-dark"
            type="button"
            onClick={handleDownloadReport}
            disabled={reportLoading}
          >
            {reportLoading
              ? "Downloading..."
              : "Download PDF Report"}
          </button>
          <Link
  className="btn btn-outline-dark"
  to={`/fhir/${referralId}`}
>
  View FHIR Record
</Link>

<Link
  className="btn btn-outline-success"
  to={`/assistant/${referralId}`}
>
  Ask Assistant
</Link>
 
<Link
  className="btn btn-outline-secondary"
  to={`/slm/${referralId}`}
>
  SLM Summary
</Link>

        </div>
      </div>

      {reportError && (
        <div className="alert alert-danger">
          {reportError}
        </div>
      )}

      <div className="row g-4">
        <div className="col-lg-4">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Patient Information
              </h2>

              <dl className="row mb-0">
                <dt className="col-6">Patient ID</dt>
                <dd className="col-6">
                  {referral.patient_id}
                </dd>

                <dt className="col-6">Age</dt>
                <dd className="col-6">
                  {referral.age}
                </dd>

                <dt className="col-6">Gender</dt>
                <dd className="col-6">
                  {referral.gender}
                </dd>

                <dt className="col-6">Department</dt>
                <dd className="col-6">
                  {referral.department}
                </dd>

                <dt className="col-6">Waiting Days</dt>
                <dd className="col-6">
                  {referral.waiting_days}
                </dd>

                <dt className="col-6">Status</dt>
                <dd className="col-6">
                  <span className="badge text-bg-warning">
                    {referral.status}
                  </span>
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Referral Note
              </h2>

              <p className="referral-note mb-0">
                {referral.referral_text}
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Extracted Information
              </h2>

              <h3 className="h6">
                Symptoms
              </h3>

              {referral.extracted_symptoms?.length > 0 ? (
                <div className="d-flex flex-wrap gap-2 mb-4">
                  {referral.extracted_symptoms.map(
                    (symptom) => (
                      <span
                        className="badge text-bg-primary"
                        key={symptom}
                      >
                        {symptom}
                      </span>
                    )
                  )}
                </div>
              ) : (
                <p className="text-muted">
                  No known symptoms were extracted.
                </p>
              )}

              <h3 className="h6">
                Existing Conditions
              </h3>

              {referral.extracted_conditions?.length > 0 ? (
                <div className="d-flex flex-wrap gap-2 mb-4">
                  {referral.extracted_conditions.map(
                    (condition) => (
                      <span
                        className="badge text-bg-secondary"
                        key={condition}
                      >
                        {condition}
                      </span>
                    )
                  )}
                </div>
              ) : (
                <p className="text-muted">
                  No known conditions were extracted.
                </p>
              )}

              <h3 className="h6">
                Reported Duration
              </h3>

              <p className="mb-0">
                {referral.duration_days !== null
                  ? `${referral.duration_days} days`
                  : "Duration was not detected."}
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Red-Flag Assessment
              </h2>

              {referral.red_flag_detected ? (
                <div className="alert alert-danger">
                  <strong>Red flag detected</strong>
                </div>
              ) : (
                <div className="alert alert-success">
                  No configured red-flag combination detected.
                </div>
              )}

              <p>
                <strong>Red-flag score:</strong>{" "}
                {Math.round(referral.red_flag_score * 100)}
                %
              </p>

              <p className="mb-0">
                <strong>Reason:</strong>{" "}
                {referral.red_flag_reason}
              </p>
            </div>
          </div>
        </div>

        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <h2 className="h5 mb-1">
                    ML Triage Prediction
                  </h2>

                  <p className="text-muted mb-0">
                    Predict urgency using the trained triage model.
                  </p>
                </div>

                <button
                  className="btn btn-primary"
                  type="button"
                  onClick={handleRunTriagePrediction}
                  disabled={triageLoading}
                >
                  {triageLoading
                    ? "Predicting..."
                    : "Run Triage Prediction"}
                </button>
              </div>

              {triageError && (
                <div className="alert alert-danger">
                  {triageError}
                </div>
              )}

              {!triageResult && !triageError && (
                <div className="alert alert-info mb-0">
                  No triage prediction has been generated yet.
                </div>
              )}

              {triageResult && (
                <div className="row g-3">
                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Predicted Urgency
                      </p>

                      <span
                        className={`badge ${getUrgencyBadgeClass(
                          triageResult.predicted_urgency
                        )}`}
                      >
                        {triageResult.predicted_urgency}
                      </span>
                    </div>
                  </div>

                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Final Urgency
                      </p>

                      <span
                        className={`badge ${getUrgencyBadgeClass(
                          triageResult.final_urgency
                        )}`}
                      >
                        {triageResult.final_urgency}
                      </span>
                    </div>
                  </div>

                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Confidence
                      </p>

                      <h3 className="h5 mb-0">
                        {Math.round(
                          triageResult.confidence * 100
                        )}
                        %
                      </h3>
                    </div>
                  </div>

                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Risk Score
                      </p>

                      <h3 className="h5 mb-0">
                        {Math.round(
                          triageResult.risk_score * 100
                        )}
                        %
                      </h3>
                    </div>
                  </div>

                  <div className="col-12">
                    <div className="alert alert-secondary mb-0">
                      <strong>Explanation:</strong>{" "}
                      {triageResult.explanation}
                    </div>
                  </div>

                  <div className="col-12">
                    <div className="alert alert-warning mb-0">
                      Human review required:{" "}
                      {triageResult.human_review_required
                        ? "Yes"
                        : "No"}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <h2 className="h5 mb-1">
                    DNA Missed Appointment Prediction
                  </h2>

                  <p className="text-muted mb-0">
                    Predict whether the patient may miss the appointment.
                  </p>
                </div>

                <button
                  className="btn btn-dark"
                  type="button"
                  onClick={handleRunDNAPrediction}
                  disabled={dnaLoading}
                >
                  {dnaLoading
                    ? "Predicting..."
                    : "Run DNA Prediction"}
                </button>
              </div>

              {dnaError && (
                <div className="alert alert-danger">
                  {dnaError}
                </div>
              )}

              {!dnaResult && !dnaError && (
                <div className="alert alert-info mb-0">
                  No DNA prediction has been generated yet.
                </div>
              )}

              {dnaResult && (
                <div className="row g-3">
                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        DNA Risk
                      </p>

                      <span
                        className={`badge ${getDNABadgeClass(
                          dnaResult.dna_risk
                        )}`}
                      >
                        {dnaResult.dna_risk}
                      </span>
                    </div>
                  </div>

                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Confidence
                      </p>

                      <h3 className="h5 mb-0">
                        {Math.round(
                          dnaResult.confidence * 100
                        )}
                        %
                      </h3>
                    </div>
                  </div>

                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Risk Score
                      </p>

                      <h3 className="h5 mb-0">
                        {Math.round(
                          dnaResult.risk_score * 100
                        )}
                        %
                      </h3>
                    </div>
                  </div>

                  <div className="col-md-3">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Reminder Sent
                      </p>

                      <h3 className="h6 mb-0">
                        {dnaResult.reminder_sent ? "Yes" : "No"}
                      </h3>
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Appointment Day
                      </p>

                      <h3 className="h6 mb-0">
                        {dnaResult.appointment_day}
                      </h3>
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Appointment Time
                      </p>

                      <h3 className="h6 mb-0">
                        {dnaResult.appointment_time}
                      </h3>
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="border rounded p-3 h-100">
                      <p className="text-muted mb-1">
                        Distance Band
                      </p>

                      <h3 className="h6 mb-0">
                        {dnaResult.distance_band}
                      </h3>
                    </div>
                  </div>

                  <div className="col-12">
                    <div className="alert alert-secondary mb-0">
                      <strong>Recommended Action:</strong>{" "}
                      {dnaResult.recommended_action}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-12">
          <div className="alert alert-warning mb-0">
            This is a synthetic clinical decision-support
            prototype. It must not be used for diagnosis or
            real healthcare decision-making.
          </div>
        </div>
      </div>
    </main>
  );
}

export default PatientDetailPage;
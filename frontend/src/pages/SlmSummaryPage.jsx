import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getSlmReferralSummary } from "../services/slmService";


function SlmSummaryPage() {
  const { referralId } = useParams();

  const [summaryResult, setSummaryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function handleGenerateSummary() {
    setLoading(true);
    setError("");

    try {
      const result = await getSlmReferralSummary(referralId);
      setSummaryResult(result);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3">
            SLM Referral Summary
          </h1>

          <p className="text-muted mb-0">
            Generate a safe decision-support summary for referral #{referralId}.
          </p>
        </div>

        <Link
          className="btn btn-outline-primary"
          to={`/referrals/${referralId}`}
        >
          Back to Referral
        </Link>
      </div>

      <div className="alert alert-info">
        This page uses the SLM summary endpoint. If Ollama/local SLM is not running,
        the system uses the CareFlow fallback summary engine.
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <h2 className="h5 mb-3">
            Generate Summary
          </h2>

          <p className="text-muted">
            The summary is generated using referral details, extracted symptoms,
            red flags, triage result, DNA result, and clinician review.
          </p>

          <button
            className="btn btn-primary"
            type="button"
            onClick={handleGenerateSummary}
            disabled={loading}
          >
            {loading
              ? "Generating..."
              : "Generate SLM Summary"}
          </button>
        </div>
      </div>

      {!summaryResult && !loading && (
        <div className="alert alert-secondary">
          No SLM summary has been generated yet.
        </div>
      )}

      {summaryResult && (
        <div className="card shadow-sm">
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2 className="h5 mb-0">
                Generated Summary
              </h2>

              <span className="badge text-bg-dark">
                {summaryResult.generated_by}
              </span>
            </div>

            <div className="mb-3">
              <strong>Patient ID:</strong>{" "}
              {summaryResult.patient_id}
            </div>

            <div
              className="border rounded p-3 bg-light"
              style={{
                whiteSpace: "pre-wrap",
                lineHeight: "1.7",
              }}
            >
              {summaryResult.summary}
            </div>

            <div className="alert alert-warning mt-4 mb-0">
              {summaryResult.safety_note}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}


export default SlmSummaryPage;
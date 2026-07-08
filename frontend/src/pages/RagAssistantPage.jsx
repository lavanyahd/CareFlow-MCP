import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getReferral } from "../services/referralService";
import { askReferralAssistant } from "../services/ragService";


const QUICK_QUESTIONS = [
  "Summarize this referral.",
  "Why is this patient emergency?",
  "What red flag was detected?",
  "What is the DNA risk?",
  "What should staff do next?",
  "Has a clinician reviewed this referral?",
];


function RagAssistantPage() {
  const { referralId } = useParams();

  const [referral, setReferral] = useState(null);
  const [question, setQuestion] = useState("");
  const [assistantResult, setAssistantResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");


  useEffect(() => {
    async function loadReferral() {
      try {
        const referralData = await getReferral(referralId);
        setReferral(referralData);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadReferral();
  }, [referralId]);


  async function submitQuestion(questionText) {
    if (!questionText.trim()) {
      setError("Please enter a question.");
      return;
    }

    setAsking(true);
    setError("");

    try {
      const result = await askReferralAssistant(
        referralId,
        questionText
      );

      setAssistantResult(result);
      setQuestion(questionText);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setAsking(false);
    }
  }


  async function handleSubmit(event) {
    event.preventDefault();

    await submitQuestion(question);
  }


  if (loading) {
    return (
      <div className="container py-5">
        <p>Loading referral assistant...</p>
      </div>
    );
  }


  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3">
            Referral Assistant
          </h1>

          <p className="text-muted mb-0">
            Ask questions about referral #{referralId}
          </p>
        </div>

        <Link
          className="btn btn-outline-primary"
          to={`/referrals/${referralId}`}
        >
          Back to Referral
        </Link>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {referral && (
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <h2 className="h5 mb-3">
              Referral Summary
            </h2>

            <div className="row">
              <div className="col-md-3">
                <strong>Patient ID</strong>
                <p>{referral.patient_id}</p>
              </div>

              <div className="col-md-3">
                <strong>Age</strong>
                <p>{referral.age}</p>
              </div>

              <div className="col-md-3">
                <strong>Department</strong>
                <p>{referral.department}</p>
              </div>

              <div className="col-md-3">
                <strong>Status</strong>
                <p>
                  <span className="badge text-bg-warning">
                    {referral.status}
                  </span>
                </p>
              </div>
            </div>

            <p className="mb-0">
              <strong>Referral Note:</strong>{" "}
              {referral.referral_text}
            </p>
          </div>
        </div>
      )}

      <div className="row g-4">
        <div className="col-lg-5">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Ask a Question
              </h2>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">
                    Question
                  </label>

                  <textarea
                    className="form-control"
                    rows="5"
                    value={question}
                    onChange={(event) =>
                      setQuestion(event.target.value)
                    }
                    placeholder="Example: Why is this patient emergency?"
                    required
                  />
                </div>

                <button
                  className="btn btn-primary"
                  type="submit"
                  disabled={asking}
                >
                  {asking ? "Asking..." : "Ask Assistant"}
                </button>
              </form>

              <hr />

              <h3 className="h6 mb-3">
                Quick Questions
              </h3>

              <div className="d-flex flex-wrap gap-2">
                {QUICK_QUESTIONS.map((quickQuestion) => (
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    type="button"
                    key={quickQuestion}
                    onClick={() =>
                      submitQuestion(quickQuestion)
                    }
                    disabled={asking}
                  >
                    {quickQuestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-7">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Assistant Answer
              </h2>

              {!assistantResult && (
                <div className="alert alert-info mb-0">
                  Ask a question to see the assistant response.
                </div>
              )}

              {assistantResult && (
                <>
                  <div className="mb-3">
                    <strong>Question:</strong>
                    <p className="mb-0">
                      {assistantResult.question}
                    </p>
                  </div>

                  <div className="alert alert-secondary">
                    <strong>Answer:</strong>{" "}
                    {assistantResult.answer}
                  </div>

                  <div className="mb-3">
                    <strong>Sources used:</strong>

                    <div className="d-flex flex-wrap gap-2 mt-2">
                      {assistantResult.sources.map((source) => (
                        <span
                          className="badge text-bg-primary"
                          key={source}
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="alert alert-warning mb-0">
                    {assistantResult.safety_note}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}


export default RagAssistantPage;
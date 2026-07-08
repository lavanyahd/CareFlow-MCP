import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getReferral } from "../services/referralService";
import {
  createClinicianReview,
  getClinicianReviews,
} from "../services/reviewService";


function ClinicianReviewPage() {
  const { referralId } = useParams();

  const [referral, setReferral] = useState(null);
  const [reviews, setReviews] = useState([]);

  const [reviewerName, setReviewerName] = useState("");
  const [decision, setDecision] = useState("Approve ML decision");
  const [finalUrgency, setFinalUrgency] = useState("Urgent");
  const [notes, setNotes] = useState("");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");


  useEffect(() => {
    async function loadData() {
      try {
        const referralData = await getReferral(referralId);
        setReferral(referralData);

        const reviewData = await getClinicianReviews(referralId);
        setReviews(reviewData);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [referralId]);


  async function handleSubmit(event) {
    event.preventDefault();

    setSubmitting(true);
    setError("");
    setSuccessMessage("");

    try {
      const reviewData = {
        reviewer_name: reviewerName,
        decision: decision,
        final_urgency: finalUrgency,
        notes: notes,
      };

      const savedReview = await createClinicianReview(
        referralId,
        reviewData
      );

      setReviews([savedReview, ...reviews]);

      setSuccessMessage(
        "Clinician review saved successfully."
      );

      setReviewerName("");
      setDecision("Approve ML decision");
      setFinalUrgency("Urgent");
      setNotes("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }


  if (loading) {
    return (
      <div className="container py-5">
        <p>Loading review page...</p>
      </div>
    );
  }


  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3">
            Clinician Review
          </h1>

          <p className="text-muted mb-0">
            Human review and final decision for referral #{referralId}
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

      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
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
                <strong>Patient ID:</strong>
                <p>{referral.patient_id}</p>
              </div>

              <div className="col-md-3">
                <strong>Age:</strong>
                <p>{referral.age}</p>
              </div>

              <div className="col-md-3">
                <strong>Department:</strong>
                <p>{referral.department}</p>
              </div>

              <div className="col-md-3">
                <strong>Status:</strong>
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
        <div className="col-lg-6">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Add Review
              </h2>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">
                    Reviewer Name
                  </label>

                  <input
                    className="form-control"
                    type="text"
                    value={reviewerName}
                    onChange={(event) =>
                      setReviewerName(event.target.value)
                    }
                    placeholder="Example: Dr Smith"
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    Decision
                  </label>

                  <select
                    className="form-select"
                    value={decision}
                    onChange={(event) =>
                      setDecision(event.target.value)
                    }
                  >
                    <option>
                      Approve ML decision
                    </option>
                    <option>
                      Override ML decision
                    </option>
                    <option>
                      Request more information
                    </option>
                  </select>
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    Final Urgency
                  </label>

                  <select
                    className="form-select"
                    value={finalUrgency}
                    onChange={(event) =>
                      setFinalUrgency(event.target.value)
                    }
                  >
                    <option>Emergency</option>
                    <option>Urgent</option>
                    <option>Soon</option>
                    <option>Routine</option>
                    <option>Self-care</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    Review Notes
                  </label>

                  <textarea
                    className="form-control"
                    rows="5"
                    value={notes}
                    onChange={(event) =>
                      setNotes(event.target.value)
                    }
                    placeholder="Add clinician notes here..."
                    required
                  />
                </div>

                <button
                  className="btn btn-primary"
                  type="submit"
                  disabled={submitting}
                >
                  {submitting
                    ? "Saving..."
                    : "Save Clinician Review"}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Review History
              </h2>

              {reviews.length === 0 && (
                <div className="alert alert-info">
                  No clinician reviews added yet.
                </div>
              )}

              {reviews.map((review) => (
                <div
                  className="border rounded p-3 mb-3"
                  key={review.id}
                >
                  <div className="d-flex justify-content-between">
                    <strong>
                      {review.reviewer_name}
                    </strong>

                    <span className="badge text-bg-primary">
                      {review.final_urgency}
                    </span>
                  </div>

                  <p className="mb-1 mt-2">
                    <strong>Decision:</strong>{" "}
                    {review.decision}
                  </p>

                  <p className="mb-1">
                    <strong>Notes:</strong>{" "}
                    {review.notes}
                  </p>

                  <p className="text-muted mb-0">
                    {new Date(
                      review.created_at
                    ).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="alert alert-warning mt-4">
        AI outputs are decision-support only. Final clinical
        decisions must be made by qualified healthcare staff.
      </div>
    </main>
  );
}


export default ClinicianReviewPage;
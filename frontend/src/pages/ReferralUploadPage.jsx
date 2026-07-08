import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createReferral } from "../services/referralService";


const initialFormData = {
  patient_id: "",
  age: "",
  gender: "",
  department: "",
  waiting_days: "0",
  referral_text: "",
};


function ReferralUploadPage() {
  const navigate = useNavigate();

  const [formData, setFormData] =
    useState(initialFormData);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] = useState("");


  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));
  }


  async function handleSubmit(event) {
    event.preventDefault();

    setSubmitting(true);
    setError("");

    const requestData = {
      ...formData,
      age: Number(formData.age),
      waiting_days: Number(formData.waiting_days),
    };

    try {
      const createdReferral =
        await createReferral(requestData);

      navigate(`/referrals/${createdReferral.id}`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-body p-4">
              <h1 className="h3 mb-2">
                Upload Patient Referral
              </h1>

              <p className="text-muted">
                Enter synthetic patient information only.
                Do not use real patient data.
              </p>

              {error && (
                <div
                  className="alert alert-danger"
                  role="alert"
                >
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  <div className="col-md-6">
                    <label
                      className="form-label"
                      htmlFor="patient_id"
                    >
                      Patient ID
                    </label>

                    <input
                      id="patient_id"
                      name="patient_id"
                      className="form-control"
                      value={formData.patient_id}
                      onChange={handleChange}
                      placeholder="P001"
                      required
                    />
                  </div>

                  <div className="col-md-3">
                    <label
                      className="form-label"
                      htmlFor="age"
                    >
                      Age
                    </label>

                    <input
                      id="age"
                      name="age"
                      type="number"
                      className="form-control"
                      min="0"
                      max="120"
                      value={formData.age}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="col-md-3">
                    <label
                      className="form-label"
                      htmlFor="gender"
                    >
                      Gender
                    </label>

                    <select
                      id="gender"
                      name="gender"
                      className="form-select"
                      value={formData.gender}
                      onChange={handleChange}
                      required
                    >
                      <option value="">
                        Select
                      </option>
                      <option value="Female">
                        Female
                      </option>
                      <option value="Male">
                        Male
                      </option>
                      <option value="Other">
                        Other
                      </option>
                      <option value="Not stated">
                        Prefer not to state
                      </option>
                    </select>
                  </div>

                  <div className="col-md-8">
                    <label
                      className="form-label"
                      htmlFor="department"
                    >
                      Referral Department
                    </label>

                    <select
                      id="department"
                      name="department"
                      className="form-select"
                      value={formData.department}
                      onChange={handleChange}
                      required
                    >
                      <option value="">
                        Select department
                      </option>
                      <option value="Cardiology">
                        Cardiology
                      </option>
                      <option value="Respiratory">
                        Respiratory
                      </option>
                      <option value="Gastroenterology">
                        Gastroenterology
                      </option>
                      <option value="Dermatology">
                        Dermatology
                      </option>
                      <option value="Neurology">
                        Neurology
                      </option>
                      <option value="General Medicine">
                        General Medicine
                      </option>
                    </select>
                  </div>

                  <div className="col-md-4">
                    <label
                      className="form-label"
                      htmlFor="waiting_days"
                    >
                      Waiting Days
                    </label>

                    <input
                      id="waiting_days"
                      name="waiting_days"
                      type="number"
                      className="form-control"
                      min="0"
                      value={formData.waiting_days}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="col-12">
                    <label
                      className="form-label"
                      htmlFor="referral_text"
                    >
                      Referral Note
                    </label>

                    <textarea
                      id="referral_text"
                      name="referral_text"
                      className="form-control"
                      rows="7"
                      value={formData.referral_text}
                      onChange={handleChange}
                      placeholder="Describe symptoms, duration and existing conditions..."
                      minLength="10"
                      required
                    />
                  </div>

                  <div className="col-12 d-flex gap-2">
                    <button
                      className="btn btn-primary"
                      type="submit"
                      disabled={submitting}
                    >
                      {submitting
                        ? "Uploading..."
                        : "Upload Referral"}
                    </button>

                    <button
                      className="btn btn-outline-secondary"
                      type="button"
                      onClick={() => navigate("/")}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default ReferralUploadPage;
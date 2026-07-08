import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getFhirBundle } from "../services/fhirService";


function getResourcesByType(bundle, resourceType) {
  if (!bundle?.entry) {
    return [];
  }

  return bundle.entry
    .map((entry) => entry.resource)
    .filter((resource) => resource.resourceType === resourceType);
}


function getFirstResourceByType(bundle, resourceType) {
  const resources = getResourcesByType(bundle, resourceType);

  if (resources.length === 0) {
    return null;
  }

  return resources[0];
}


function getComponentValue(resource, componentText) {
  const component = resource?.component?.find(
    (item) => item.code?.text === componentText
  );

  if (!component) {
    return "Not available";
  }

  if (component.valueString !== undefined) {
    return component.valueString;
  }

  if (component.valueDecimal !== undefined) {
    return component.valueDecimal;
  }

  if (component.valueBoolean !== undefined) {
    return component.valueBoolean ? "Yes" : "No";
  }

  return "Not available";
}


function FhirViewerPage() {
  const { referralId } = useParams();

  const [fhirBundle, setFhirBundle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showJson, setShowJson] = useState(false);


  useEffect(() => {
    async function loadFhirBundle() {
      try {
        const data = await getFhirBundle(referralId);
        setFhirBundle(data);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadFhirBundle();
  }, [referralId]);


  if (loading) {
    return (
      <div className="container py-5">
        <p>Loading FHIR record...</p>
      </div>
    );
  }


  const patient = getFirstResourceByType(
    fhirBundle,
    "Patient"
  );

  const serviceRequest = getFirstResourceByType(
    fhirBundle,
    "ServiceRequest"
  );

  const observations = getResourcesByType(
    fhirBundle,
    "Observation"
  );

  const conditions = getResourcesByType(
    fhirBundle,
    "Condition"
  );

  const symptomObservations = observations.filter(
    (observation) =>
      observation.code?.text === "Extracted symptom"
  );

  const redFlagObservation = observations.find(
    (observation) =>
      observation.code?.text === "CareFlow red-flag assessment"
  );

  const triageObservation = observations.find(
    (observation) =>
      observation.code?.text === "CareFlow ML triage prediction"
  );

  const dnaObservation = observations.find(
    (observation) =>
      observation.code?.text ===
      "CareFlow DNA missed appointment prediction"
  );


  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3">
            FHIR Mock Patient Record
          </h1>

          <p className="text-muted mb-0">
            Referral #{referralId} represented using healthcare-style FHIR resources.
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

      {!error && fhirBundle && (
        <>
          <div className="alert alert-info">
            This page shows the referral as a mock FHIR Bundle. Cards are shown for readability, and raw JSON is kept for technical validation.
          </div>

          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="h5 mb-3">
                Bundle Summary
              </h2>

              <div className="row">
                <div className="col-md-4">
                  <strong>Resource Type</strong>
                  <p>{fhirBundle.resourceType}</p>
                </div>

                <div className="col-md-4">
                  <strong>Bundle Type</strong>
                  <p>{fhirBundle.type}</p>
                </div>

                <div className="col-md-4">
                  <strong>Total Entries</strong>
                  <p>{fhirBundle.entry?.length || 0}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="row g-4">
            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    Patient Resource
                  </h2>

                  {patient ? (
                    <dl className="row mb-0">
                      <dt className="col-5">FHIR Type</dt>
                      <dd className="col-7">{patient.resourceType}</dd>

                      <dt className="col-5">Patient ID</dt>
                      <dd className="col-7">{patient.id}</dd>

                      <dt className="col-5">Gender</dt>
                      <dd className="col-7">{patient.gender}</dd>

                      <dt className="col-5">Age</dt>
                      <dd className="col-7">
                        {patient.extension?.[0]?.valueInteger ??
                          "Not available"}
                      </dd>
                    </dl>
                  ) : (
                    <p className="text-muted mb-0">
                      Patient resource not found.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    ServiceRequest Resource
                  </h2>

                  {serviceRequest ? (
                    <dl className="row mb-0">
                      <dt className="col-5">FHIR Type</dt>
                      <dd className="col-7">
                        {serviceRequest.resourceType}
                      </dd>

                      <dt className="col-5">Referral ID</dt>
                      <dd className="col-7">
                        {serviceRequest.id}
                      </dd>

                      <dt className="col-5">Status</dt>
                      <dd className="col-7">
                        {serviceRequest.status}
                      </dd>

                      <dt className="col-5">Department</dt>
                      <dd className="col-7">
                        {serviceRequest.category?.[0]?.text}
                      </dd>

                      <dt className="col-5">Priority</dt>
                      <dd className="col-7">
                        <span className="badge text-bg-warning">
                          {serviceRequest.priority}
                        </span>
                      </dd>
                    </dl>
                  ) : (
                    <p className="text-muted mb-0">
                      ServiceRequest resource not found.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    Extracted Symptoms
                  </h2>

                  {symptomObservations.length > 0 ? (
                    <div className="d-flex flex-wrap gap-2">
                      {symptomObservations.map((symptom) => (
                        <span
                          className="badge text-bg-primary"
                          key={symptom.id}
                        >
                          {symptom.valueString}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted mb-0">
                      No symptom observations found.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    Conditions
                  </h2>

                  {conditions.length > 0 ? (
                    <div className="d-flex flex-wrap gap-2">
                      {conditions.map((condition) => (
                        <span
                          className="badge text-bg-secondary"
                          key={condition.id}
                        >
                          {condition.code?.text}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted mb-0">
                      No condition resources found.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    Red-Flag Observation
                  </h2>

                  {redFlagObservation ? (
                    <>
                      <p>
                        <strong>Red Flag Detected:</strong>{" "}
                        {redFlagObservation.valueBoolean ? (
                          <span className="badge text-bg-danger">
                            Yes
                          </span>
                        ) : (
                          <span className="badge text-bg-success">
                            No
                          </span>
                        )}
                      </p>

                      <p>
                        <strong>Score:</strong>{" "}
                        {Math.round(
                          Number(
                            getComponentValue(
                              redFlagObservation,
                              "Red flag score"
                            )
                          ) * 100
                        )}
                        %
                      </p>

                      <p className="mb-0">
                        <strong>Reason:</strong>{" "}
                        {getComponentValue(
                          redFlagObservation,
                          "Red flag reason"
                        )}
                      </p>
                    </>
                  ) : (
                    <p className="text-muted mb-0">
                      Red-flag observation not found.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    ML Triage Observation
                  </h2>

                  {triageObservation ? (
                    <>
                      <p>
                        <strong>Final Urgency:</strong>{" "}
                        <span className="badge text-bg-danger">
                          {triageObservation.valueString}
                        </span>
                      </p>

                      <p>
                        <strong>Predicted Urgency:</strong>{" "}
                        {getComponentValue(
                          triageObservation,
                          "Predicted urgency"
                        )}
                      </p>

                      <p>
                        <strong>Confidence:</strong>{" "}
                        {Math.round(
                          Number(
                            getComponentValue(
                              triageObservation,
                              "Confidence"
                            )
                          ) * 100
                        )}
                        %
                      </p>

                      <p className="mb-0">
                        <strong>Model:</strong>{" "}
                        {getComponentValue(
                          triageObservation,
                          "Model name"
                        )}
                      </p>
                    </>
                  ) : (
                    <p className="text-muted mb-0">
                      Triage observation not found.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 mb-3">
                    DNA Missed Appointment Observation
                  </h2>

                  {dnaObservation ? (
                    <>
                      <p>
                        <strong>DNA Risk:</strong>{" "}
                        <span className="badge text-bg-success">
                          {dnaObservation.valueString}
                        </span>
                      </p>

                      <p>
                        <strong>Confidence:</strong>{" "}
                        {Math.round(
                          Number(
                            getComponentValue(
                              dnaObservation,
                              "Confidence"
                            )
                          ) * 100
                        )}
                        %
                      </p>

                      <p>
                        <strong>Risk Score:</strong>{" "}
                        {Math.round(
                          Number(
                            getComponentValue(
                              dnaObservation,
                              "Risk score"
                            )
                          ) * 100
                        )}
                        %
                      </p>

                      <p className="mb-0">
                        <strong>Recommended Action:</strong>{" "}
                        {getComponentValue(
                          dnaObservation,
                          "Recommended action"
                        )}
                      </p>
                    </>
                  ) : (
                    <p className="text-muted mb-0">
                      DNA observation not found.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="card shadow-sm mt-4">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h2 className="h5 mb-0">
                  Raw FHIR JSON Bundle
                </h2>

                <button
                  className="btn btn-sm btn-outline-dark"
                  type="button"
                  onClick={() => setShowJson(!showJson)}
                >
                  {showJson ? "Hide JSON" : "Show JSON"}
                </button>
              </div>

              {showJson && (
                <pre
                  className="bg-light border rounded p-3"
                  style={{
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    maxHeight: "700px",
                    overflowY: "auto",
                  }}
                >
                  {JSON.stringify(fhirBundle, null, 2)}
                </pre>
              )}

              {!showJson && (
                <p className="text-muted mb-0">
                  Raw JSON is hidden. Click Show JSON to view the technical FHIR bundle.
                </p>
              )}
            </div>
          </div>
        </>
      )}
    </main>
  );
}


export default FhirViewerPage;
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getWaitingList } from "../services/waitingListService";


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

  if (urgency === "Self-care") {
    return "text-bg-success";
  }

  return "text-bg-secondary";
}


function getPriorityBadgeClass(priorityScore) {
  if (priorityScore >= 85) {
    return "text-bg-danger";
  }

  if (priorityScore >= 70) {
    return "text-bg-warning";
  }

  if (priorityScore >= 50) {
    return "text-bg-info";
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

  if (dnaRisk === "Low") {
    return "text-bg-success";
  }

  return "text-bg-secondary";
}


function DashboardPage() {
  const [waitingList, setWaitingList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadWaitingList() {
      try {
        const data = await getWaitingList();
        setWaitingList(data);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadWaitingList();
  }, []);


  if (loading) {
    return (
      <div className="container py-5">
        <p>Loading waiting list...</p>
      </div>
    );
  }


  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3">
            Waiting List Prioritisation Dashboard
          </h1>

          <p className="text-muted mb-0">
            Patients are ranked by clinical urgency, red flags,
            waiting time, and operational DNA risk.
          </p>
        </div>

        <Link
          className="btn btn-primary"
          to="/referrals/new"
        >
          Upload Referral
        </Link>
      </div>

      {error && (
        <div
          className="alert alert-danger"
          role="alert"
        >
          {error}
        </div>
      )}

      {!error && waitingList.length === 0 && (
        <div className="alert alert-info">
          No referrals have been uploaded yet.
        </div>
      )}

      {waitingList.length > 0 && (
        <div className="table-responsive">
          <table className="table table-bordered table-hover align-middle">
            <thead className="table-light">
              <tr>
                <th>Rank</th>
                <th>Patient ID</th>
                <th>Age</th>
                <th>Department</th>
                <th>Waiting Days</th>
                <th>Urgency</th>
                <th>Priority</th>
                <th>DNA Risk</th>
                <th>Red Flag</th>
                <th>Suggested Clinical Action</th>
                <th>DNA Action</th>
                <th>Status</th>
                <th>View</th>
              </tr>
            </thead>

            <tbody>
              {waitingList.map((item, index) => (
                <tr key={item.referral_id}>
                  <td>
                    <strong>#{index + 1}</strong>
                  </td>

                  <td>{item.patient_id}</td>

                  <td>{item.age}</td>

                  <td>{item.department}</td>

                  <td>{item.waiting_days}</td>

                  <td>
                    <span
                      className={`badge ${getUrgencyBadgeClass(
                        item.triage_urgency
                      )}`}
                    >
                      {item.triage_urgency}
                    </span>
                  </td>

                  <td>
                    <span
                      className={`badge ${getPriorityBadgeClass(
                        item.priority_score
                      )}`}
                    >
                      {item.priority_score}/100
                    </span>
                  </td>

                  <td>
                    <span
                      className={`badge ${getDNABadgeClass(
                        item.dna_risk
                      )}`}
                    >
                      {item.dna_risk}
                    </span>
                  </td>

                  <td>
                    {item.red_flag_detected ? (
                      <span className="badge text-bg-danger">
                        Detected
                      </span>
                    ) : (
                      <span className="badge text-bg-success">
                        None
                      </span>
                    )}
                  </td>

                  <td>
                    {item.suggested_action}
                  </td>

                  <td>
                    {item.dna_recommended_action}
                  </td>

                  <td>
                    <span className="badge text-bg-warning">
                      {item.status}
                    </span>
                  </td>

                  <td>
                    <Link
                      className="btn btn-sm btn-outline-primary"
                      to={`/referrals/${item.referral_id}`}
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

export default DashboardPage;
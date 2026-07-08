import { useEffect, useState } from "react";

import { getAuditLogs } from "../services/auditService";


function getActionBadge(action) {
  if (action === "RED_FLAG_DETECTED") {
    return "text-bg-danger";
  }

  if (action === "TRIAGE_PREDICTED") {
    return "text-bg-warning";
  }

  if (action === "DNA_RISK_PREDICTED") {
    return "text-bg-dark";
  }

  if (action === "REFERRAL_CREATED") {
    return "text-bg-primary";
  }

  if (action === "REFERRAL_PARSED") {
    return "text-bg-info";
  }
  if (action === "RAG_ASSISTANT_USED") {
    return "text-bg-success";
  }

  return "text-bg-success";
}


function formatAction(action) {
  return action
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1)
    )
    .join(" ");
}


function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadAuditLogs() {
      try {
        const data = await getAuditLogs();
        setLogs(data);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadAuditLogs();
  }, []);


  if (loading) {
    return (
      <main className="container py-5">
        <p>Loading audit logs...</p>
      </main>
    );
  }


  return (
    <main className="container py-4">
      <div className="mb-4">
        <h1 className="h3">
          System Audit Logs
        </h1>

        <p className="text-muted mb-0">
          Trace referral processing and automated
          safety checks.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {!error && logs.length === 0 && (
        <div className="alert alert-info">
          No audit records are available yet.
          Upload a new referral to generate logs.
        </div>
      )}

      {logs.length > 0 && (
        <div className="table-responsive">
          <table className="table table-bordered table-hover align-middle">
            <thead className="table-light">
              <tr>
                <th>Time</th>
                <th>Patient</th>
                <th>Referral</th>
                <th>Action</th>
                <th>Source</th>
                <th>Details</th>
              </tr>
            </thead>

            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>
                    {new Date(
                      log.created_at
                    ).toLocaleString()}
                  </td>

                  <td>{log.patient_id}</td>

                  <td>#{log.referral_id}</td>

                  <td>
                    <span
                      className={`badge ${getActionBadge(
                        log.action
                      )}`}
                    >
                      {formatAction(log.action)}
                    </span>
                  </td>

                  <td>{log.source}</td>

                  <td>{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

export default AuditLogPage;
import { useEffect, useState } from "react";

import { getModelMonitoring } from "../services/monitoringService";


function formatPercent(value) {
  if (value === undefined || value === null) {
    return "Not available";
  }

  return `${Math.round(Number(value) * 100)}%`;
}


function MetricCard({ title, value }) {
  return (
    <div className="col-md-3">
      <div className="card shadow-sm h-100">
        <div className="card-body">
          <p className="text-muted mb-1">
            {title}
          </p>

          <h2 className="h4 mb-0">
            {value}
          </h2>
        </div>
      </div>
    </div>
  );
}


function ResultsTable({ results }) {
  if (!results || results.length === 0) {
    return (
      <div className="alert alert-info">
        No model comparison results found.
      </div>
    );
  }

  return (
    <div className="table-responsive">
      <table className="table table-bordered table-hover align-middle">
        <thead className="table-light">
          <tr>
            {Object.keys(results[0]).map((column) => (
              <th key={column}>
                {column}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {results.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {Object.values(row).map((value, valueIndex) => (
                <td key={valueIndex}>
                  {typeof value === "number"
                    ? value.toFixed(4)
                    : value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


function ModelSection({ title, modelData, type }) {
  const metadata = modelData?.metadata || {};
  const results = modelData?.results || [];

  return (
    <section className="mb-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h2 className="h4 mb-1">
            {title}
          </h2>

          <p className="text-muted mb-0">
            Best model:{" "}
            <strong>
              {metadata.model_name || "Not available"}
            </strong>
          </p>
        </div>

        <span className="badge text-bg-primary">
          {metadata.available ? "Available" : "Missing metadata"}
        </span>
      </div>

      <div className="row g-3 mb-4">
        <MetricCard
          title="Accuracy"
          value={formatPercent(metadata.accuracy)}
        />

        <MetricCard
          title="Macro F1"
          value={formatPercent(metadata.macro_f1)}
        />

        {type === "triage" ? (
          <>
            <MetricCard
              title="Emergency Recall"
              value={formatPercent(metadata.emergency_recall)}
            />

            <MetricCard
              title="Urgent Recall"
              value={formatPercent(metadata.urgent_recall)}
            />
          </>
        ) : (
          <>
            <MetricCard
              title="High DNA Recall"
              value={formatPercent(metadata.high_recall)}
            />

            <MetricCard
              title="Medium DNA Recall"
              value={formatPercent(metadata.medium_recall)}
            />
          </>
        )}

        <MetricCard
          title="Priority Score"
          value={formatPercent(metadata.priority_score)}
        />

        <MetricCard
          title="Training Rows"
          value={metadata.training_rows || "Not available"}
        />

        <MetricCard
          title="Test Rows"
          value={metadata.test_rows || "Not available"}
        />

        <MetricCard
          title="Target"
          value={metadata.target || "Not available"}
        />
      </div>

      <div className="card shadow-sm">
        <div className="card-body">
          <h3 className="h5 mb-3">
            Model Comparison Results
          </h3>

          <ResultsTable results={results} />
        </div>
      </div>
    </section>
  );
}


function ModelMonitoringPage() {
  const [monitoringData, setMonitoringData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadMonitoringData() {
      try {
        const data = await getModelMonitoring();
        setMonitoringData(data);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }

    loadMonitoringData();
  }, []);


  if (loading) {
    return (
      <div className="container py-5">
        <p>Loading model monitoring dashboard...</p>
      </div>
    );
  }


  return (
    <main className="container py-4">
      <div className="mb-4">
        <h1 className="h3">
          Model Monitoring Dashboard
        </h1>

        <p className="text-muted mb-0">
          Track performance of triage and DNA prediction models used in CareFlow-MCP.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {!error && monitoringData && (
        <>
          <div className="alert alert-warning">
            These metrics are based on synthetic training data. They are for prototype monitoring only.
          </div>

          <ModelSection
            title="Triage Urgency Model"
            modelData={monitoringData.triage_model}
            type="triage"
          />

          <ModelSection
            title="DNA Missed Appointment Model"
            modelData={monitoringData.dna_model}
            type="dna"
          />
        </>
      )}
    </main>
  );
}


export default ModelMonitoringPage;
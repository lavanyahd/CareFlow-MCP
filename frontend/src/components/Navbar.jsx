import { Link } from "react-router-dom";


function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container">
        <Link
          className="navbar-brand fw-bold"
          to="/"
        >
          CareFlow-MCP
        </Link>

        <div className="navbar-nav ms-auto">
          <Link
            className="nav-link"
            to="/"
          >
            Dashboard
          </Link>

          <Link
            className="nav-link"
            to="/referrals/new"
          >
            Upload Referral
          </Link>

          <Link
            className="nav-link"
            to="/monitoring"
          >
            Model Monitoring
          </Link>

          <Link
            className="nav-link"
            to="/audit-logs"
          >
            Audit Logs
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
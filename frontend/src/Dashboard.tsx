import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface ThreatAlert {
  id: number;
  username: string;
  ip_address: string;
  alert_type: string;
  severity: string;
  description: string;
  timestamp: string;
}

interface DashboardStats {
  total_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  total_authentication_events: number;
  failed_login_attempts: number;
}

function Dashboard() {
  const [alerts, setAlerts] = useState<ThreatAlert[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");

  const [generatingAlerts, setGeneratingAlerts] =
  useState<boolean>(false);

const [alertMessage, setAlertMessage] =
  useState<string>("");

  const navigate = useNavigate();

  const loadDashboard = async (): Promise<void> => {
  const token = localStorage.getItem("token");

  if (!token) {
    navigate("/login");
    return;
  }

  try {
    const headers = {
      Authorization: `Bearer ${token}`,
    };

    const statsResponse = await fetch(
      "http://127.0.0.1:5000/dashboard-stats",
      {
        headers,
      }
    );

    if (!statsResponse.ok) {
      if (statsResponse.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        navigate("/login");
        return;
      }

      throw new Error("Unable to load dashboard statistics.");
    }

    const statsData: DashboardStats =
      await statsResponse.json();

    setStats(statsData);

    const alertsResponse = await fetch(
      "http://127.0.0.1:5000/threat-alerts",
      {
        headers,
      }
    );

    if (!alertsResponse.ok) {
      if (alertsResponse.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        navigate("/login");
        return;
      }

      throw new Error("Unable to load threat alerts.");
    }

    const alertsData: { alerts: ThreatAlert[] } =
      await alertsResponse.json();

    setAlerts(alertsData.alerts);
  } catch {
    setError("Unable to load dashboard data.");
  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  void loadDashboard();
}, [navigate]);

const handleGenerateAlerts = async (): Promise<void> => {
  const token = localStorage.getItem("token");

  if (!token) {
    navigate("/login");
    return;
  }

  setGeneratingAlerts(true);
  setAlertMessage("");
  setError("");

  try {
    const response = await fetch(
      "http://127.0.0.1:5000/generate-alerts",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      navigate("/login");
      return;
    }

    if (!response.ok) {
      throw new Error("Unable to generate threat alerts.");
    }

    const data: {
      message: string;
      alerts_created: number;
    } = await response.json();

    setAlertMessage(
      `${data.message} Alerts created: ${data.alerts_created}.`
    );

    await loadDashboard();
  } catch {
    setError("Unable to generate threat alerts.");
  } finally {
    setGeneratingAlerts(false);
  }
};

  const handleLogout = (): void => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");

    navigate("/login");
  };

  const filteredAlerts =
  severityFilter === "ALL"
    ? alerts
    : alerts.filter(
        (alert) => alert.severity === severityFilter
      );

  return (
    <div className="app">
      <div className="register-container dashboard-container">

        <h1>Security Monitoring Dashboard</h1>

        <p>
          Welcome,{" "}
          {localStorage.getItem("username") ?? "Analyst"}.
        </p>

        <p className="security-status">
          🛡️ Security Status: Monitoring Active
        </p>

        {loading && <p>Loading dashboard...</p>}

        {error && (
          <p className="error-message">
            {error}
          </p>
        )}

        {!loading && !error && stats && (
          <>
            <h2>Security Overview</h2>

            <div className="stats-grid">

              <div className="stat-card">
                <h3>Total Alerts</h3>
                <p>{stats.total_alerts}</p>
              </div>

              <div className="stat-card">
                <h3>High Severity</h3>
                <p>{stats.high_alerts}</p>
              </div>

              <div className="stat-card">
                <h3>Medium Severity</h3>
                <p>{stats.medium_alerts}</p>
              </div>

              <div className="stat-card">
                <h3>Low Severity</h3>
                <p>{stats.low_alerts}</p>
              </div>

              <div className="stat-card">
                <h3>Authentication Events</h3>
                <p>{stats.total_authentication_events}</p>
              </div>

              <div className="stat-card">
                <h3>Failed Logins</h3>
                <p>{stats.failed_login_attempts}</p>
              </div>

            </div>

            <h2>Threat Alerts</h2>
            <button
  type="button"
  onClick={handleGenerateAlerts}
  disabled={generatingAlerts}
>
  {generatingAlerts
    ? "Generating Alerts..."
    : "Generate Threat Alerts"}
</button>

{alertMessage && (
  <p className="security-status">
    {alertMessage}
  </p>
)}
            <div className="alert-filter">
  <label htmlFor="severity-filter">
    Filter by severity:
  </label>

  <select
    id="severity-filter"
    value={severityFilter}
    onChange={(event) =>
      setSeverityFilter(event.target.value)
    }
  >
    <option value="ALL">All</option>
    <option value="HIGH">High</option>
    <option value="MEDIUM">Medium</option>
    <option value="LOW">Low</option>
  </select>
</div>

            {alerts.length === 0 && (
              <p>No threat alerts detected.</p>
            )}

            {filteredAlerts.map((alert) => (
              <div
  className={`alert-card severity-${alert.severity.toLowerCase()}`}
  key={alert.id}
>
                <h3>{alert.alert_type}</h3>

                <p>
                  <strong>Severity:</strong>{" "}
                  {alert.severity}
                </p>

                <p>
                  <strong>User:</strong>{" "}
                  {alert.username}
                </p>

                <p>
                  <strong>IP Address:</strong>{" "}
                  {alert.ip_address}
                </p>

                <p>
                  <strong>Description:</strong>{" "}
                  {alert.description}
                </p>

                <p>
                  <strong>Time:</strong>{" "}
                  {alert.timestamp}
                </p>
              </div>
            ))}
          </>
        )}

        <div className="dashboard-navigation">
  <button
    type="button"
    onClick={() => navigate("/auth-logs")}
  >
    View Authentication Logs
  </button>

  <button
    type="button"
    onClick={handleLogout}
  >
    Logout
  </button>
</div>

      </div>
    </div>
  );
}

export default Dashboard;
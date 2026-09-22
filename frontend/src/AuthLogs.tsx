import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface AuthenticationLog {
  id: number;
  username: string;
  event_type: string;
  ip_address: string;
  timestamp: string;
}

const formatHarareTime = (timestamp: string): string => {
  return new Intl.DateTimeFormat("en-ZW", {
    timeZone: "Africa/Harare",
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(new Date(timestamp));
};

function AuthLogs() {
  const [logs, setLogs] = useState<AuthenticationLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  const navigate = useNavigate();

  useEffect(() => {
    const loadLogs = async (): Promise<void> => {
      const token = localStorage.getItem("token");

      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const response = await fetch(
          "http://127.0.0.1:5000/auth-logs",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          if (response.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("username");
            navigate("/login");
            return;
          }

          throw new Error("Unable to load authentication logs.");
        }

        const data: { logs: AuthenticationLog[] } =
          await response.json();

        setLogs(data.logs);
      } catch {
        setError("Unable to load authentication logs.");
      } finally {
        setLoading(false);
      }
    };

    void loadLogs();
  }, [navigate]);

  return (
    <div className="app">
      <div className="register-container dashboard-container">

        <h1>Authentication Logs</h1>

        <p>
          Review login activity recorded by the security
          monitoring system.
        </p>

        {loading && <p>Loading authentication logs...</p>}

        {error && (
          <p className="error-message">
            {error}
          </p>
        )}

        {!loading && !error && logs.length === 0 && (
          <p>No authentication events recorded.</p>
        )}

        {!loading && !error && logs.length > 0 && (
          <div className="logs-container">
            {logs.map((log) => (
              <div
                className="log-card"
                key={log.id}
              >
                <h3>{log.event_type}</h3>

                <p>
                  <strong>Username:</strong>{" "}
                  {log.username}
                </p>

                <p>
                  <strong>IP Address:</strong>{" "}
                  {log.ip_address}
                </p>

                <p>
                  <strong>Timestamp:</strong>{" "}
                  {formatHarareTime(log.timestamp)}
                </p>
              </div>
            ))}
          </div>
        )}

        <div className="dashboard-navigation">
  <button
    type="button"
    onClick={() => navigate("/dashboard")}
  >
    Back to Dashboard
  </button>

  <button
    type="button"
    onClick={() => {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      navigate("/login");
    }}
  >
    Logout
  </button>
</div>

      </div>
    </div>
  );
}

export default AuthLogs;
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Protected() {
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async (): Promise<void> => {
      const token = localStorage.getItem("token");

      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const response = await fetch(
          "http://127.0.0.1:5000/protected",
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data: {
          message?: string;
          error?: string;
        } = await response.json();

        if (!response.ok) {
          localStorage.removeItem("token");
          localStorage.removeItem("username");

          setError(data.error ?? "Authentication failed.");

          navigate("/login");
          return;
        }

        setMessage(
          data.message ??
            "Protected content accessed successfully."
        );
      } catch {
        setError(
          "Unable to connect to the backend server."
        );
      } finally {
        setLoading(false);
      }
    };

    void verifyToken();
  }, [navigate]);

  const handleLogout = (): void => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");

    navigate("/login");
  };

  if (loading) {
    return (
      <div className="app">
        <div className="register-container">
          <h2>Loading...</h2>
          <p>Verifying your authentication token.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="register-container">
        <h1>Security Monitoring</h1>

        <h2>Protected Area</h2>

        {message && (
          <p className="success-message">
            {message}
          </p>
        )}

        {error && (
          <p className="error-message">
            {error}
          </p>
        )}

        <p>
          Welcome,{" "}
          {localStorage.getItem("username") ?? "Analyst"}.
        </p>

        <button
          type="button"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </div>
  );
}

export default Protected;
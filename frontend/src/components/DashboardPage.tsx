import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface Metrics {
  num_batches: number;
  num_documents: number;
}

const DashboardPage = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        if (!token) {
          navigate("/login");
          return;
        }

        const response = await fetch(
          "http://127.0.0.1:8000/api/v1/dashboard",
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 401) {
          logout();
          navigate("/login");
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const data = await response.json();

        // Adjust depending on backend response structure
        setMetrics(data.data ?? data);
      } catch (err: any) {
        setError(err.message || "Something went wrong");
      }
    };

    fetchMetrics();
  }, [token, navigate, logout]);

  const avg =
    metrics && metrics.num_batches > 0
      ? (metrics.num_documents / metrics.num_batches).toFixed(1)
      : "0";

  return (
    <div className="container fade-in" style={{ padding: "60px 0" }}>
      <div style={{ marginBottom: "60px" }}>
        <h1 style={{ fontSize: "48px", fontWeight: 800 }}>
          Welcome Back
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "18px" }}>
          Here's an overview of your analysis activity.
        </p>
      </div>

      {error && (
        <div
          className="glass"
          style={{
            padding: "20px",
            background: "rgba(239, 68, 68, 0.05)",
            borderRadius: "16px",
            marginBottom: "40px",
          }}
        >
          <p style={{ color: "var(--error)" }}>
            ⚠️ Error: {error}
          </p>
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "32px",
          marginBottom: "60px",
        }}
      >
        <Stat label="Total Batches" value={metrics?.num_batches ?? 0} icon="📦" />
        <Stat label="Documents Analyzed" value={metrics?.num_documents ?? 0} icon="📄" />
        <Stat label="Avg. per Batch" value={avg} icon="📊" />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
          gap: "32px",
        }}
      >
        <Link to="/upload" className="glass card-hover" style={cardStyle}>
          <Icon>📤</Icon>
          <div>
            <h3>Upload Documents</h3>
            <p>Check for plagiarism & AI content</p>
          </div>
        </Link>

        <Link to="/ai-check" className="glass card-hover" style={cardStyle}>
          <Icon>🤖</Icon>
          <div>
            <h3>AI Detection</h3>
            <p>Analyze text for AI authorship</p>
          </div>
        </Link>
      </div>
    </div>
  );
};

const Stat = ({ label, value, icon }: any) => (
  <div className="glass card-hover" style={{ padding: "32px", position: "relative" }}>
    <div
      style={{
        position: "absolute",
        top: "-10px",
        right: "-10px",
        fontSize: "80px",
        opacity: 0.05,
      }}
    >
      {icon}
    </div>
    <h3 style={{ fontSize: "14px", opacity: 0.7 }}>{label}</h3>
    <p style={{ fontSize: "48px", fontWeight: 800 }}>{value}</p>
  </div>
);

const Icon = ({ children }: any) => (
  <div
    style={{
      fontSize: "40px",
      width: "80px",
      height: "80px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    {children}
  </div>
);

const cardStyle = {
  textDecoration: "none",
  color: "inherit",
  padding: "40px",
  display: "flex",
  alignItems: "center",
  gap: "24px",
};

export default DashboardPage;

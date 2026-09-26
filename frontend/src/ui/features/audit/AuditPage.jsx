import { useState } from "react";
import { analyzeRepo } from "../../../infrastructure/api/auditApi";

const SEVERITY_STYLES = {
  critical: { bg: "#fff0f0", border: "#f87171", badge: "#dc2626" },
  high:     { bg: "#fff7ed", border: "#fb923c", badge: "#ea580c" },
  medium:   { bg: "#fefce8", border: "#facc15", badge: "#ca8a04" },
  low:      { bg: "#f0fdf4", border: "#86efac", badge: "#16a34a" },
};

function SeverityBadge({ severity }) {
  const s = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.low;
  return (
    <span
      style={{
        backgroundColor: s.badge,
        color: "#fff",
        fontSize: "0.7rem",
        fontWeight: 700,
        letterSpacing: "0.05em",
        textTransform: "uppercase",
        padding: "2px 8px",
        borderRadius: "999px",
      }}
    >
      {severity}
    </span>
  );
}

function LeakCard({ leak }) {
  const s = SEVERITY_STYLES[leak.severity] ?? SEVERITY_STYLES.low;
  return (
    <div
      style={{
        backgroundColor: s.bg,
        border: `1px solid ${s.border}`,
        borderRadius: "8px",
        padding: "14px 16px",
        display: "flex",
        flexDirection: "column",
        gap: "6px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <SeverityBadge severity={leak.severity} />
        <code style={{ fontSize: "0.85rem", color: "#374151", fontWeight: 600 }}>
          {leak.file}
          {leak.line != null && (
            <span style={{ color: "#6b7280", fontWeight: 400 }}>:{leak.line}</span>
          )}
        </code>
      </div>
      <p style={{ margin: 0, fontSize: "0.875rem", color: "#4b5563", lineHeight: 1.5 }}>
        {leak.description}
      </p>
    </div>
  );
}

export default function AuditPage() {
  const [repoUrl, setRepoUrl]   = useState("");
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!repoUrl.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const data = await analyzeRepo(repoUrl.trim());
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f7f8fa", padding: "48px 16px", fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif' }}>
      <div style={{ maxWidth: "720px", margin: "0 auto" }}>

        {/* Header */}
        <div style={{ marginBottom: "36px" }}>
          <h1 style={{ margin: "0 0 6px", fontSize: "1.75rem", fontWeight: 700, color: "#1f2328" }}>
            RepoDoc
          </h1>
          <p style={{ margin: 0, color: "#57606a", fontSize: "0.95rem" }}>
            Intelligent repo onboarding &amp; state leak auditing
          </p>
        </div>

        {/* Input form */}
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", gap: "10px", marginBottom: "32px" }}
        >
          <input
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/owner/repository"
            required
            disabled={loading}
            style={{
              flex: 1,
              padding: "10px 14px",
              fontSize: "0.95rem",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              outline: "none",
              backgroundColor: loading ? "#f3f4f6" : "#fff",
              color: "#1f2328",
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px 22px",
              fontSize: "0.9rem",
              fontWeight: 600,
              color: "#fff",
              backgroundColor: loading ? "#93c5fd" : "#3b82d4",
              border: "none",
              borderRadius: "8px",
              cursor: loading ? "not-allowed" : "pointer",
              whiteSpace: "nowrap",
              transition: "background-color 0.15s",
            }}
          >
            {loading ? "Analyzing…" : "Analyze Repo"}
          </button>
        </form>

        {/* Loading indicator */}
        {loading && (
          <div style={{ textAlign: "center", color: "#57606a", fontSize: "0.9rem", padding: "24px 0" }}>
            <div style={{ marginBottom: "8px", fontSize: "1.4rem" }}>⏳</div>
            Running analysis — this may take a moment…
          </div>
        )}

        {/* Error state */}
        {error && (
          <div style={{ backgroundColor: "#fff0f0", border: "1px solid #f87171", borderRadius: "8px", padding: "14px 16px", color: "#b91c1c", fontSize: "0.9rem" }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>

            {/* Architecture summary */}
            <section style={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px", padding: "20px 22px" }}>
              <h2 style={{ margin: "0 0 12px", fontSize: "1rem", fontWeight: 700, color: "#1f2328" }}>
                Architecture Summary
              </h2>
              <p style={{ margin: 0, color: "#4b5563", lineHeight: 1.7, fontSize: "0.9rem" }}>
                {result.architecture_summary}
              </p>
            </section>

            {/* State leaks */}
            <section>
              <h2 style={{ margin: "0 0 14px", fontSize: "1rem", fontWeight: 700, color: "#1f2328" }}>
                State Leaks
                <span style={{ marginLeft: "8px", fontSize: "0.8rem", fontWeight: 500, color: "#57606a" }}>
                  ({result.state_leaks.length} found)
                </span>
              </h2>
              {result.state_leaks.length === 0 ? (
                <p style={{ color: "#57606a", fontSize: "0.9rem" }}>No state leaks detected.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {result.state_leaks.map((leak, i) => (
                    <LeakCard key={i} leak={leak} />
                  ))}
                </div>
              )}
            </section>

          </div>
        )}
      </div>
    </div>
  );
}

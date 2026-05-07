import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { searchJobs, getRecentJobs } from "../api";

const C = {
  bg: "#0a0a0a",
  surface: "#111",
  border: "#1e1e1e",
  accent: "#e8ff47",
  accentDim: "rgba(232,255,71,0.08)",
  text: "#e8e8e8",
  muted: "#555",
  mono: "'DM Mono', monospace",
  sans: "'DM Sans', sans-serif",
};

const pill = (color) => ({
  display: "inline-block",
  padding: "2px 10px",
  borderRadius: "99px",
  fontSize: "11px",
  fontFamily: C.mono,
  fontWeight: "500",
  background: color === "green" ? "rgba(74,222,128,0.1)" : color === "yellow" ? "rgba(232,255,71,0.1)" : "rgba(255,107,107,0.1)",
  color: color === "green" ? "#4ade80" : color === "yellow" ? "#e8ff47" : "#ff6b6b",
  border: `1px solid ${color === "green" ? "rgba(74,222,128,0.2)" : color === "yellow" ? "rgba(232,255,71,0.2)" : "rgba(255,107,107,0.2)"}`,
});

function ScoreBadge({ score }) {
  const color = score >= 70 ? "green" : score >= 40 ? "yellow" : "red";
  return <span style={pill(color)}>{score}/100</span>;
}

function NavBar({ onLogout }) {
  return (
    <nav style={{
      background: "#0d0d0d",
      borderBottom: `1px solid ${C.border}`,
      padding: "0 24px",
      height: "52px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      position: "sticky",
      top: 0,
      zIndex: 10,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div style={{ background: C.accent, borderRadius: "6px", width: "24px", height: "24px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "13px" }}>⚡</div>
        <span style={{ fontFamily: C.mono, color: C.text, fontSize: "15px", fontWeight: "500" }}>JobRadar</span>
      </div>
      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
        <Link to="/settings" style={{
          color: C.muted, fontSize: "13px", textDecoration: "none",
          fontFamily: C.mono, padding: "6px 12px", borderRadius: "6px",
          border: `1px solid ${C.border}`,
        }}>settings</Link>
        <button onClick={onLogout} style={{
          background: "transparent", border: `1px solid ${C.border}`,
          borderRadius: "6px", color: C.muted, fontSize: "13px",
          fontFamily: C.mono, padding: "6px 12px", cursor: "pointer",
        }}>logout</button>
      </div>
    </nav>
  );
}

function SearchForm({ onResults, onLoading }) {
  const [form, setForm] = useState({
    role: "Product Manager",
    years_exp: "",
    domain: "",
    location: "India",
    time_filter: "24h",
    limit: 10,
  });
  const [running, setRunning] = useState(false);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  async function handleRun(e) {
    e.preventDefault();
    setRunning(true);
    onLoading(true);
    try {
      const res = await searchJobs({ ...form, years_exp: Number(form.years_exp) });
      onResults(res.data);
    } catch (err) {
      onResults({ error: err.response?.data?.detail || "Search failed" });
    } finally {
      setRunning(false);
      onLoading(false);
    }
  }

  const inputStyle = {
    width: "100%",
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: "7px",
    padding: "10px 12px",
    color: C.text,
    fontSize: "13px",
    fontFamily: C.sans,
    outline: "none",
    boxSizing: "border-box",
  };

  const labelStyle = {
    display: "block",
    color: C.muted,
    fontSize: "10px",
    fontFamily: C.mono,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginBottom: "6px",
  };

  const fieldStyle = { marginBottom: "16px" };

  return (
    <div style={{
      background: C.surface,
      border: `1px solid ${C.border}`,
      borderRadius: "12px",
      padding: "24px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "24px" }}>
        <span style={{ fontFamily: C.mono, color: C.accent, fontSize: "11px" }}>// search</span>
      </div>

      <form onSubmit={handleRun}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" }}>
          <div style={fieldStyle}>
            <label style={labelStyle}>Role *</label>
            <input style={inputStyle} value={form.role}
              onChange={e => set("role", e.target.value)} placeholder="Product Manager" required />
          </div>

          <div style={fieldStyle}>
            <label style={labelStyle}>Years of Experience *</label>
            <input style={inputStyle} type="number" min="0" max="40"
              value={form.years_exp} onChange={e => set("years_exp", e.target.value)}
              placeholder="e.g. 5" required />
          </div>

          <div style={fieldStyle}>
            <label style={labelStyle}>Domain</label>
            <input style={inputStyle} value={form.domain}
              onChange={e => set("domain", e.target.value)} placeholder="e.g. fintech, saas" />
          </div>

          <div style={fieldStyle}>
            <label style={labelStyle}>Location</label>
            <input style={inputStyle} value={form.location}
              onChange={e => set("location", e.target.value)} placeholder="India" />
          </div>

          <div style={fieldStyle}>
            <label style={labelStyle}>Time Window *</label>
            <select style={{ ...inputStyle, cursor: "pointer" }}
              value={form.time_filter} onChange={e => set("time_filter", e.target.value)}>
              <option value="24h">Last 24 hours</option>
              <option value="1w">Last week</option>
              <option value="1m">Last month</option>
            </select>
          </div>

          <div style={fieldStyle}>
            <label style={labelStyle}>Max Results</label>
            <select style={{ ...inputStyle, cursor: "pointer" }}
              value={form.limit} onChange={e => set("limit", Number(e.target.value))}>
              <option value={10}>10 jobs</option>
              <option value={20}>20 jobs</option>
              <option value={50}>50 jobs</option>
            </select>
          </div>
        </div>

        <button type="submit" disabled={running} style={{
          width: "100%",
          background: running ? "#1a1a1a" : C.accent,
          color: running ? C.muted : "#0a0a0a",
          border: "none",
          borderRadius: "8px",
          padding: "12px",
          fontSize: "13px",
          fontWeight: "600",
          fontFamily: C.mono,
          cursor: running ? "not-allowed" : "pointer",
          transition: "all 0.15s",
          marginTop: "4px",
        }}>
          {running ? "// searching linkedin..." : "run_search()"}
        </button>
      </form>
    </div>
  );
}

function JobCard({ job, match }) {
  const [expanded, setExpanded] = useState(false);
  const score = match?.score ?? 0;
  const reasons = match?.reasons ?? [];
  const warnings = match?.warnings ?? [];
  const req = match?.extracted_requirements ?? {};

  return (
    <div style={{
      background: C.surface,
      border: `1px solid ${C.border}`,
      borderRadius: "10px",
      padding: "18px 20px",
      transition: "border-color 0.15s",
    }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "#333"}
      onMouseLeave={e => e.currentTarget.style.borderColor = C.border}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", marginBottom: "4px" }}>
            <ScoreBadge score={score} />
            {req.remote_friendly && (
              <span style={{ ...pill("green"), fontSize: "10px" }}>remote</span>
            )}
          </div>
          <h3 style={{ color: C.text, fontSize: "15px", fontWeight: "600", margin: "6px 0 2px", lineHeight: 1.3 }}>
            {job.title}
          </h3>
          <p style={{ color: C.muted, fontSize: "13px", margin: 0, fontFamily: C.mono }}>
            {job.company} · {job.location}
          </p>
        </div>

        <div style={{ display: "flex", gap: "8px", flexShrink: 0 }}>
          <a href={job.link} target="_blank" rel="noreferrer" style={{
            background: C.accentDim,
            border: `1px solid rgba(232,255,71,0.15)`,
            color: C.accent,
            borderRadius: "7px",
            padding: "7px 14px",
            fontSize: "12px",
            fontFamily: C.mono,
            textDecoration: "none",
            whiteSpace: "nowrap",
          }}>apply →</a>
          <button onClick={() => setExpanded(x => !x)} style={{
            background: "transparent",
            border: `1px solid ${C.border}`,
            borderRadius: "7px",
            padding: "7px 10px",
            color: C.muted,
            fontSize: "12px",
            fontFamily: C.mono,
            cursor: "pointer",
          }}>{expanded ? "▲" : "▼"}</button>
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: "16px", paddingTop: "16px", borderTop: `1px solid ${C.border}` }}>
          {req.min_years_experience !== null && (
            <div style={{ marginBottom: "12px" }}>
              <span style={{ ...labelMini }}>JD requires</span>
              <span style={{ color: C.text, fontSize: "13px", fontFamily: C.mono }}>
                {req.min_years_experience}{req.max_years_experience ? `–${req.max_years_experience}` : "+"} yrs
                {req.seniority_level !== "unknown" && ` · ${req.seniority_level}`}
              </span>
            </div>
          )}

          {req.domains?.length > 0 && (
            <div style={{ marginBottom: "12px" }}>
              <span style={labelMini}>domains</span>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
                {req.domains.map(d => (
                  <span key={d} style={{
                    background: "#1a1a1a", border: `1px solid ${C.border}`,
                    borderRadius: "5px", padding: "2px 8px", color: "#888",
                    fontSize: "11px", fontFamily: C.mono,
                  }}>{d}</span>
                ))}
              </div>
            </div>
          )}

          {reasons.length > 0 && (
            <div style={{ marginBottom: "12px" }}>
              <span style={labelMini}>why it matched</span>
              {reasons.map((r, i) => (
                <div key={i} style={{ color: "#4ade80", fontSize: "12px", fontFamily: C.mono, marginTop: "3px" }}>
                  ✓ {r}
                </div>
              ))}
            </div>
          )}

          {warnings.length > 0 && (
            <div>
              <span style={labelMini}>warnings</span>
              {warnings.map((w, i) => (
                <div key={i} style={{ color: "#f59e0b", fontSize: "12px", fontFamily: C.mono, marginTop: "3px" }}>
                  ⚠ {w}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const labelMini = {
  display: "block",
  color: C.muted,
  fontSize: "10px",
  fontFamily: C.mono,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  marginBottom: "4px",
};

export default function Dashboard() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recentJobs, setRecentJobs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getRecentJobs().then(r => setRecentJobs(r.data || [])).catch(() => {});
  }, []);

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  const jobs = results?.jobs || [];
  const hasError = results?.error;

  return (
    <div style={{ background: C.bg, minHeight: "100vh", fontFamily: C.sans }}>
      <NavBar onLogout={handleLogout} />

      <div style={{ maxWidth: "900px", margin: "0 auto", padding: "32px 24px" }}>

        {/* Header */}
        <div style={{ marginBottom: "32px" }}>
          <h1 style={{ color: C.text, fontSize: "24px", fontWeight: "600", margin: "0 0 6px" }}>
            Job Search
          </h1>
          <p style={{ color: C.muted, fontSize: "13px", fontFamily: C.mono, margin: 0 }}>
            // searches linkedin · filters by experience · sends email alerts
          </p>
        </div>

        <SearchForm onResults={setResults} onLoading={setLoading} />

        {/* Loading state */}
        {loading && (
          <div style={{
            marginTop: "24px", padding: "32px",
            background: C.surface, border: `1px solid ${C.border}`,
            borderRadius: "12px", textAlign: "center",
          }}>
            <div style={{ color: C.accent, fontFamily: C.mono, fontSize: "13px", marginBottom: "8px" }}>
              searching linkedin...
            </div>
            <div style={{ color: C.muted, fontFamily: C.mono, fontSize: "11px" }}>
              fetching JDs · running LLM analysis · this takes ~30s
            </div>
          </div>
        )}

        {/* Error */}
        {hasError && !loading && (
          <div style={{
            marginTop: "24px", padding: "16px 20px",
            background: "#120808", border: "1px solid #2a1010",
            borderRadius: "10px", color: "#ff6b6b",
            fontFamily: C.mono, fontSize: "13px",
          }}>
            ⚠ {results.error}
          </div>
        )}

        {/* Results */}
        {!loading && jobs.length > 0 && (
          <div style={{ marginTop: "24px" }}>
            <div style={{
              display: "flex", justifyContent: "space-between",
              alignItems: "center", marginBottom: "16px",
            }}>
              <span style={{ color: C.muted, fontFamily: C.mono, fontSize: "12px" }}>
                {jobs.length} job{jobs.length !== 1 ? "s" : ""} found
              </span>
              <span style={{ color: C.muted, fontFamily: C.mono, fontSize: "12px" }}>
                sorted by match score
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {[...jobs].sort((a, b) => (b.match?.score ?? 0) - (a.match?.score ?? 0))
                .map(item => (
                  <JobCard key={item.job?.job_id || Math.random()}
                    job={item.job || item} match={item.match || item} />
                ))}
            </div>
          </div>
        )}

        {!loading && results && jobs.length === 0 && !hasError && (
          <div style={{
            marginTop: "24px", padding: "40px",
            background: C.surface, border: `1px solid ${C.border}`,
            borderRadius: "12px", textAlign: "center",
          }}>
            <div style={{ color: C.muted, fontFamily: C.mono, fontSize: "13px" }}>
              // no matching jobs found · try a wider time window or different role
            </div>
          </div>
        )}

        {/* Recent sent jobs */}
        {recentJobs.length > 0 && !results && (
          <div style={{ marginTop: "32px" }}>
            <div style={{ color: C.muted, fontFamily: C.mono, fontSize: "11px", marginBottom: "12px", letterSpacing: "0.08em" }}>
              // RECENTLY EMAILED
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {recentJobs.slice(0, 5).map(j => (
                <div key={j.job_id} style={{
                  background: C.surface, border: `1px solid ${C.border}`,
                  borderRadius: "8px", padding: "12px 16px",
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                }}>
                  <div>
                    <span style={{ color: C.text, fontSize: "13px" }}>{j.title}</span>
                    <span style={{ color: C.muted, fontSize: "12px", fontFamily: C.mono, marginLeft: "8px" }}>
                      {j.company}
                    </span>
                  </div>
                  <span style={{ color: "#333", fontSize: "11px", fontFamily: C.mono }}>
                    {new Date(j.sent_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
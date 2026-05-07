import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getConfig, saveConfig } from "../api";

const C = {
  bg: "#0a0a0a",
  surface: "#111",
  border: "#1e1e1e",
  accent: "#e8ff47",
  text: "#e8e8e8",
  muted: "#555",
  mono: "'DM Mono', monospace",
  sans: "'DM Sans', sans-serif",
};

const inputStyle = {
  width: "100%",
  background: "#0d0d0d",
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
  marginBottom: "7px",
};

function Section({ title, comment, children }) {
  return (
    <div style={{
      background: C.surface,
      border: `1px solid ${C.border}`,
      borderRadius: "12px",
      padding: "24px",
      marginBottom: "16px",
    }}>
      <div style={{ marginBottom: "20px" }}>
        <h2 style={{ color: C.text, fontSize: "15px", fontWeight: "600", margin: "0 0 4px" }}>{title}</h2>
        <span style={{ color: C.muted, fontSize: "11px", fontFamily: C.mono }}>{comment}</span>
      </div>
      {children}
    </div>
  );
}

export default function Settings() {
  const [config, setConfig] = useState({
    role: "Product Manager",
    years_exp: "",
    domain: "",
    location: "India",
    time_filter: "24h",
    notify_email: "",
    schedule_interval: "1h",
  });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [focusedField, setFocusedField] = useState(null);

  useEffect(() => {
    getConfig()
      .then(r => { if (r.data) setConfig(c => ({ ...c, ...r.data })); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const set = (k, v) => setConfig(c => ({ ...c, [k]: v }));

  async function handleSave(e) {
    e.preventDefault();
    setError("");
    try {
      await saveConfig({ ...config, years_exp: Number(config.years_exp) });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save settings");
    }
  }

  const focusedInput = (name) => ({
    ...inputStyle,
    borderColor: focusedField === name ? C.accent : C.border,
  });

  const fieldProps = (name) => ({
    onFocus: () => setFocusedField(name),
    onBlur: () => setFocusedField(null),
  });

  const field = (name) => ({ style: focusedInput(name), ...fieldProps(name) });

  if (loading) return (
    <div style={{ background: C.bg, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ color: C.muted, fontFamily: C.mono, fontSize: "13px" }}>loading config...</span>
    </div>
  );

  return (
    <div style={{ background: C.bg, minHeight: "100vh", fontFamily: C.sans }}>

      {/* Nav */}
      <nav style={{
        background: "#0d0d0d", borderBottom: `1px solid ${C.border}`,
        padding: "0 24px", height: "52px", display: "flex",
        alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ background: C.accent, borderRadius: "6px", width: "24px", height: "24px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "13px" }}>⚡</div>
          <span style={{ fontFamily: C.mono, color: C.text, fontSize: "15px", fontWeight: "500" }}>JobRadar</span>
        </div>
        <Link to="/" style={{
          color: C.muted, fontSize: "13px", textDecoration: "none",
          fontFamily: C.mono, padding: "6px 12px", borderRadius: "6px",
          border: `1px solid ${C.border}`,
        }}>← dashboard</Link>
      </nav>

      <div style={{ maxWidth: "680px", margin: "0 auto", padding: "32px 24px" }}>

        <div style={{ marginBottom: "32px" }}>
          <h1 style={{ color: C.text, fontSize: "24px", fontWeight: "600", margin: "0 0 6px" }}>Settings</h1>
          <p style={{ color: C.muted, fontSize: "13px", fontFamily: C.mono, margin: 0 }}>
            // configure your search agent
          </p>
        </div>

        {error && (
          <div style={{
            background: "#120808", border: "1px solid #2a1010",
            borderRadius: "8px", padding: "12px 16px",
            color: "#ff6b6b", fontFamily: C.mono, fontSize: "13px", marginBottom: "20px",
          }}>⚠ {error}</div>
        )}

        <form onSubmit={handleSave}>

          <Section title="Search Preferences" comment="// default values used for scheduled runs">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" }}>
              <div style={{ marginBottom: "16px" }}>
                <label style={labelStyle}>Job Role *</label>
                <input value={config.role} onChange={e => set("role", e.target.value)}
                  placeholder="Product Manager" required {...field("role")} />
              </div>
              <div style={{ marginBottom: "16px" }}>
                <label style={labelStyle}>Years of Experience *</label>
                <input type="number" min="0" max="40" value={config.years_exp}
                  onChange={e => set("years_exp", e.target.value)}
                  placeholder="e.g. 5" required {...field("years_exp")} />
              </div>
              <div style={{ marginBottom: "16px" }}>
                <label style={labelStyle}>Domain</label>
                <input value={config.domain} onChange={e => set("domain", e.target.value)}
                  placeholder="e.g. fintech, saas" {...field("domain")} />
              </div>
              <div style={{ marginBottom: "16px" }}>
                <label style={labelStyle}>Location</label>
                <input value={config.location} onChange={e => set("location", e.target.value)}
                  placeholder="India" {...field("location")} />
              </div>
              <div style={{ marginBottom: "0" }}>
                <label style={labelStyle}>Time Window</label>
                <select value={config.time_filter} onChange={e => set("time_filter", e.target.value)}
                  style={{ ...focusedInput("time_filter"), cursor: "pointer" }} {...fieldProps("time_filter")}>
                  <option value="24h">Last 24 hours</option>
                  <option value="1w">Last week</option>
                  <option value="1m">Last month</option>
                </select>
              </div>
            </div>
          </Section>

          <Section title="Email Notifications" comment="// where to send matched jobs">
            <div style={{ marginBottom: "0" }}>
              <label style={labelStyle}>Notify Email *</label>
              <input type="email" value={config.notify_email}
                onChange={e => set("notify_email", e.target.value)}
                placeholder="you@example.com" required {...field("notify_email")} />
              <p style={{ color: "#333", fontSize: "11px", fontFamily: C.mono, margin: "8px 0 0" }}>
                // sender is configured via SMTP settings in backend .env
              </p>
            </div>
          </Section>

          <Section title="Schedule" comment="// how often to run the search automatically">
            <div>
              <label style={labelStyle}>Run every</label>
              <div style={{ display: "flex", gap: "8px" }}>
                {[["15m", "15 min"], ["1h", "1 hour"], ["3h", "3 hours"]].map(([val, label]) => (
                  <button key={val} type="button"
                    onClick={() => set("schedule_interval", val)}
                    style={{
                      flex: 1,
                      background: config.schedule_interval === val ? "rgba(232,255,71,0.08)" : "transparent",
                      border: `1px solid ${config.schedule_interval === val ? "rgba(232,255,71,0.3)" : C.border}`,
                      borderRadius: "7px",
                      padding: "10px",
                      color: config.schedule_interval === val ? C.accent : C.muted,
                      fontSize: "13px",
                      fontFamily: C.mono,
                      cursor: "pointer",
                      transition: "all 0.15s",
                    }}>
                    {label}
                  </button>
                ))}
              </div>
              <p style={{ color: "#333", fontSize: "11px", fontFamily: C.mono, margin: "10px 0 0" }}>
                // only new jobs are emailed — duplicates are tracked in the database
              </p>
            </div>
          </Section>

          <button type="submit" style={{
            width: "100%",
            background: saved ? "rgba(74,222,128,0.1)" : C.accent,
            color: saved ? "#4ade80" : "#0a0a0a",
            border: saved ? "1px solid rgba(74,222,128,0.3)" : "none",
            borderRadius: "8px",
            padding: "13px",
            fontSize: "13px",
            fontWeight: "600",
            fontFamily: C.mono,
            cursor: "pointer",
            transition: "all 0.2s",
          }}>
            {saved ? "✓ saved" : "save_config()"}
          </button>
        </form>
      </div>
    </div>
  );
}
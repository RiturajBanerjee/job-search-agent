import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";
import API from "../api";

const styles = {
  page: {
    minHeight: "100vh",
    background: "#0a0a0a",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "'DM Sans', sans-serif",
    padding: "24px",
  },
  card: { width: "100%", maxWidth: "400px" },
  logoRow: { display: "flex", alignItems: "center", gap: "10px", marginBottom: "48px" },
  logoIcon: {
    width: "32px", height: "32px", background: "#e8ff47",
    borderRadius: "8px", display: "flex", alignItems: "center",
    justifyContent: "center", fontSize: "16px",
  },
  logoText: {
    fontFamily: "'DM Mono', monospace", color: "#fff",
    fontSize: "18px", fontWeight: "500", letterSpacing: "-0.5px",
  },
  heading: { color: "#fff", fontSize: "28px", fontWeight: "600", marginBottom: "8px", lineHeight: 1.2 },
  subheading: { color: "#555", fontSize: "14px", marginBottom: "36px", fontWeight: "400" },
  label: {
    display: "block", color: "#888", fontSize: "11px",
    fontFamily: "'DM Mono', monospace", letterSpacing: "0.08em",
    textTransform: "uppercase", marginBottom: "8px",
  },
  inputGroup: { marginBottom: "20px" },
  button: {
    width: "100%", background: "#e8ff47", color: "#0a0a0a",
    border: "none", borderRadius: "8px", padding: "13px",
    fontSize: "14px", fontWeight: "600", fontFamily: "'DM Sans', sans-serif",
    cursor: "pointer", marginTop: "8px", transition: "opacity 0.15s",
  },
  error: {
    background: "#1a0a0a", border: "1px solid #3a1a1a", borderRadius: "8px",
    padding: "12px 14px", color: "#ff6b6b", fontSize: "13px",
    marginBottom: "20px", fontFamily: "'DM Mono', monospace",
  },
  toggle: {
    color: "#444", fontSize: "12px", textAlign: "center",
    marginTop: "16px", fontFamily: "'DM Mono', monospace",
    cursor: "pointer", background: "none", border: "none",
    width: "100%", padding: "4px",
  },
  hint: {
    color: "#333", fontSize: "12px", textAlign: "center",
    marginTop: "16px", fontFamily: "'DM Mono', monospace",
  },
};

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [focusedField, setFocusedField] = useState(null);
  const navigate = useNavigate();

  const inputStyle = (name) => ({
    width: "100%",
    background: "#141414",
    border: `1px solid ${focusedField === name ? "#e8ff47" : "#222"}`,
    borderRadius: "8px",
    padding: "12px 14px",
    color: "#fff",
    fontSize: "14px",
    fontFamily: "'DM Sans', sans-serif",
    outline: "none",
    boxSizing: "border-box",
    transition: "border-color 0.15s",
  });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      let res;
      if (isRegister) {
        res = await API.post("/auth/register", { email, password });
      } else {
        res = await login(email, password);
      }
      localStorage.setItem("token", res.data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logoRow}>
          <div style={styles.logoIcon}>⚡</div>
          <span style={styles.logoText}>JobRadar</span>
        </div>

        <h1 style={styles.heading}>
          {isRegister ? "Create account" : "Welcome back"}
        </h1>
        <p style={styles.subheading}>
          {isRegister ? "Set up your job search agent" : "Sign in to your job search agent"}
        </p>

        {error && <div style={styles.error}>⚠ {error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input
              style={inputStyle("email")}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setFocusedField("email")}
              onBlur={() => setFocusedField(null)}
              placeholder="you@example.com"
              required
              autoFocus
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input
              style={inputStyle("password")}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setFocusedField("password")}
              onBlur={() => setFocusedField(null)}
              placeholder="••••••••"
              required
            />
          </div>

          <button
            style={{ ...styles.button, opacity: loading ? 0.6 : 1 }}
            type="submit"
            disabled={loading}
          >
            {loading ? "..." : isRegister ? "Create account →" : "Sign in →"}
          </button>

          <button
            type="button"
            style={styles.toggle}
            onClick={() => { setIsRegister((x) => !x); setError(""); }}
          >
            {isRegister
              ? "// already have an account? sign in"
              : "// no account? register"}
          </button>
        </form>

        <p style={styles.hint}>// backend configured via .env</p>
      </div>
    </div>
  );
}
"use client";

import { FormEvent, useState } from "react";
import { useAuth } from "../services/AuthProvider";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await login(email.trim(), password);
      window.location.assign("/");
    } catch (err: any) {
      const status = err?.response?.status;
      const message =
        err?.response?.data?.message ||
        (status === 401
          ? "The email or password is incorrect."
          : "Unable to sign in. Check the authentication service and try again.");
      setError(Array.isArray(message) ? message.join(", ") : String(message));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="gb-login-page">
      <section className="gb-login-card">
        <div className="gb-login-mark">GX</div>
        <p className="gb-login-eyebrow">GENXBABY SECURE ACCESS</p>
        <h1>Admin Control Center</h1>
        <p className="gb-login-description">
          Sign in with your standalone GenXBaby account.
          ADMIN and OWNER roles are permitted.
        </p>

        <form onSubmit={handleSubmit} className="gb-login-form">
          <label htmlFor="admin-email">Email address</label>
          <input
            id="admin-email"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="admin-password">Password</label>
          <input
            id="admin-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error && <p className="gb-login-error" role="alert">{error}</p>}

          <button type="submit" disabled={submitting}>
            {submitting ? "AUTHENTICATING…" : "SIGN IN SECURELY"}
          </button>
        </form>

        <p className="gb-login-footer">
          Authentication provided by GenXBaby standalone identity service.
        </p>
      </section>
    </main>
  );
}

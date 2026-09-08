import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { isApiError, login, setToken } from "../api";
import type { TokenOut } from "../types";

type LoginProps = {
  onAuthed: () => Promise<void>;
};

export default function Login({ onAuthed }: LoginProps) {
  const [email, setEmail] = useState("viewer@rolekit.dev");
  const [password, setPassword] = useState("viewerpass");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data: TokenOut = await login(email, password);
      setToken(data.access_token);
      await onAuthed();
      navigate("/documents");
    } catch (err) {
      setError(isApiError(err) && err.status === 401 ? "Invalid credentials" : err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth">
      <div className="card">
        <p className="kicker">Named roles, not a product</p>
        <h1>RoleKit</h1>
        <p className="lede">
          The JWT only carries your user id. Checkboxes never authorize anything by themselves.
        </p>
        <form onSubmit={onSubmit}>
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="username" />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>
          {error && <p className="banner error">{error}</p>}
          <button type="submit" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <dl className="hints">
          <div>
            <dt>viewer@rolekit.dev</dt>
            <dd>viewerpass — GET only</dd>
          </div>
          <div>
            <dt>editor@rolekit.dev</dt>
            <dd>editorpass — no delete</dd>
          </div>
          <div>
            <dt>admin@rolekit.dev</dt>
            <dd>adminpass — roles UI, no document codes</dd>
          </div>
        </dl>
      </div>
    </main>
  );
}

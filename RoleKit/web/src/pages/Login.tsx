/**
 * Login.tsx — store the JWT, then go to documents.
 * Create account hits POST /auth/register; the first user in an empty DB is admin.
 */
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, isApiError, login, setToken } from "../api";

type LoginProps = {
  onAuthed: () => Promise<void>;
};

export default function Login({ onAuthed }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function afterToken(token: string) {
    setToken(token);
    await onAuthed();
    navigate("/documents");
  }

  async function onLogin(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { data } = await login(email, password);
      await afterToken(data.access_token);
    } catch (err) {
      setError(isApiError(err) && err.status === 401 ? "Invalid credentials" : err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  async function onRegister() {
    setError("");
    setBusy(true);
    try {
      await api("/auth/register", { method: "POST", body: { email, password } });
      const { data } = await login(email, password);
      await afterToken(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth">
      <div className="card">
        <p className="kicker">Named roles</p>
        <h1>RoleKit</h1>
        <p className="lede">
          JWT only stores your user id. First account is admin. Then create a role, tick codes, and
          assign it.
        </p>
        <form onSubmit={onLogin}>
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
          <div className="row">
            <button type="submit" disabled={busy}>
              Sign in
            </button>
            <button type="button" className="ghost" disabled={busy} onClick={() => void onRegister()}>
              Create account
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}

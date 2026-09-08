import { useEffect, useState, type ReactNode } from "react";
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { api, clearToken, getToken } from "./api";
import Audit from "./pages/Audit";
import Documents from "./pages/Documents";
import Login from "./pages/Login";
import Roles from "./pages/Roles";
import Users from "./pages/Users";
import type { UserMe } from "./types";

function Protected({ me, children }: { me: UserMe | null; children: ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  if (!me) return <div className="page muted">Loading session…</div>;
  return children;
}

export default function App() {
  const [me, setMe] = useState<UserMe | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  async function loadMe() {
    if (!getToken()) {
      setMe(null);
      return;
    }
    try {
      const { data } = await api<UserMe>("/me");
      setMe(data);
    } catch {
      clearToken();
      setMe(null);
    }
  }

  useEffect(() => {
    void loadMe();
  }, [location.pathname]);

  function logout() {
    clearToken();
    setMe(null);
    navigate("/login");
  }

  return (
    <div className="shell">
      {getToken() && me && (
        <header className="topbar">
          <Link to="/documents" className="brand">
            RoleKit
          </Link>
          <nav>
            <Link to="/documents">Documents</Link>
            <Link to="/audit">Audit</Link>
            {me.is_admin && <Link to="/roles">Roles</Link>}
            {me.is_admin && <Link to="/users">Users</Link>}
          </nav>
          <div className="who">
            <span>{me.email}</span>
            {me.is_admin && <em>admin</em>}
            <button type="button" className="ghost" onClick={logout}>
              Log out
            </button>
          </div>
        </header>
      )}

      <Routes>
        <Route path="/login" element={<Login onAuthed={loadMe} />} />
        <Route
          path="/documents"
          element={
            <Protected me={me}>
              {me && <Documents me={me} />}
            </Protected>
          }
        />
        <Route
          path="/audit"
          element={
            <Protected me={me}>
              <Audit />
            </Protected>
          }
        />
        <Route
          path="/roles"
          element={
            <Protected me={me}>
              {me?.is_admin ? <Roles /> : <Navigate to="/documents" replace />}
            </Protected>
          }
        />
        <Route
          path="/users"
          element={
            <Protected me={me}>
              {me?.is_admin ? <Users /> : <Navigate to="/documents" replace />}
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to={getToken() ? "/documents" : "/login"} replace />} />
      </Routes>
    </div>
  );
}

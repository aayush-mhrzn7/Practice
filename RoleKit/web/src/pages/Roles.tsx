/**
 * Roles.tsx — permission matrix.
 * Checkboxes map to frozen codes. Save sends the full checked list
 * (PATCH /roles/{id} { name, permissions }). Uncheck = omit from that list.
 */
import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { RoleOut } from "../types";

const ALL_CODES = [
  "documents:write",
  "documents:edit",
  "documents:delete",
  "documents:read",
  "audit:read",
];

function emptyChecks() {
  return {
    "documents:write": false,
    "documents:edit": false,
    "documents:delete": false,
    "documents:read": false,
    "audit:read": false,
  };
}

function fail(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function Roles() {
  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [roleId, setRoleId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [checks, setChecks] = useState(emptyChecks());
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const { data } = await api<RoleOut[]>("/roles");
    setRoles(data);
  }

  useEffect(() => {
    load().catch((err: unknown) => setError(fail(err)));
  }, []);

  function editRole(role: RoleOut) {
    const next = emptyChecks();
    for (const code of role.permissions) {
      if (code in next) next[code as keyof typeof next] = true;
    }
    setRoleId(role.id);
    setName(role.name);
    setChecks(next);
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    const permissions = ALL_CODES.filter((code) => checks[code as keyof typeof checks]);
    try {
      let id = roleId;
      if (!id) {
        const created = await api<RoleOut>("/roles", { method: "POST", body: { name } });
        id = created.data.id;
      }
      await api(`/roles/${id}`, { method: "PATCH", body: { name, permissions } });
      setNotice("Saved.");
      setRoleId(null);
      setName("");
      setChecks(emptyChecks());
      await load();
    } catch (err) {
      setError(fail(err));
    }
  }

  return (
    <main className="page wide">
      <h1>Roles</h1>
      <p className="lede">
        Name a role, tick cells, save. Create is <code>documents:write</code>, update is{" "}
        <code>documents:edit</code>. Audit only has read.
      </p>
      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}

      <form className="card form-grid" onSubmit={save}>
        <h2>{roleId ? "Edit role" : "New role"}</h2>
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="viewer" required />
        </label>
        <div className="table-wrap">
          <table className="perm-table">
            <thead>
              <tr>
                <th>Resource</th>
                <th>Create</th>
                <th>Update</th>
                <th>Delete</th>
                <th>Read</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Documents</th>
                <td>
                  <input
                    type="checkbox"
                    checked={checks["documents:write"]}
                    onChange={(e) => setChecks({ ...checks, "documents:write": e.target.checked })}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={checks["documents:edit"]}
                    onChange={(e) => setChecks({ ...checks, "documents:edit": e.target.checked })}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={checks["documents:delete"]}
                    onChange={(e) => setChecks({ ...checks, "documents:delete": e.target.checked })}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={checks["documents:read"]}
                    onChange={(e) => setChecks({ ...checks, "documents:read": e.target.checked })}
                  />
                </td>
              </tr>
              <tr>
                <th scope="row">Audit</th>
                <td className="muted">—</td>
                <td className="muted">—</td>
                <td className="muted">—</td>
                <td>
                  <input
                    type="checkbox"
                    checked={checks["audit:read"]}
                    onChange={(e) => setChecks({ ...checks, "audit:read": e.target.checked })}
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="row">
          <button type="submit">Save</button>
          {roleId && (
            <button
              type="button"
              className="ghost"
              onClick={() => {
                setRoleId(null);
                setName("");
                setChecks(emptyChecks());
              }}
            >
              New role
            </button>
          )}
        </div>
      </form>

      <ul className="doc-list">
        {roles.map((role) => (
          <li key={role.id} className="card row-between">
            <div>
              <h2>{role.name}</h2>
              <p className="muted">{role.permissions.join(", ") || "no codes"}</p>
            </div>
            <button type="button" className="ghost" onClick={() => editRole(role)}>
              Edit
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

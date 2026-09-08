import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { RoleOut, UserList } from "../types";

function failMessage(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function Users() {
  const [users, setUsers] = useState<UserList[]>([]);
  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [userId, setUserId] = useState("");
  const [checked, setChecked] = useState<Record<number, boolean>>({});
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const [usersRes, rolesRes] = await Promise.all([
      api<UserList[]>("/users"),
      api<RoleOut[]>("/roles"),
    ]);
    setUsers(usersRes.data);
    setRoles(rolesRes.data);
    if (!userId && usersRes.data[0]) {
      setUserId(String(usersRes.data[0].id));
    }
  }

  useEffect(() => {
    load().catch((err: unknown) => setError(failMessage(err)));
  }, []);

  useEffect(() => {
    if (!userId || !users.length) return;
    const user = users.find((u) => String(u.id) === userId);
    if (!user) return;
    const next: Record<number, boolean> = {};
    for (const role of roles) next[role.id] = user.roles.some((r) => r.id === role.id);
    setChecked(next);
  }, [userId, users, roles]);

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    const user = users.find((u) => String(u.id) === userId);
    if (!user) return;
    const current = new Set(user.roles.map((r) => r.id));
    const desired = new Set(
      Object.entries(checked)
        .filter(([, on]) => on)
        .map(([id]) => Number(id)),
    );
    try {
      for (const id of desired) {
        if (!current.has(id)) {
          await api(`/users/${user.id}/roles/${id}`, { method: "POST" });
        }
      }
      for (const id of current) {
        if (!desired.has(id)) {
          await api(`/users/${user.id}/roles/${id}`, { method: "DELETE" });
        }
      }
      setNotice(`Updated roles for ${user.email}. Next request reloads codes from SQL.`);
      await load();
    } catch (err) {
      setError(failMessage(err));
    }
  }

  const selected = users.find((u) => String(u.id) === userId);

  return (
    <main className="page">
      <h1>Users</h1>
      <p className="lede">
        Grant and revoke means attach or detach a <code>user_roles</code> row. The token stays
        valid; the next request must fail if you revoke.
      </p>
      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}

      <form className="card form-grid" onSubmit={save}>
        <label>
          User
          <select value={userId} onChange={(e) => setUserId(e.target.value)}>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.email}
                {user.is_admin ? " (admin)" : ""}
              </option>
            ))}
          </select>
        </label>
        <fieldset className="checks">
          <legend>Roles {selected ? `for ${selected.email}` : ""}</legend>
          {roles.map((role) => (
            <label key={role.id} className="check">
              <input
                type="checkbox"
                checked={Boolean(checked[role.id])}
                onChange={(e) => setChecked({ ...checked, [role.id]: e.target.checked })}
              />
              {role.name}
              <span className="muted">{role.permissions.join(", ") || "no codes"}</span>
            </label>
          ))}
        </fieldset>
        <button type="submit">Save grants</button>
      </form>
    </main>
  );
}

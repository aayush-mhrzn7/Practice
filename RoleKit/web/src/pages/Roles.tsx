import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { PermissionGroup, RoleOut } from "../types";

type Verb = "create" | "update" | "delete" | "read";

const COLUMNS: Verb[] = ["create", "update", "delete", "read"];

type RoleForm = {
  id: number | null;
  name: string;
  checks: Record<string, boolean>;
};

function verbOf(code: string): Verb | null {
  const suffix = code.split(":")[1];
  if (suffix === "write") return "create";
  if (suffix === "edit") return "update";
  if (suffix === "delete" || suffix === "read") return suffix;
  return null;
}

function codesByVerb(group: PermissionGroup): Partial<Record<Verb, string>> {
  const map: Partial<Record<Verb, string>> = {};
  for (const item of group.permissions) {
    const verb = verbOf(item.code);
    if (verb) map[verb] = item.code;
  }
  return map;
}

function emptyChecks(groups: PermissionGroup[]): Record<string, boolean> {
  const checks: Record<string, boolean> = {};
  for (const group of groups) {
    for (const item of group.permissions) checks[item.code] = false;
  }
  return checks;
}

function failMessage(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function Roles() {
  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [groups, setGroups] = useState<PermissionGroup[]>([]);
  const [form, setForm] = useState<RoleForm>({ id: null, name: "", checks: {} });
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const [rolesRes, catalogRes] = await Promise.all([
      api<RoleOut[]>("/roles"),
      api<PermissionGroup[]>("/permissions"),
    ]);
    setRoles(rolesRes.data);
    setGroups(catalogRes.data);
    setForm((current) => ({
      ...current,
      checks: { ...emptyChecks(catalogRes.data), ...current.checks },
    }));
  }

  useEffect(() => {
    load().catch((err: unknown) => setError(failMessage(err)));
  }, []);

  function applyRole(role: RoleOut) {
    const checks = emptyChecks(groups);
    for (const code of role.permissions) checks[code] = true;
    setForm({ id: role.id, name: role.name, checks });
  }

  function toggle(code: string, on: boolean) {
    setForm({ ...form, checks: { ...form.checks, [code]: on } });
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    const permissions = Object.entries(form.checks)
      .filter(([, on]) => on)
      .map(([code]) => code);
    try {
      let roleId = form.id;
      if (!roleId) {
        const created = await api<RoleOut>("/roles", { method: "POST", body: { name: form.name } });
        roleId = created.data.id;
      }
      await api(`/roles/${roleId}`, {
        method: "PATCH",
        body: { name: form.name, permissions },
      });
      setNotice(`Saved ${form.name} with ${permissions.join(", ") || "no codes"}.`);
      setForm({ id: null, name: "", checks: emptyChecks(groups) });
      await load();
    } catch (err) {
      setError(failMessage(err));
    }
  }

  return (
    <main className="page wide">
      <h1>Roles</h1>
      <p className="lede">
        Tick cells in the matrix. Save sends the full set of checked codes. Create maps to{" "}
        <code>:write</code>, update to <code>:edit</code>. Empty cells mean that resource has no
        such code.
      </p>
      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}

      <form className="card form-grid" onSubmit={save}>
        <h2>{form.id ? `Edit ${form.name}` : "New role"}</h2>
        <label>
          Name
          <input
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="night-editor"
            required
          />
        </label>
        <div className="table-wrap">
          <table className="perm-table">
            <thead>
              <tr>
                <th>Resource</th>
                {COLUMNS.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => {
                const verbs = codesByVerb(group);
                return (
                  <tr key={group.key}>
                    <th scope="row">{group.label}</th>
                    {COLUMNS.map((col) => {
                      const code = verbs[col];
                      return (
                        <td key={col}>
                          {code ? (
                            <label className="cell-check">
                              <input
                                type="checkbox"
                                checked={Boolean(form.checks[code])}
                                onChange={(e) => toggle(code, e.target.checked)}
                                aria-label={`${group.label} ${col}`}
                              />
                            </label>
                          ) : (
                            <span className="muted">—</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="row">
          <button type="submit">Save</button>
          {form.id && (
            <button
              type="button"
              className="ghost"
              onClick={() => setForm({ id: null, name: "", checks: emptyChecks(groups) })}
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
            <button type="button" className="ghost" onClick={() => applyRole(role)}>
              Edit
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

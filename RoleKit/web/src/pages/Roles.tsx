import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { PermissionCode, RoleOut } from "../types";

const CHECKS: { code: PermissionCode; label: string }[] = [
  { code: "documents:read", label: "Read" },
  { code: "documents:write", label: "Write" },
  { code: "documents:edit", label: "Edit" },
  { code: "documents:delete", label: "Delete" },
];

type RoleForm = {
  id: number | null;
  name: string;
  checks: Record<PermissionCode, boolean>;
};

function emptyForm(): RoleForm {
  return {
    id: null,
    name: "",
    checks: {
      "documents:read": false,
      "documents:write": false,
      "documents:edit": false,
      "documents:delete": false,
    },
  };
}

function fromRole(role: RoleOut): RoleForm {
  const checks = emptyForm().checks;
  for (const code of role.permissions) {
    if (code in checks) checks[code as PermissionCode] = true;
  }
  return { id: role.id, name: role.name, checks };
}

function codesFrom(checks: Record<PermissionCode, boolean>): PermissionCode[] {
  return CHECKS.map((item) => item.code).filter((code) => checks[code]);
}

function failMessage(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function Roles() {
  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [form, setForm] = useState<RoleForm>(emptyForm());
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const { data } = await api<RoleOut[]>("/roles");
    setRoles(data);
  }

  useEffect(() => {
    load().catch((err: unknown) => setError(failMessage(err)));
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    const permissions = codesFrom(form.checks);
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
      setForm(emptyForm());
      await load();
    } catch (err) {
      setError(failMessage(err));
    }
  }

  return (
    <main className="page">
      <h1>Roles</h1>
      <p className="lede">
        A role is a name plus four checks. Saving sends the full set of checked codes. Unchecking
        removes that code on the server.
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
        <fieldset className="checks">
          <legend>Permissions</legend>
          {CHECKS.map((item) => (
            <label key={item.code} className="check">
              <input
                type="checkbox"
                checked={form.checks[item.code]}
                onChange={(e) =>
                  setForm({
                    ...form,
                    checks: { ...form.checks, [item.code]: e.target.checked },
                  })
                }
              />
              {item.label}
              <span className="muted">{item.code}</span>
            </label>
          ))}
        </fieldset>
        <div className="row">
          <button type="submit">Save</button>
          {form.id && (
            <button type="button" className="ghost" onClick={() => setForm(emptyForm())}>
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
            <button type="button" className="ghost" onClick={() => setForm(fromRole(role))}>
              Edit
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

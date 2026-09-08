import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { SettingOut, UserMe } from "../types";

function fail(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function SettingsPage({ me }: { me: UserMe }) {
  const [workspaceName, setWorkspaceName] = useState("");
  const [banner, setBanner] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const canEdit = me.permissions.includes("settings:edit");

  async function load() {
    setError("");
    try {
      const { data } = await api<SettingOut>("/settings");
      setWorkspaceName(data.workspace_name);
      setBanner(data.banner);
    } catch (err) {
      setError(fail(err));
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      await api("/settings", {
        method: "PATCH",
        body: { workspace_name: workspaceName, banner },
      });
      setNotice("Saved. An audit row is written if you have audit:read.");
    } catch (err) {
      setError(fail(err));
    }
  }

  return (
    <main className="page">
      <h1>Settings</h1>
      <p className="lede">
        Workspace name and banner. <code>settings:read</code> to see, <code>settings:edit</code> to
        save. The desk role has both.
      </p>
      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}
      <form className="card form-grid" onSubmit={save}>
        <label>
          Workspace name
          <input value={workspaceName} onChange={(e) => setWorkspaceName(e.target.value)} />
        </label>
        <label>
          Banner
          <textarea value={banner} onChange={(e) => setBanner(e.target.value)} rows={3} />
        </label>
        {canEdit ? (
          <button type="submit">Save</button>
        ) : (
          <button type="submit">Try save</button>
        )}
      </form>
    </main>
  );
}

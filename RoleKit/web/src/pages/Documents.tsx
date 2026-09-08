/**
 * Documents.tsx — UI for the gated resource.
 * canWrite only hides the create form. Try edit / Try delete still fire
 * PATCH/DELETE so a missing server check would be obvious.
 */
import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { DocumentOut, UserMe } from "../types";

function fail(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function Documents({ me }: { me: UserMe }) {
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [editing, setEditing] = useState<DocumentOut | null>(null);
  const [error, setError] = useState("");
  const canWrite = me.permissions.includes("documents:write");
  const canEdit = me.permissions.includes("documents:edit");
  const canDelete = me.permissions.includes("documents:delete");

  async function load() {
    setError("");
    try {
      const { data } = await api<DocumentOut[]>("/documents");
      setDocs(data);
    } catch (err) {
      setDocs([]);
      setError(fail(err));
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function createDoc(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api("/documents", { method: "POST", body: { title, body } });
      setTitle("");
      setBody("");
      await load();
    } catch (err) {
      setError(fail(err));
    }
  }

  async function saveEdit(event: FormEvent) {
    event.preventDefault();
    if (!editing) return;
    setError("");
    try {
      await api(`/documents/${editing.id}`, {
        method: "PATCH",
        body: { title: editing.title, body: editing.body },
      });
      setEditing(null);
      await load();
    } catch (err) {
      setError(fail(err));
    }
  }

  async function remove(id: number) {
    setError("");
    try {
      await api(`/documents/${id}`, { method: "DELETE" });
      await load();
    } catch (err) {
      setError(fail(err));
    }
  }

  return (
    <main className="page">
      <h1>Documents</h1>
      <p className="lede">
        Server checks <code>documents:read / write / edit / delete</code> on every request. A 403
        shows as <strong>no permission</strong>.
      </p>
      {error && <p className="banner error">{error}</p>}

      {canWrite && (
        <form className="card form-grid" onSubmit={createDoc}>
          <h2>Create</h2>
          <label>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label>
            Body
            <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={3} />
          </label>
          <button type="submit">Create</button>
        </form>
      )}

      <ul className="doc-list">
        {docs.map((doc) => (
          <li key={doc.id} className="card">
            {editing?.id === doc.id ? (
              <form onSubmit={saveEdit}>
                <input
                  value={editing.title}
                  onChange={(e) => setEditing({ ...editing, title: e.target.value })}
                />
                <textarea
                  value={editing.body}
                  onChange={(e) => setEditing({ ...editing, body: e.target.value })}
                  rows={3}
                />
                <div className="row">
                  <button type="submit">Save</button>
                  <button type="button" className="ghost" onClick={() => setEditing(null)}>
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <>
                <h2>{doc.title}</h2>
                <p>{doc.body}</p>
                <div className="row">
                  <button type="button" className="ghost" onClick={() => setEditing(doc)}>
                    {canEdit ? "Edit" : "Try edit"}
                  </button>
                  <button type="button" className="danger" onClick={() => remove(doc.id)}>
                    {canDelete ? "Delete" : "Try delete"}
                  </button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}

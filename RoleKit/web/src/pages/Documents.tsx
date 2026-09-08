import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { DocumentOut, UserMe } from "../types";

function permissionMessage(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

export default function Documents({ me }: { me: UserMe }) {
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [editing, setEditing] = useState<DocumentOut | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const codes = me.permissions;
  const canWrite = codes.includes("documents:write");
  const canEdit = codes.includes("documents:edit");
  const canDelete = codes.includes("documents:delete");

  async function load() {
    setError("");
    try {
      const { data } = await api<DocumentOut[]>("/documents");
      setDocs(data);
    } catch (err) {
      setDocs([]);
      setError(permissionMessage(err));
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function createDoc(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      await api("/documents", { method: "POST", body: { title, body } });
      setTitle("");
      setBody("");
      setNotice("Created.");
      await load();
    } catch (err) {
      setError(permissionMessage(err));
    }
  }

  async function saveEdit(event: FormEvent) {
    event.preventDefault();
    if (!editing) return;
    setError("");
    setNotice("");
    try {
      await api(`/documents/${editing.id}`, {
        method: "PATCH",
        body: { title: editing.title, body: editing.body },
      });
      setEditing(null);
      setNotice("Updated.");
      await load();
    } catch (err) {
      setError(permissionMessage(err));
    }
  }

  async function remove(id: number) {
    setError("");
    setNotice("");
    try {
      await api(`/documents/${id}`, { method: "DELETE" });
      setNotice("Deleted.");
      await load();
    } catch (err) {
      setError(permissionMessage(err));
    }
  }

  return (
    <main className="page">
      <h1>Documents</h1>
      <p className="lede">
        Gates: read, write, edit, delete. Hiding a button is not auth. Your codes:{" "}
        {codes.length ? codes.join(", ") : "none"}
      </p>
      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}

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
                <p className="muted">
                  #{doc.id} · owner {doc.owner_id}
                </p>
                <div className="row">
                  {canEdit && (
                    <button type="button" className="ghost" onClick={() => setEditing(doc)}>
                      Edit
                    </button>
                  )}
                  {canDelete && (
                    <button type="button" className="danger" onClick={() => remove(doc.id)}>
                      Delete
                    </button>
                  )}
                  {!canEdit && (
                    <button type="button" className="ghost" onClick={() => setEditing(doc)}>
                      Try edit
                    </button>
                  )}
                  {!canDelete && (
                    <button type="button" className="ghost" onClick={() => remove(doc.id)}>
                      Try delete
                    </button>
                  )}
                </div>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}

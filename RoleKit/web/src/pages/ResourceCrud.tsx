import { useEffect, useState, type FormEvent } from "react";
import { api, isApiError } from "../api";
import type { TitledOut, UserMe } from "../types";

function permissionMessage(err: unknown) {
  if (isApiError(err) && err.status === 403) return "no permission";
  return err instanceof Error ? err.message : "Request failed";
}

type Verbs = {
  read: string;
  write: string;
  edit: string;
  delete: string;
};

type ResourceCrudProps = {
  me: UserMe;
  heading: string;
  blurb: string;
  path: string;
  verbs: Verbs;
};

export default function ResourceCrud({ me, heading, blurb, path, verbs }: ResourceCrudProps) {
  const [items, setItems] = useState<TitledOut[]>([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [editing, setEditing] = useState<TitledOut | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const canWrite = me.permissions.includes(verbs.write);
  const canEdit = me.permissions.includes(verbs.edit);
  const canDelete = me.permissions.includes(verbs.delete);

  async function load() {
    setError("");
    try {
      const { data } = await api<TitledOut[]>(path);
      setItems(data);
    } catch (err) {
      setItems([]);
      setError(permissionMessage(err));
    }
  }

  useEffect(() => {
    void load();
  }, [path]);

  async function createItem(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      await api(path, { method: "POST", body: { title, body } });
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
      await api(`${path}/${editing.id}`, {
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
      await api(`${path}/${id}`, { method: "DELETE" });
      setNotice("Deleted.");
      await load();
    } catch (err) {
      setError(permissionMessage(err));
    }
  }

  return (
    <main className="page">
      <h1>{heading}</h1>
      <p className="lede">{blurb}</p>
      {error && <p className="banner error">{error}</p>}
      {notice && <p className="banner ok">{notice}</p>}

      {canWrite && (
        <form className="card form-grid" onSubmit={createItem}>
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
        {items.map((item) => (
          <li key={item.id} className="card">
            {editing?.id === item.id ? (
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
                <h2>{item.title}</h2>
                <p>{item.body}</p>
                <p className="muted">
                  #{item.id} · owner {item.owner_id}
                </p>
                <div className="row">
                  {canEdit && (
                    <button type="button" className="ghost" onClick={() => setEditing(item)}>
                      Edit
                    </button>
                  )}
                  {canDelete && (
                    <button type="button" className="danger" onClick={() => remove(item.id)}>
                      Delete
                    </button>
                  )}
                  {!canEdit && (
                    <button type="button" className="ghost" onClick={() => setEditing(item)}>
                      Try edit
                    </button>
                  )}
                  {!canDelete && (
                    <button type="button" className="ghost" onClick={() => remove(item.id)}>
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

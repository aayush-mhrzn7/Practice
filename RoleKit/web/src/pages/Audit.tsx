/**
 * Audit.tsx — GET /audit. 403 → "no permission" if audit:read is missing.
 */
import { useEffect, useState } from "react";
import { api, isApiError } from "../api";
import type { AuditEvent } from "../types";

export default function Audit() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<AuditEvent[]>("/audit")
      .then(({ data }) => setEvents(data))
      .catch((err: unknown) => {
        setEvents([]);
        setError(isApiError(err) && err.status === 403 ? "no permission" : "Request failed");
      });
  }, []);

  return (
    <main className="page">
      <h1>Audit</h1>
      <p className="lede">
        Role create / replace / grant / revoke. Needs <code>audit:read</code>.
      </p>
      {error && <p className="banner error">{error}</p>}
      <ul className="doc-list">
        {events.map((event) => (
          <li key={event.id} className="card">
            <h2>{event.action}</h2>
            <p>{event.detail}</p>
            <p className="muted">
              actor {event.actor_id ?? "—"} · {event.created_at}
            </p>
          </li>
        ))}
      </ul>
    </main>
  );
}

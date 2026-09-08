import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { PermissionGroup, UserMe } from "../types";

const AREAS = [
  { to: "/documents", label: "Documents", read: "documents:read" },
  { to: "/notes", label: "Notes", read: "notes:read" },
  { to: "/announcements", label: "Announcements", read: "announcements:read" },
  { to: "/audit", label: "Audit", read: "audit:read" },
  { to: "/settings", label: "Settings", read: "settings:read" },
];

export default function Home({ me }: { me: UserMe }) {
  const [groups, setGroups] = useState<PermissionGroup[]>([]);

  useEffect(() => {
    api<PermissionGroup[]>("/permissions")
      .then(({ data }) => setGroups(data))
      .catch(() => setGroups([]));
  }, []);

  return (
    <main className="page">
      <h1>Desk</h1>
      <p className="lede">
        Your token is only an id. These codes were loaded from SQL on <code>GET /me</code>.
      </p>
      <div className="dash-grid">
        {AREAS.map((area) => {
          const allowed = me.permissions.includes(area.read);
          return (
            <Link key={area.to} to={area.to} className="card dash-card">
              <h2>{area.label}</h2>
              <p className={allowed ? "ok-text" : "muted"}>{allowed ? "read allowed" : "will 403"}</p>
            </Link>
          );
        })}
      </div>
      {groups.map((group) => (
        <section key={group.key} className="chip-block">
          <h2>{group.label}</h2>
          <ul className="chips">
            {group.permissions.map((item) => {
              const on = me.permissions.includes(item.code);
              return (
                <li key={item.code} className={on ? "chip on" : "chip"}>
                  {item.label}
                  <span>{item.code}</span>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </main>
  );
}

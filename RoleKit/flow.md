# RoleKit flow

How a request becomes a 403 or a 200, and **why each file exists**.
Read this, then open the files. The code comments match this document.

There is no seed. Register once — that user is admin. Create a role, tick
codes, assign it to a second account.

---

## What the JWT is allowed to know

```
JWT payload = { sub: user_id, exp }
```

No roles. No permission list. Logout on the client only deletes
`localStorage.rolekit_token`. The token is still valid until `exp`.
Revoke still works because the **next** request reloads from SQLite.

---

## Tables

```
User ──< user_roles >── Role ──< role_permissions >── Permission
  │
  └── documents.owner_id

audit_events  (append-only log of grant / revoke / role save)
```

Permission rows are frozen (Alembic inserted them):

| code | meaning |
|---|---|
| `documents:read` | GET documents |
| `documents:write` | POST (create) |
| `documents:edit` | PATCH (update) |
| `documents:delete` | DELETE |
| `audit:read` | GET /audit |

`is_admin` is **not** in that table. It only unlocks `/roles` and `/users`.
An admin with no document role still gets 403 on GET `/documents`.

---

## Request path (the thing to memorize)

Example: `PATCH /documents/1` with `Authorization: Bearer …`

```
1. web/src/api.ts
      attach Bearer token from localStorage
      fetch http://localhost:8000/documents/1

2. api/main.py
      CORS allows the Vite origin
      route → routers/documents.py update_document

3. FastAPI Depends, in order:
      get_db()                 database.py   open a Session
      get_current_user()       auth.py       decode sub, load User
      require_permission(      deps.py
        "documents:edit")
          load_permission_codes(user_id)
            SQL: user → roles → permission.codes
          if "documents:edit" not in set → 403 { detail: "no permission" }

4. If the code is present, UPDATE the row and return JSON.
```

Same token, after admin DELETE `/users/{id}/roles/{role_id}`:

```
3. load_permission_codes again  (new Session, new query)
   "documents:edit" gone → 403
```

That is why codes are not in the token.

401 vs 403:

| status | meaning | where |
|---|---|---|
| 401 | no/bad/expired token, or unknown user id | `auth.py` |
| 403 | we know you; you lack the code (or not admin) | `deps.py` |
| 409 | unique email or role name | IntegrityError |

---

## Happy path you should walk

1. Create account (first user → admin).
2. Roles: name `viewer`, tick Documents **read** only, save.
3. Create a second account (not admin).
4. Users: assign `viewer` to that account.
5. Log in as the second user: GET documents works; PATCH/DELETE show **no permission**.
6. Tick Audit **read** on that role, save. Audit page works for them.
7. Uncheck it / revoke the role. Same JWT, next request 403s.

Role create/replace/grant/revoke also insert `audit_events`. Viewing them
needs `audit:read`.

---

## File map (API)

### `api/main.py`

Wires CORS and routers. No business logic. If a new resource appears, you
include a router here — we kept only documents + audit.

### `api/database.py`

Engine + `get_db()`. One Session per request, always closed. SQLite file is
`rolekit.db`. Alembic uses the same URL (`alembic.ini`).

### `api/models.py`

SQLAlchemy tables. Association tables `user_roles` and `role_permissions`
are the grant graph. `PERMISSION_CODES` is the allow-list roles.py checks
so the UI cannot invent `documents:explode`.

### `api/schemas.py`

JSON in/out. Separate from models so the token response cannot accidentally
include ORM relationships. `UserOut.permissions` is filled in auth.py from
`load_permission_codes`, not from a column on `users`.

### `api/auth.py`

Hash, verify, encode, decode, `get_current_user`.
**Reason it is not inside deps.py:** 401 (identity) and 403 (authorization)
are different failures. Keep identity here.

### `api/deps.py`

**This is the authorization file.**

- `load_permission_codes(db, user_id)` — walk the M2M graph, return a set.
- `require_admin` — `user.is_admin`, for matrix CRUD only.
- `require_permission(code)` — factory that returns a FastAPI dependency.

Why a factory? FastAPI `Depends(fn)` injects arguments into `fn`. We need
to pass `code` as well, so we close over it:

```
require_permission("documents:edit")
    returns checker(user, db)
        403 unless code in load_permission_codes(...)
```

Why reload every request? If we stored `user._codes` on a cached object,
revoke would lie until restart.

### `api/routers/auth.py`

`POST /auth/register` (first user is admin), `POST /auth/login` (`{access_token}`),
`GET /me`. No seed.py.

### `api/routers/roles.py`

Admin. Create a name. PATCH replaces the permission set (full list of
checked codes). Writes an audit row.

### `api/routers/users.py`

Admin. POST grant, DELETE revoke. Writes an audit row. Does not touch JWT.

### `api/routers/documents.py`

Plain CRUD. Each function has `Depends(require_permission("documents:…"))`.
No generic factory — you can read GET vs POST vs PATCH vs DELETE in one file.

### `api/routers/audit.py`

`GET /audit` gated by `audit:read`. `add_audit()` is the insert helper
roles/users call.

### `alembic/`

Schema migrations. `001` creates users/roles/permissions/documents.
`002` added extra resources (history). `003_simplify` drops those extras
and keeps documents + `audit:read`. Cold start: `alembic upgrade head`.

---

## File map (web)

### `web/src/main.tsx`

Mount React + BrowserRouter.

### `web/src/App.tsx`

Holds `me` from GET `/me`. Nav: Documents, Audit; Roles/Users if `me.is_admin`.
Logout = `clearToken()`. Protected routes bounce to `/login` without a token.

### `web/src/api.ts`

`fetch` wrapper. Bearer header. Maps 403 to `ApiError` so pages can print
**no permission**.

### `web/src/types.ts`

TypeScript shapes that match `schemas.py`.

### `web/src/pages/Login.tsx`

Sign in or create account. First create-account is admin.

### `web/src/pages/Documents.tsx`

List/create/edit/delete. Buttons still call the API when you lack the code
("Try edit") so you can see 403. Hiding the button is not auth.

### `web/src/pages/Roles.tsx`

Table: resource × create / update / delete / read.
Create → `documents:write`, update → `documents:edit`.
Audit only has a read checkbox. Save sends the **full** checked list.

### `web/src/pages/Users.tsx`

Pick a user, tick roles, save. Diffs POST (grant) vs DELETE (revoke).

### `web/src/pages/Audit.tsx`

GET `/audit`. 403 if you lack `audit:read`.

---

## Two gates, side by side

```
                    is_admin?                    permission code?
                         │                            │
                         ▼                            ▼
              POST/PATCH /roles              GET/POST/PATCH/DELETE /documents
              POST/DELETE user roles         GET /audit
```

Do not short-circuit "admin can do everything" on documents unless you
change this file and `deps.py` on purpose.

---

## Cold start (no seed)

```bash
cd RoleKit
source venv/bin/activate
alembic upgrade head
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd web && npm run dev
```

Open `http://localhost:5173`, **Create account**, then walk the happy path above.

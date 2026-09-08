# RoleKit

A one-day learning bar: a small admin for **named roles**. Not a product. No Celery, no deploy, no real document app beyond enough CRUD to prove a **403**.

The JWT only carries your **user id**. Every protected route reloads roles and permissions from SQLAlchemy. The checkboxes never authorize anything by themselves.

This README is the map of how RoleKit works. The code is already in `api/` and `web/`. Use the evenings as a walkthrough of the design, then cold-start and prove a 403.

---

## What this is, and what it is not

| RoleKit is | RoleKit is not |
|---|---|
| JWT with `sub` = user id | A permission list inside the token |
| Roles named by you (`night-editor`) | A document product |
| Four frozen permission codes | UI-invented permission codes |
| Server 403 on missing code | Hide-the-button auth |
| `is_admin` for role/user admin | “Admin can do everything” on documents |
| SQLite + Alembic | Celery, Redis, deploy, Rolemill |

If you already know JWT and React, evenings 1–4 can collapse into one sitting. Do not add Celery here. That is Rolemill.

---

## Target layout

Reshape the current files into this. Today you have `main.py`, `database/`, and `routers/` at the RoleKit root. The finished tree lives under `api/` plus `web/`.

```
RoleKit/
  api/
    main.py          # FastAPI, CORS, include routers
    database.py      # engine, SessionLocal, get_db
    models.py        # User, Role, Permission, Document, two M2Ms
    schemas.py       # Pydantic in/out, ConfigDict(from_attributes=True)
    auth.py          # hash, verify, create/decode JWT, get_current_user
    deps.py          # require_permission("documents:edit")
    routers/
      auth.py        # register, login, /me
      roles.py       # name a role, set the four checks
      users.py       # grant/revoke roles
      documents.py  # the gated resource
    seed.py
  alembic/
  web/               # Vite + React + TypeScript
    src/pages/Login.tsx
    src/pages/Documents.tsx
    src/pages/Roles.tsx
    src/pages/Users.tsx
  README.md
```

The tree above is what is in this folder. Run from `RoleKit/`. Uvicorn loads `api.main:app`.

---

## Mental model

```
User ──< user_roles >── Role ──< role_permissions >── Permission (four seed codes)
  │
  └── documents.owner_id
```

**Auth is a chain, not a token dump.**

```
request
  → Bearer token
  → decode JWT → sub (user id only)
  → load User from DB
  → if require_permission(code):
       load user.roles
       union role.permissions.codes
       403 if code not in that set
```

Revoke a role in the DB. The next request fails even if the JWT is still valid. Do not cache the permission set on the user object across requests.

**Two different gates**

```
is_admin          →  POST/PATCH /roles, grant/revoke user roles
permission codes  →  GET/POST/PATCH/DELETE /documents
```

`is_admin` is only the bootstrap for managing the matrix. Document access comes from the role matrix. Do not short-circuit “admin can do everything” unless you write that shortcut in this README and mean it. Default: **no shortcut**.

---

## Tables

### `users`

| Column | Notes |
|---|---|
| `id` | PK |
| `email` | unique → IntegrityError maps to **409** |
| `password_hash` | bcrypt. Never store plaintext. Rename from current `password`. |
| `is_admin` | bootstrap flag for role CRUD only |

Drop `username` from the current model unless you want it as extra display. Spec auth is email + password.

### `permissions`

Four seed rows. **Do not let the UI invent new codes.**

| code |
|---|
| `documents:read` |
| `documents:write` |
| `documents:edit` |
| `documents:delete` |

Seed them in an Alembic migration, not in random app startup.

### `roles`

| Column | Notes |
|---|---|
| `id` | PK |
| `name` | unique (`night-editor`) → IntegrityError maps to **409** |

A role is just a name you type.

### `role_permissions`

Many-to-many. Granting a permission to a role means inserting a row here. Replacing a role’s permission set means: **delete all current links, insert the full checked set**. Do not toggle one code at a time on the server unless you also send the full set.

Composite PK `(role_id, permission_id)` is enough. The extra `id` on the current association tables is optional; drop it if you want a textbook association table.

### `user_roles`

Many-to-many. Grant = insert. Revoke = delete that row.

### `documents`

| Column | Notes |
|---|---|
| `id` | PK |
| `title` | |
| `body` | |
| `owner_id` | FK → users.id |
| `created_at` | server default `now()` |

Enough CRUD to prove a 403. Not a real document app.

---

## Request map

| Method | Path | Who | Gate | Status notes |
|---|---|---|---|---|
| `POST` | `/auth/register` | anyone | none | **201**, hash password |
| `POST` | `/auth/login` | anyone | none | `{ access_token }`, bad password **401** |
| `GET` | `/me` | logged in | valid JWT | user + **permission codes** for the UI |
| `GET` | `/roles` | admin | `is_admin` | roles with their codes |
| `POST` | `/roles` | admin | `is_admin` | body `{ name }` |
| `PATCH` | `/roles/{id}` | admin | `is_admin` | name and/or **replace** permission codes |
| `POST` | `/users/{id}/roles/{role_id}` | admin | `is_admin` | grant |
| `DELETE` | `/users/{id}/roles/{role_id}` | admin | `is_admin` | revoke |
| `GET` | `/documents` | logged in | `documents:read` | list |
| `GET` | `/documents/{id}` | logged in | `documents:read` | get |
| `POST` | `/documents` | logged in | `documents:write` | create |
| `PATCH` | `/documents/{id}` | logged in | `documents:edit` | update |
| `DELETE` | `/documents/{id}` | logged in | `documents:delete` | **204** |

Missing permission → **403**, never 404. Missing document after you already passed the permission check may still be 404. Do not hide a 403 as a 404.

SQLite unique email / unique role name → catch `IntegrityError` → **409**.

---

## Pseudo-code: core modules

These are the files to write. Keep them this thin.

### `api/database.py`

```
DATABASE_URL = sqlite:///./rolekit.db
engine = create_engine(..., connect_args={check_same_thread: False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

function get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Alembic owns schema. Do not `Base.metadata.create_all()` in production flow. Cold start is `alembic upgrade head`.

### `api/models.py`

```
User:
    email unique
    password_hash
    is_admin default False
    roles  M2M via user_roles
    documents relationship

Permission:
    code unique   # documents:read | write | edit | delete
    roles  M2M via role_permissions

Role:
    name unique
    permissions M2M via role_permissions
    users       M2M via user_roles

Document:
    title, body
    owner_id FK users.id
    created_at

user_roles         Table(user_id FK, role_id FK, PK both)
role_permissions   Table(role_id FK, permission_id FK, PK both)
```

### `api/schemas.py`

```
UserCreate:     email, password
UserOut:        id, email, is_admin, permissions: list[str]
TokenOut:       access_token

RoleCreate:     name
RoleUpdate:     name?: str, permissions?: list[str]   # full set of codes
RoleOut:        id, name, permissions: list[str]

DocumentCreate: title, body
DocumentUpdate: title?, body?
DocumentOut:    id, title, body, owner_id, created_at

# every Out schema: model_config = ConfigDict(from_attributes=True)
```

`GET /me` returns `UserOut` so the React shell knows which buttons to show. Showing a button is not authorization.

### `api/auth.py`

```
SECRET = env JWT_SECRET
ALGO   = HS256

function hash_password(plain) -> str
function verify_password(plain, hashed) -> bool

function create_access_token(user_id) -> str:
    payload = { sub: str(user_id), exp: now + TTL }
    return jwt.encode(payload, SECRET, ALGO)
    # NEVER put permissions or is_admin in the payload

function decode_token(token) -> user_id
    # 401 on missing/expired/invalid

function get_current_user(Authorization Bearer, db) -> User:
    user_id = decode_token(token)
    user = db.get(User, user_id)
    if not user: 401
    return user
```

Login returns `{ access_token }`. Logout on the client is `localStorage.removeItem`. The JWT stays valid until it expires. Document that.

### `api/deps.py`

```
function require_admin(user = get_current_user):
    if not user.is_admin:
        raise 403
    return user

function require_permission(code: str):
    function checker(user = get_current_user, db):
        # reload from SQLAlchemy every request — no cache
        codes = empty set
        for role in user.roles:          # load roles
            for perm in role.permissions:  # load permissions
                codes.add(perm.code)
        if code not in codes:
            raise 403 { detail: "no permission" }
        return user
    return checker
```

Use it as:

```
@router.get("/documents")
def list_docs(user = Depends(require_permission("documents:read")), db=Depends(get_db)):
    ...
```

The string is the only source of truth. Checkboxes in React do not appear here.

### `api/routers/auth.py`

```
POST /auth/register:
    hash password
    insert User(is_admin=False)
    on IntegrityError → 409
    return 201 UserOut (permissions = [])

POST /auth/login:
    find by email
    if missing or verify_password fails → 401
    return { access_token: create_access_token(user.id) }

GET /me:
    user = get_current_user
    codes = union of permission codes from DB (same loop as require_permission)
    return { id, email, is_admin, permissions: codes }
```

### `api/routers/roles.py`

```
all routes Depends(require_admin)

GET /roles:
    return each role with [p.code for p in role.permissions]

POST /roles  body { name }:
    insert Role
    on IntegrityError → 409
    return RoleOut with permissions []

PATCH /roles/{id}  body { name?, permissions?: [codes] }:
    if name: role.name = name
    if permissions is not None:
        # REPLACE, do not toggle
        validate every code is one of the four seed codes
        if unknown code → 400
        role.permissions = db.query(Permission).filter(code in body.permissions).all()
    commit
    return RoleOut
```

Unchecking in the UI means: send the list **without** that code. Server replaces the set. That is how uncheck works.

### `api/routers/users.py`

```
all grant/revoke Depends(require_admin)

POST /users/{id}/roles/{role_id}:
    attach role to user (insert user_roles)
    if already attached: 200 idempotent or 409 — pick one and stick to it
    return user + role names

DELETE /users/{id}/roles/{role_id}:
    detach row
    if not attached: 404
    next request from that user must 403 on codes that role owned
```

Also useful for the Users page: `GET /users` (admin) listing id, email, role names. Spec does not name it; the UI needs it. Add it.

### `api/routers/documents.py`

```
GET    /documents      require documents:read
GET    /documents/{id} require documents:read
POST   /documents      require documents:write   owner_id = current user
PATCH  /documents/{id} require documents:edit
DELETE /documents/{id} require documents:delete → 204 no body
```

Permission check runs **before** “does this id exist?” if you want 403 on a viewer hitting DELETE `/documents/1`. FastAPI Depends runs first. That is the desired order.

### `api/main.py`

```
app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite only, evening 5
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(users.router)
app.include_router(documents.router)
```

### `api/seed.py`

Run after `alembic upgrade head`. Idempotent: skip if admin email exists.

```
ensure permissions already exist (migration)

admin  = User(email=admin@rolekit.dev,  hash(pass), is_admin=True)
viewer = User(email=viewer@rolekit.dev, hash(pass), is_admin=False)
editor = User(email=editor@rolekit.dev, hash(pass), is_admin=False)

role_admin  = Role(name="admin")   # optional; is_admin still gates /roles
role_viewer = Role(name="viewer")  # documents:read only
role_editor = Role(name="editor")  # read + write + edit, not delete

assign viewer → viewer user
assign editor → editor user
# admin user may have no document roles; is_admin ≠ document superuser

insert 2 documents owned by admin
```

Pick passwords, write them in this README’s cold-start section so you can smoke both logins.

---

## Pseudo-code: request lifecycle (one PATCH)

```
1. React: Authorization: Bearer <token>
2. get_current_user
      decode sub → 7
      SELECT users WHERE id = 7
3. require_permission("documents:edit")
      SELECT roles via user_roles WHERE user_id = 7
      SELECT permissions via role_permissions for those roles
      codes = { "documents:read", "documents:edit" }
      "documents:edit" in codes? yes → continue
      if this were DELETE: "documents:delete" not in codes → 403
4. UPDATE documents SET ... WHERE id = ?
5. return DocumentOut
```

Same token, later, after admin revokes `night-editor`:

```
3. codes = { "documents:read" }   # reloaded, not from JWT
   "documents:edit" missing → 403
```

---

## Evenings

Do not skip the exit criteria. Each evening has a proof.

### Evening 1 — Auth only

**Build**

- Reshape into `api/`
- Alembic: `users` table (`email` unique, `password_hash`, `is_admin`)
- `POST /auth/register` → 201
- `POST /auth/login` → `{ access_token }`
- `GET /me` with Bearer

**Pseudo flow**

```
register(email, password):
    user = User(email, hash(password), is_admin=False)
    save
    201

login(email, password):
    user = find email
    if not user or not verify: 401
    return { access_token }

me():
    return current user
```

**Done when**

- Bad password returns **401**
- Restart uvicorn, login still finds the user (Alembic + SQLite file, not memory)

### Evening 2 — Roles in the API

**Build**

- Migration: `permissions`, `roles`, `role_permissions`, `user_roles`
- Seed the four codes in that migration
- Admin-only role CRUD + grant/revoke
- Bootstrap: first user you register, then `UPDATE users SET is_admin=1` in sqlite, **or** a seed flag. You need one admin to call `/roles`.

**Pseudo flow**

```
create_role({ name }):
    require is_admin
    insert Role(name)

replace_permissions(role_id, codes):
    require is_admin
    role.permissions = load Permissions where code in codes   # full replace

grant(user_id, role_id):
    require is_admin
    insert user_roles

revoke(user_id, role_id):
    require is_admin
    delete that user_roles row
```

**Done when**

- A `viewer` role exists with only `documents:read`
- Assigned to a second user
- `GET /me` as that user returns `permissions: ["documents:read"]`

### Evening 3 — Documents plus gates

**Build**

- `documents` table + router
- Wire `require_permission` on each verb

**Pseudo flow**

```
list/get  → documents:read
create    → documents:write
patch     → documents:edit
delete    → documents:delete → 204
missing   → 403 { detail: "no permission" }
```

**Done when**

- Viewer token: GET works
- Viewer token: POST, PATCH, DELETE → **403** (not 404)

Prove with curl, not the UI yet:

```
curl -H "Authorization: Bearer $VIEWER" http://localhost:8000/documents
curl -X POST .../documents          # 403
curl -X PATCH .../documents/1      # 403
curl -X DELETE .../documents/1     # 403
```

### Evening 4 — React shell

**Build**

```
npm create vite@latest web -- --template react
```

- `Login.tsx` — POST login, store token (`localStorage`)
- Axios/fetch interceptor: every request `Authorization: Bearer`
- `Documents.tsx` — list, create, edit, delete
- On 403, render the body as **`no permission`**
- After login, `GET /me` to know `is_admin` and codes

**Pseudo flow**

```
onLogin:
    token = login().access_token
    store token
    me = GET /me
    route to /documents

api(method, url, body):
    headers.Authorization = Bearer + token
    res = fetch
    if res.status == 403:
        show "no permission"
    if res.status == 401:
        drop token, go to /login
```

**Done when**

- Log in as viewer vs a user who has write/edit/delete
- Same page, different 403s. The UI difference is a consequence of the API, not a second auth system.

### Evening 5 — The checkbox page (the point of the week)

**Roles.tsx**

```
state: name, read, write, edit, delete   # four booleans

onSave:
    codes = []
    if read:   codes.push("documents:read")
    if write:  codes.push("documents:write")
    if edit:   codes.push("documents:edit")
    if delete: codes.push("documents:delete")
    if role is new: POST /roles { name }
    PATCH /roles/{id} { name, permissions: codes }   # full set
```

Unchecking Edit means the next PATCH sends `["documents:read"]` with no edit. Server replaces. Do not send `{ remove: "documents:edit" }`.

**Users.tsx**

```
pick user
checkboxes = all roles (checked if currently granted)

onSave:
    desired = checked role ids
    current = GET that user's roles
    for id in desired - current: POST  /users/{id}/roles/{role_id}
    for id in current - desired: DELETE /users/{id}/roles/{role_id}
```

**Done when, all from the UI**

1. Create role `night-editor`
2. Tick Read and Edit
3. Assign it to a user
4. Log in as that user
5. PATCH a document works
6. DELETE returns 403 → page shows `no permission`

### Evening 6 — Harden

- CORS allowlist = Vite origin only (`http://localhost:5173`)
- Hide Roles / Users nav unless `me.is_admin`
- Logout = drop the token. Note in this README: **the JWT stays valid until it expires**
- `seed.py`: admin, viewer, editor, two demo users, a couple of documents
- Hide delete button if `"documents:delete" not in me.permissions` — **and** keep the server 403. A manual fetch must still fail.

**Done when**

- Cold start below works on a clean clone
- Viewer vs editor vs night-editor behave as in evening 5
- Admin sees nav; viewer does not

---

## React pages (contract)

### `Login.tsx`

Form: email, password → `POST /auth/login` → store token → `GET /me` → `/documents`.

### `Documents.tsx`

- List from `GET /documents`
- Create form if UI has `documents:write` (still 403 if someone forges)
- Edit if `documents:edit`
- Delete if `documents:delete`
- Any 403 body → show `no permission`

### `Roles.tsx` (admin)

Name field + four checkboxes: Read, Write, Edit, Delete → the four codes. Save sends name + checked codes. Load existing role by mapping codes back to checks.

### `Users.tsx` (admin)

User select + role checks. Save diffs grants/revokes. Do not PUT a whole user blob unless you also implement that; the spec is POST/DELETE per role.

### Client auth helper

```
token in localStorage
logout: remove token, redirect /login
is_admin from /me, not from JWT payload
```

---

## Cold start

From `RoleKit/`:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m api.seed
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Second terminal:

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5173`. API is `http://localhost:8000`. CORS is locked to the Vite origin.

Logout only drops the token in `localStorage`. The JWT stays valid until it expires (8 hours). There is no denylist.

**Seed logins**

| email | password | flags | document codes |
|---|---|---|---|
| `admin@rolekit.dev` | `adminpass` | `is_admin` | none |
| `viewer@rolekit.dev` | `viewerpass` | | `documents:read` |
| `editor@rolekit.dev` | `editorpass` | | read, write, edit |
| `demo1@rolekit.dev` | `demopass` | | none |
| `demo2@rolekit.dev` | `demopass` | | none |

Smoke viewer and admin after seed. Admin can open Roles/Users but `GET /documents` is 403 until you grant a document role. That is intentional: `is_admin` is not a document superuser.

---

## Walkthrough: one grant, one revoke

Use this after evening 5.

**Grant**

1. Log in as admin.
2. Roles: create `night-editor`, tick Read + Edit, save.
3. Users: pick `viewer@rolekit.dev` (or a third user), check `night-editor`, save → `POST /users/{id}/roles/{role_id}`.
4. Log in as that user. `GET /me` includes `documents:read` and `documents:edit`.
5. Documents: edit a row. PATCH 200.
6. Delete. DELETE 403, UI shows `no permission`.

**Revoke**

1. Admin: uncheck `night-editor` on that user, save → `DELETE /users/{id}/roles/{role_id}`.
2. Do **not** wait for the JWT to expire.
3. Same user, same token, PATCH again → **403**.
4. That is the whole point of not putting permissions in the token.

---

## Pitfalls (read before you code)

1. **A checkbox is not auth.** Hide delete in React and forget `require_permission("documents:delete")` → a manual fetch still deletes. Always 403 on the server.

2. **`is_admin` is not document superuser.** It only unlocks role/user admin routes. An admin with no document roles GET `/documents` → 403. That is correct unless you document a shortcut.

3. **Replace the full permission set.** PATCH body is the checked codes. Uncheck = omit from the list. A single-code toggle makes uncheck easy to get wrong.

4. **Revoke must hit the DB.** `require_permission` loads roles every request. Do not store `user.permissions` on a cached user attached to the app. Do not put codes in JWT.

5. **Unique email / unique role name** → `IntegrityError` → **409**, not 500.

6. **403 vs 404.** Missing permission is 403 even if the document id is fake. Viewer probing DELETE should not learn existence via 404.

7. **Logout does not invalidate JWT.** Client drops the token. README must say the token remains valid until `exp`. No denylist in RoleKit.

8. **Do not invent permission codes in the UI.** The four checkboxes map to four strings. No free-text permission field.

9. **JWT secret.** Override with `JWT_SECRET` in `.env`. The payload is only `sub` + `exp`.

10. **No Celery.** If you reach for a queue, you left RoleKit.

---

## Dependencies (keep this small)

API (`requirements.txt`):

```
fastapi[standard]
sqlalchemy
alembic
pyjwt
bcrypt
python-dotenv
```

Web: Vite + React + TypeScript. `fetch` in `web/src/api.ts` attaches `Authorization: Bearer`.

---

## File-by-file checklist

Use this as a progress list. Do not start evening 4 until 1–3 are green.

- [x] `api/database.py` — engine, `get_db`
- [x] `api/models.py` — User, Role, Permission, Document, two M2Ms
- [x] Alembic env points at `Base.metadata`
- [x] Migration: users
- [x] Migration: permissions (four INSERT), roles, M2Ms, documents
- [x] `api/schemas.py`
- [x] `api/auth.py` — hash, JWT, `get_current_user`
- [x] `api/deps.py` — `require_admin`, `require_permission`
- [x] `api/routers/auth.py` — register 201, login, `/me`
- [x] `api/routers/roles.py` — create, replace codes, list
- [x] `api/routers/users.py` — grant, revoke, list users
- [x] `api/routers/documents.py` — four verbs, 204 on delete
- [x] `api/main.py` — CORS locked to Vite
- [x] `api/seed.py`
- [x] `web` Login, Documents, Roles, Users
- [ ] Proof on your machine: night-editor PATCH 200, DELETE 403 from the UI
- [ ] Proof on your machine: revoke then PATCH 403 with the same token

---

## Status of this folder today

Implemented. Walk the grant/revoke section from the UI to prove it: create `night-editor`, tick Read and Edit, assign it, PATCH works, DELETE shows `no permission`. Then revoke and PATCH again with the same token — still 403.

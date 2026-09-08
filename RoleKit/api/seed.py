from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth import hash_password
from api.database import SessionLocal
from api.models import PERMISSION_CODES, Announcement, Document, Note, Permission, Role, Setting, User

ADMIN_EMAIL = "admin@rolekit.dev"
VIEWER_EMAIL = "viewer@rolekit.dev"
EDITOR_EMAIL = "editor@rolekit.dev"
AUDITOR_EMAIL = "auditor@rolekit.dev"
DEMO1_EMAIL = "demo1@rolekit.dev"
DEMO2_EMAIL = "demo2@rolekit.dev"

PASSWORDS = {
    ADMIN_EMAIL: "adminpass",
    VIEWER_EMAIL: "viewerpass",
    EDITOR_EMAIL: "editorpass",
    AUDITOR_EMAIL: "auditorpass",
    DEMO1_EMAIL: "demopass",
    DEMO2_EMAIL: "demopass",
}


def _get_or_create_user(db: Session, email: str, is_admin: bool = False) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(PASSWORDS[email]),
            is_admin=is_admin,
        )
        db.add(user)
        db.flush()
    else:
        user.is_admin = is_admin
        user.password_hash = hash_password(PASSWORDS[email])
    return user


def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if role is None:
        role = Role(name=name)
        db.add(role)
        db.flush()
    return role


def _assign(user: User, role: Role) -> None:
    if role not in user.roles:
        user.roles.append(role)


def seed(db: Session) -> None:
    perms = {p.code: p for p in db.execute(select(Permission)).scalars()}
    missing = [code for code in PERMISSION_CODES if code not in perms]
    if missing:
        raise RuntimeError(
            f"Missing permission rows {missing}. Run `alembic upgrade head` first."
        )

    admin = _get_or_create_user(db, ADMIN_EMAIL, is_admin=True)
    viewer_user = _get_or_create_user(db, VIEWER_EMAIL)
    editor_user = _get_or_create_user(db, EDITOR_EMAIL)
    auditor_user = _get_or_create_user(db, AUDITOR_EMAIL)
    _get_or_create_user(db, DEMO1_EMAIL)
    _get_or_create_user(db, DEMO2_EMAIL)

    viewer_role = _get_or_create_role(db, "viewer")
    editor_role = _get_or_create_role(db, "editor")
    auditor_role = _get_or_create_role(db, "auditor")
    desk_role = _get_or_create_role(db, "desk")

    viewer_role.permissions = [
        perms["documents:read"],
        perms["notes:read"],
        perms["announcements:read"],
    ]
    editor_role.permissions = [
        perms["documents:read"],
        perms["documents:write"],
        perms["documents:edit"],
        perms["notes:read"],
        perms["notes:write"],
        perms["notes:edit"],
        perms["announcements:read"],
        perms["announcements:write"],
        perms["announcements:edit"],
    ]
    auditor_role.permissions = [
        perms["documents:read"],
        perms["notes:read"],
        perms["announcements:read"],
        perms["audit:read"],
    ]
    desk_role.permissions = [
        perms["settings:read"],
        perms["settings:edit"],
        perms["announcements:read"],
        perms["announcements:write"],
        perms["announcements:edit"],
        perms["announcements:delete"],
    ]

    _assign(viewer_user, viewer_role)
    _assign(editor_user, editor_role)
    _assign(auditor_user, auditor_role)

    if db.execute(select(Setting).where(Setting.id == 1)).scalar_one_or_none() is None:
        db.add(
            Setting(
                id=1,
                workspace_name="RoleKit",
                banner="The JWT only carries your user id. Checkboxes never authorize anything.",
            )
        )

    if not db.execute(select(Document)).scalars().first():
        db.add_all(
            [
                Document(
                    title="Welcome to RoleKit",
                    body="Enough CRUD to prove a 403. The JWT only carries your user id.",
                    owner_id=admin.id,
                ),
                Document(
                    title="The night desk",
                    body="Create night-editor, tick Read and Edit, then PATCH this. DELETE should fail.",
                    owner_id=admin.id,
                ),
            ]
        )

    if not db.execute(select(Note)).scalars().first():
        db.add_all(
            [
                Note(
                    title="Shift handover",
                    body="Viewer can read this. Editor can patch it. Neither can delete unless you grant notes:delete.",
                    owner_id=admin.id,
                ),
                Note(
                    title="Locker combo is not in the JWT",
                    body="Revoke a role and the next request reloads from SQLAlchemy.",
                    owner_id=admin.id,
                ),
            ]
        )

    if not db.execute(select(Announcement)).scalars().first():
        db.add_all(
            [
                Announcement(
                    title="Desk is open",
                    body="Announcements are a separate resource. Same 403 rules, different codes.",
                    owner_id=admin.id,
                ),
                Announcement(
                    title="Auditor sees the log",
                    body="Grant audit:read to watch grants and revokes. Settings stay dark unless you tick them.",
                    owner_id=admin.id,
                ),
            ]
        )

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
        print("Seeded RoleKit.")
        print("  admin@rolekit.dev   / adminpass    is_admin; no resource codes")
        print("  viewer@rolekit.dev  / viewerpass   read documents, notes, announcements")
        print("  editor@rolekit.dev  / editorpass   write/edit those three; no delete")
        print("  auditor@rolekit.dev / auditorpass   reads + audit:read")
        print("  demo1@rolekit.dev   / demopass")
        print("  demo2@rolekit.dev   / demopass")
        print("  desk role exists (settings + announcements CRUD) — assign it from Users")
    finally:
        db.close()


if __name__ == "__main__":
    main()

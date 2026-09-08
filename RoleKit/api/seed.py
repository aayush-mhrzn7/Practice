from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth import hash_password
from api.database import SessionLocal
from api.models import Document, Permission, Role, User

ADMIN_EMAIL = "admin@rolekit.dev"
VIEWER_EMAIL = "viewer@rolekit.dev"
EDITOR_EMAIL = "editor@rolekit.dev"
DEMO1_EMAIL = "demo1@rolekit.dev"
DEMO2_EMAIL = "demo2@rolekit.dev"

PASSWORDS = {
    ADMIN_EMAIL: "adminpass",
    VIEWER_EMAIL: "viewerpass",
    EDITOR_EMAIL: "editorpass",
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


def seed(db: Session) -> None:
    perms = {p.code: p for p in db.execute(select(Permission)).scalars()}
    required = ("documents:read", "documents:write", "documents:edit", "documents:delete")
    missing = [code for code in required if code not in perms]
    if missing:
        raise RuntimeError(
            f"Missing permission rows {missing}. Run `alembic upgrade head` first."
        )

    admin = _get_or_create_user(db, ADMIN_EMAIL, is_admin=True)
    viewer_user = _get_or_create_user(db, VIEWER_EMAIL)
    editor_user = _get_or_create_user(db, EDITOR_EMAIL)
    _get_or_create_user(db, DEMO1_EMAIL)
    _get_or_create_user(db, DEMO2_EMAIL)

    viewer_role = _get_or_create_role(db, "viewer")
    editor_role = _get_or_create_role(db, "editor")

    viewer_role.permissions = [perms["documents:read"]]
    editor_role.permissions = [
        perms["documents:read"],
        perms["documents:write"],
        perms["documents:edit"],
    ]

    if viewer_role not in viewer_user.roles:
        viewer_user.roles.append(viewer_role)
    if editor_role not in editor_user.roles:
        editor_user.roles.append(editor_role)

    existing_docs = db.execute(select(Document)).scalars().all()
    if not existing_docs:
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

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
        print("Seeded RoleKit.")
        print("  admin@rolekit.dev  / adminpass   (is_admin, no document roles)")
        print("  viewer@rolekit.dev / viewerpass  (documents:read)")
        print("  editor@rolekit.dev / editorpass  (read, write, edit)")
        print("  demo1@rolekit.dev  / demopass")
        print("  demo2@rolekit.dev  / demopass")
    finally:
        db.close()


if __name__ == "__main__":
    main()

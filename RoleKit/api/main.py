from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import announcements, audit, auth, catalog, documents, notes, roles, settings, users

app = FastAPI(title="RoleKit")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(roles.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(notes.router)
app.include_router(announcements.router)
app.include_router(audit.router)
app.include_router(settings.router)


@app.get("/health")
def health_check():
    return {"message": "OK"}

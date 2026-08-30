from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import get_settings
from starlette_csrf import CSRFMiddleware
from user.routes import router as user_router
from tags.routes import router as tag_router
from bookmarks.routes import router as bookmark_router
import uvicorn
app = FastAPI(title="LinkStash", description="A simple tool that manages your bookmarks and groups them via tags", version="1.0.0",docs_url="/docs",redoc_url="/redoc")
settings= get_settings()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(
    CSRFMiddleware,
    secret=settings.CSRF_SECRET_KEY,
    cookie_name="csrf_token",
    header_name="x-csrftoken",
    cookie_secure=settings.PROD,    # True in production with HTTPS
    cookie_samesite="lax",           # lax in development, strict in production
)

app.include_router(user_router)
app.include_router(tag_router)
app.include_router(bookmark_router)

@app.get("/")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
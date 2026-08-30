from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import get_settings
from starlette_csrf import CSRFMiddleware
import uvicorn
app = FastAPI()
settings= get_settings()
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

@app.get("/")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
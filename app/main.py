from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.routers.auth import router as auth_router
from app.routers.contacts import router as contacts_router
from app.routers.users import limiter, router as users_router

settings = get_settings()

app = FastAPI(
    title="Contacts REST API — HW 10",
    description=(
        "Authenticated contacts API with JWT authorization, email "
        "verification, rate limiting, CORS, and Cloudinary avatars."
    ),
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(contacts_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "message": "Contacts REST API HW 10 is running.",
        "docs": "/docs",
        "mailpit": "http://127.0.0.1:8025",
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}

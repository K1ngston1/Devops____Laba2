from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis  # type: ignore

from app.auth.router import router as auth_router
from app.project.router import router as project_router
from app.audit.router import router as audit_router
from app.pdf_to_audio.router import router as pdf_to_audio_router
from app.submission.router import router as submission_router
from app.admin.router import router as admin_router
from app.shared.config.env import get_env_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        get_env_settings().redis_url, encoding="utf-8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(project_router, prefix="/project", tags=["project"])
app.include_router(audit_router, prefix="/audit", tags=["audit"])
app.include_router(pdf_to_audio_router, prefix="/pdf-to-audio", tags=["pdf-to-audio"])
app.include_router(submission_router, prefix="/submission", tags=["submission"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/health")
async def check_health() -> str:
    return "I'm good"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from database import init_db
from routers import tutor

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print(f"[Attune] Database initialized.")
    yield
    # Shutdown (nothing needed for now)


app = FastAPI(
    title="Attune API",
    description="AI-powered music theory tutor — REST API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tutor.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}

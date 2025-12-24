import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.api import auth, users
from app.api.admin import admin_router
from app.startup import run_startup_tasks
from app.utils.logger import logger

# Reduce noise from third-party libraries
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"Debug: {settings.debug}, Log Level: {settings.log_level}")

    # Tables are created via migrations (alembic upgrade head)
    # Don't auto-create tables here

    # Auto-seed RBAC, superadmin, and config on startup
    async with AsyncSessionLocal() as db:
        await run_startup_tasks(db)

    yield

    # Shutdown
    logger.info("Shutting down application")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="Sample Application Template API",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "SampleApp API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

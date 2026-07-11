"""OrbitOps India — FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.routers import health, satellites, passes, schedule, export

settings = get_settings()

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("orbitops")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Satellite pass planning and ground-station scheduling platform for "
        "Indian university CubeSat and small-satellite teams. Not affiliated "
        "with ISRO or any government body. Uses legitimate public orbital data."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # exc.errors() can include raw exception objects (e.g. under "ctx") from
    # custom Pydantic validators that raise ValueError — those aren't JSON
    # serializable on their own, so stringify anything under "ctx" first.
    safe_errors = []
    for error in exc.errors():
        error = dict(error)
        if "ctx" in error:
            error["ctx"] = {k: str(v) for k, v in error["ctx"].items()}
        safe_errors.append(error)

    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": jsonable_encoder(safe_errors)},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


API_PREFIX = "/api/v1"
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(satellites.router, prefix=API_PREFIX)
app.include_router(passes.router, prefix=API_PREFIX)
app.include_router(schedule.router, prefix=API_PREFIX)
app.include_router(export.router, prefix=API_PREFIX)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api_prefix": API_PREFIX,
    }

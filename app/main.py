from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import Base, engine
from app.models import Ingredient, Recipe  # noqa: F401 — register models
from app.routers import ingredients, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup and synchronize with Alembic version."""
    Base.metadata.create_all(bind=engine)
    try:
        from alembic.config import Config

        from alembic import command

        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
    except Exception:
        pass
    yield


tags_metadata = [
    {"name": "recipes", "description": "Операции с рецептами"},
    {"name": "ingredients", "description": "Операции с ингредиентами"},
]

app = FastAPI(
    title="Recipe API",
    description="RESTful API для управления рецептами и ингредиентами",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format validation errors with HTTP 400 as required by TZ."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = first.get("loc", ())
        field = loc[-1] if loc else "body"
        msg = first.get("msg", "Validation error")
        reason = f"Field '{field}': {msg}"
    else:
        reason = "Invalid request payload"

    return JSONResponse(
        status_code=400,
        content={"status": 400, "reason": reason},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Format HTTP exceptions consistently as JSON."""
    reason = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "reason": reason},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Format unexpected errors with HTTP 500 as required by TZ."""
    return JSONResponse(
        status_code=500,
        content={"status": 500, "reason": str(exc) or "Internal server error"},
    )


app.include_router(recipes.router)
app.include_router(ingredients.router)

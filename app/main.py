"""
main.py

FastAPI application exposing a simple calculator API (add, subtract,
multiply, divide) as well as a minimal HTML front end for interactive
use / end-to-end testing with Playwright.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.logging_config import setup_logging
from app import operations
from app.database import get_db

setup_logging()
logger = logging.getLogger("calculator.main")

app = FastAPI(title="FastAPI Calculator", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class OperationRequest(BaseModel):
    """Request body for a two-operand arithmetic operation."""
    a: float
    b: float


class OperationResponse(BaseModel):
    """Response body containing the result of an arithmetic operation."""
    result: float


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """Serve the calculator's single-page HTML front end."""
    logger.info(f"Serving index page to client {request.client}")
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(), status_code=200)


@app.get("/health")
async def health_check() -> dict:
    """Simple health check endpoint used by CI / uptime checks."""
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/db-health")
async def db_health_check(db: Session = Depends(get_db)) -> dict:
    """Confirms the FastAPI app can reach the PostgreSQL database."""
    try:
        db.execute(text("SELECT 1"))
        logger.info("Database health check succeeded")
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        raise HTTPException(status_code=503, detail="Database unavailable")


def _handle_operation(op_name: str, func, payload: OperationRequest) -> OperationResponse:
    """Shared helper to run an operation, log it, and translate errors to HTTP errors."""
    try:
        result = func(payload.a, payload.b)
        return OperationResponse(result=result)
    except ValueError as exc:
        logger.error(f"{op_name} failed for a={payload.a}, b={payload.b}: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/add", response_model=OperationResponse)
async def add_endpoint(payload: OperationRequest) -> OperationResponse:
    logger.info(f"Received /add request: {payload}")
    return _handle_operation("ADD", operations.add, payload)


@app.post("/subtract", response_model=OperationResponse)
async def subtract_endpoint(payload: OperationRequest) -> OperationResponse:
    logger.info(f"Received /subtract request: {payload}")
    return _handle_operation("SUBTRACT", operations.subtract, payload)


@app.post("/multiply", response_model=OperationResponse)
async def multiply_endpoint(payload: OperationRequest) -> OperationResponse:
    logger.info(f"Received /multiply request: {payload}")
    return _handle_operation("MULTIPLY", operations.multiply, payload)


@app.post("/divide", response_model=OperationResponse)
async def divide_endpoint(payload: OperationRequest) -> OperationResponse:
    logger.info(f"Received /divide request: {payload}")
    return _handle_operation("DIVIDE", operations.divide, payload)

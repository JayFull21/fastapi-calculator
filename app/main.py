"""
main.py

FastAPI application exposing a simple calculator API (add, subtract,
multiply, divide) as well as a minimal HTML front end for interactive
use / end-to-end testing with Playwright.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import operations

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
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(), status_code=200)


@app.get("/health")
async def health_check() -> dict:
    """Simple health check endpoint used by CI / uptime checks."""
    return {"status": "ok"}


def _handle_operation(func, payload: OperationRequest) -> OperationResponse:
    """Shared helper to run an operation and translate errors to HTTP errors."""
    try:
        result = func(payload.a, payload.b)
        return OperationResponse(result=result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/add", response_model=OperationResponse)
async def add_endpoint(payload: OperationRequest) -> OperationResponse:
    return _handle_operation(operations.add, payload)


@app.post("/subtract", response_model=OperationResponse)
async def subtract_endpoint(payload: OperationRequest) -> OperationResponse:
    return _handle_operation(operations.subtract, payload)


@app.post("/multiply", response_model=OperationResponse)
async def multiply_endpoint(payload: OperationRequest) -> OperationResponse:
    return _handle_operation(operations.multiply, payload)


@app.post("/divide", response_model=OperationResponse)
async def divide_endpoint(payload: OperationRequest) -> OperationResponse:
    return _handle_operation(operations.divide, payload)

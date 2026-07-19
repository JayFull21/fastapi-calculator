"""
FastAPI Calculator — Module 12.

Keeps all Module 11 routes (index page, health checks, stateless /add,
/subtract, /multiply, /divide) and adds:

  * POST /users/register  — create a user with a bcrypt-hashed password
  * POST /users/login     — verify password, return a JWT bearer token
  * BREAD /calculations   — per-user calculation records, built through
                            CalculationFactory (polymorphic model)

All /calculations endpoints require an Authorization: Bearer <token> header.
"""

import logging
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.logging_config import setup_logging
from app import operations
from app.database import Base, engine, get_db
from app.factory.calculation_factory import CalculationFactory
from app.models import Calculation, User
from app.schemas import (
    CalculationCreate,
    CalculationRead,
    CalculationUpdate,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

setup_logging()
logger = logging.getLogger("calculator.main")

app = FastAPI(title="FastAPI Calculator", version="2.0.0")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------
# Module 11 routes (unchanged)
# --------------------------------------------------------------------------
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


# --------------------------------------------------------------------------
# Module 12: auth dependency
# --------------------------------------------------------------------------
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    return user


# --------------------------------------------------------------------------
# Module 12: user endpoints
# --------------------------------------------------------------------------
@app.post(
    "/users/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter(or_(User.username == user_in.username, User.email == user_in.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Registered new user {user.username}")
    return user


@app.post("/users/login", response_model=Token, tags=["users"])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == credentials.username,
                User.email == credentials.username,
            )
        )
        .first()
    )
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(user.id)
    logger.info(f"User {user.username} logged in")
    return Token(access_token=token, user=UserRead.model_validate(user))


# --------------------------------------------------------------------------
# Module 12: calculation endpoints (BREAD)
# --------------------------------------------------------------------------
def _get_owned_calculation(calc_id: int, db: Session, current_user: User) -> Calculation:
    calc = db.get(Calculation, calc_id)
    if calc is None or calc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return calc


# Browse
@app.get("/calculations", response_model=List[CalculationRead], tags=["calculations"])
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.id)
        .order_by(Calculation.id.desc())
        .all()
    )


# Read
@app.get("/calculations/{calc_id}", response_model=CalculationRead, tags=["calculations"])
def read_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_calculation(calc_id, db, current_user)


# Edit
@app.put("/calculations/{calc_id}", response_model=CalculationRead, tags=["calculations"])
def update_calculation(
    calc_id: int,
    calc_in: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = _get_owned_calculation(calc_id, db, current_user)

    # Merge incoming values with the existing row
    new_type = calc_in.type.value if calc_in.type is not None else calc.type
    new_a = calc_in.a if calc_in.a is not None else calc.a
    new_b = calc_in.b if calc_in.b is not None else calc.b

    # Validate + compute through the factory (raises ValueError on
    # divide-by-zero or unknown type). Instance is transient — never added
    # to the session — we only want its validated result.
    try:
        validated = CalculationFactory.create(new_type, new_a, new_b, current_user.id)
        new_result = validated.get_result()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    # Bulk UPDATE instead of mutating the ORM instance: with single-table
    # inheritance the loaded object's Python class can't change (e.g.
    # Addition -> Multiplication), so we update the row directly and
    # re-fetch to get the correct subclass.
    db.query(Calculation).filter(Calculation.id == calc.id).update(
        {"type": new_type, "a": new_a, "b": new_b, "result": new_result}
    )
    db.commit()
    db.expire_all()
    return db.get(Calculation, calc_id)


# Add
@app.post(
    "/calculations",
    response_model=CalculationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def add_calculation(
    calc_in: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership always comes from the token, never the request body —
    # the schema's user_id field is accepted for backward compatibility
    # with CalculationCreate but intentionally ignored here.
    try:
        calc = CalculationFactory.create(
            calc_in.type.value, calc_in.a, calc_in.b, current_user.id
        )
        calc.compute_and_store()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )

    db.add(calc)
    db.commit()
    db.refresh(calc)
    logger.info(f"User {current_user.username} created calculation {calc.id}")
    return calc


# Delete
@app.delete(
    "/calculations/{calc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["calculations"],
)
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = _get_owned_calculation(calc_id, db, current_user)
    db.delete(calc)
    db.commit()
    return None

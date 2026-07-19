# Module 12 — User Auth + Calculation BREAD API

FastAPI application with user registration/login (bcrypt-hashed passwords, JWT tokens) and full BREAD endpoints for calculations, backed by PostgreSQL. Integration tests run in GitHub Actions against a live Postgres service, and a passing build pushes a new image to Docker Hub.

**Docker Hub:** https://hub.docker.com/r/jayfull21/module12_fastapi_calculations

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/register` | Register a new user (unique username + email) |
| POST | `/users/login` | Log in, returns a JWT bearer token |
| GET | `/calculations` | Browse the authenticated user's calculations |
| GET | `/calculations/{id}` | Read one calculation |
| PUT | `/calculations/{id}` | Edit a calculation (result is recomputed) |
| POST | `/calculations` | Add a calculation (`addition`, `subtraction`, `multiplication`, `division`) |
| DELETE | `/calculations/{id}` | Delete a calculation |

All `/calculations` endpoints require an `Authorization: Bearer <token>` header from `/users/login`.

## Run locally with Docker Compose

```bash
docker compose up --build
```

App: http://localhost:8000 — Swagger UI: http://localhost:8000/docs — ReDoc: http://localhost:8000/redoc

## Run integration tests

Start Postgres (via compose or your own instance), then:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
pytest tests -v
```

The suite covers: user registration (success, duplicates, invalid email, short password, hashed password verified directly in the DB), login (success, wrong password, unknown user, login by email), and calculation BREAD (create/read/update/delete, recomputed results, divide-by-zero rejection, invalid type/inputs, 404s, auth required, per-user isolation).


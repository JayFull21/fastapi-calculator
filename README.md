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

## Manual checks via OpenAPI (`/docs`)

1. `POST /users/register` — body:
   ```json
   {"username": "jay", "email": "jay@example.com", "password": "SuperSecret123"}
   ```
   Expect **201** with the user (no password fields returned).
2. `POST /users/login` with the same username/password — expect **200** and an `access_token`.
3. Click **Authorize** (top right), paste the token, confirm.
4. `POST /calculations` — body:
   ```json
   {"type": "addition", "inputs": [2, 3, 5]}
   ```
   Expect **201** with `"result": 10`.
5. `GET /calculations` — your calculation appears in the list.
6. `PUT /calculations/{id}` with `{"type": "division", "inputs": [10, 0]}` — expect **422** (divide by zero).
7. `DELETE /calculations/{id}` — expect **204**, then `GET` the same id — expect **404**.

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR:

1. **test job** — spins up a `postgres:16` service container, installs dependencies, runs `pytest tests -v` against it.
2. **deploy job** — only on a passing `main` push: logs in to Docker Hub and pushes `jayfull21/module12_fastapi_calculations:latest` (plus a commit-SHA tag).

Required repo secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` (access token with **Read & Write** scope).

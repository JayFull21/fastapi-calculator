# FastAPI Calculator

A simple calculator web application built with FastAPI, covered by unit,
integration, and end-to-end (Playwright) tests, with logging and a
GitHub Actions CI pipeline.

## Features

- REST API endpoints: `/add`, `/subtract`, `/multiply`, `/divide`
- Minimal HTML/JS front end served at `/`
- Centralized logging to console and `logs/app.log`
- Full test suite:
  - **Unit tests** — `tests/test_operations.py`
  - **Integration tests** — `tests/test_main.py`
  - **End-to-end tests** — `tests/e2e/test_e2e.py` (Playwright)
- GitHub Actions workflow (`.github/workflows/ci.yml`) that runs all three
  test layers automatically on every push/PR.

## Project Structure

```
fastapi_calculator/
├── app/
│   ├── main.py              # FastAPI app + routes
│   ├── operations.py        # Core arithmetic functions
│   └── logging_config.py    # Logging setup
├── static/
│   └── index.html           # Front-end UI
├── tests/
│   ├── test_operations.py   # Unit tests
│   ├── test_main.py         # Integration tests
│   └── e2e/
│       └── test_e2e.py      # Playwright end-to-end tests
├── .github/workflows/ci.yml # CI pipeline
├── requirements.txt
└── pytest.ini
```


## Running the tests

```bash
# Unit tests
pytest tests/test_operations.py -v

# Integration tests
pytest tests/test_main.py -v

# End-to-end tests (requires the app to be running separately)
uvicorn app.main:app &
pytest tests/e2e -v
```

```

## Postgres Integration

Every push triggers `.github/workflows/ci.yml`, which:
1. Installs dependencies
2. Runs unit tests
3. Runs integration tests
4. Installs Playwright + Chromium
5. Starts the FastAPI server
6. Runs end-to-end tests against the live server

#
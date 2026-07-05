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

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright's browser binaries (only needed for e2e tests)
playwright install chromium
```

## Running the app locally

```bash
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

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

## Logging

All operations and errors are logged with timestamps to both the console
and `logs/app.log` (rotated at 1 MB, keeping 3 backups). Log format:

```
2026-07-05 15:22:06,583 | INFO | calculator.operations | ADD: 4.0 + 5.0 = 9.0
```

## Continuous Integration

Every push triggers `.github/workflows/ci.yml`, which:
1. Installs dependencies
2. Runs unit tests
3. Runs integration tests
4. Installs Playwright + Chromium
5. Starts the FastAPI server
6. Runs end-to-end tests against the live server

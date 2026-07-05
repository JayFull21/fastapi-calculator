"""
test_e2e.py

End-to-end tests using Playwright's sync API + pytest. These tests drive
a real (headless) browser against the running FastAPI app, exercising
the same HTML/JS a human user would interact with.

Requires the app to be served at BASE_URL (default http://127.0.0.1:8000).
In CI, a separate step starts the server (uvicorn) before these tests run.
"""

import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(autouse=True)
def go_to_home(page: Page):
    page.goto(BASE_URL)
    yield


def test_page_title_and_heading(page: Page):
    expect(page).to_have_title("FastAPI Calculator")
    expect(page.locator("h1")).to_have_text("FastAPI Calculator")


def test_addition(page: Page):
    page.fill("#a", "4")
    page.fill("#b", "5")
    page.click("#add-btn")
    expect(page.locator("#result")).to_have_text("Result: 9")


def test_subtraction(page: Page):
    page.fill("#a", "10")
    page.fill("#b", "3")
    page.click("#subtract-btn")
    expect(page.locator("#result")).to_have_text("Result: 7")


def test_multiplication(page: Page):
    page.fill("#a", "6")
    page.fill("#b", "7")
    page.click("#multiply-btn")
    expect(page.locator("#result")).to_have_text("Result: 42")


def test_division(page: Page):
    page.fill("#a", "20")
    page.fill("#b", "4")
    page.click("#divide-btn")
    expect(page.locator("#result")).to_have_text("Result: 5")


def test_division_by_zero_shows_error(page: Page):
    page.fill("#a", "10")
    page.fill("#b", "0")
    page.click("#divide-btn")
    expect(page.locator("#error")).to_have_text("Division by zero is not allowed.")


def test_invalid_input_shows_error(page: Page):
    page.fill("#a", "")
    page.fill("#b", "5")
    page.click("#add-btn")
    expect(page.locator("#error")).to_have_text("Please enter valid numbers for A and B.")

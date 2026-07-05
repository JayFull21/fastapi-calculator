"""
logging_config.py

Centralized logging setup for the calculator application. Logs go both to
the console and to a rotating file (logs/app.log) so history is preserved
across runs without growing unbounded.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logging() -> None:
    """Configure the root 'calculator' logger with console + file handlers."""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("calculator")
    logger.setLevel(logging.INFO)

    # Avoid attaching duplicate handlers if setup_logging() is called twice
    # (e.g., once by main.py and once by tests importing main).
    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

"""
Logging setup for BusBidder Spain
"""

import logging
from pathlib import Path

LOG_FILE = Path("output/logs/busbidder.log")


def setup_logging(log_file: Path = LOG_FILE) -> None:
    """Send log messages (INFO and above) to a file, creating its folder if needed."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger. Call once at the entry point of any script.
    level: Logging level string ("INFO", "DEBUG", etc).
    """
    root = logging.getLogger()
    lvl = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(lvl)

    if not root.handlers:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter(LOG_FORMAT))
        root.addHandler(sh)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

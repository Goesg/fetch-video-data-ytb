import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))
        logger.addHandler(handler)
    return logger


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.getLogger("app").setLevel(level)
    # Suppress yt-dlp's own output — we control what gets printed
    logging.getLogger("yt_dlp").setLevel(logging.ERROR)

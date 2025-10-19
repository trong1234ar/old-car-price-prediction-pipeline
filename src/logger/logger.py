
import logging
import sys
import os

def get_logger(name: str = None, level: str = "INFO", log_file: str = None) -> logging.Logger:
    LEVELS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    
    LOG_FMT = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    logger = logging.getLogger(name)
    logger.setLevel(LEVELS.get(level.upper(), logging.INFO))
    logger.propagate = False  # avoid duplicate logs if root has handlers

    # clear existing handlers if reconfiguring
    if logger.handlers:
        for h in list(logger.handlers):
            logger.removeHandler(h)

    formatter = logging.Formatter(LOG_FMT, DATE_FMT)

    # console
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # optional file
    if log_file:
        fh = logging.FileHandler(log_file, mode='w', encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
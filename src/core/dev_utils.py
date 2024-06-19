from pathlib import Path
import sys
import time
import logging


def set_up_logger(logger_name: str, log_dir: Path, level: str = logging.INFO) -> logging.Logger:

    # Build logger with passed level and format
    formatter = logging.Formatter('[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Add file handler
    file_handler = logging.FileHandler(
        log_dir / f"{time.strftime('%d-%m-%Y')}.log"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Add stream handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

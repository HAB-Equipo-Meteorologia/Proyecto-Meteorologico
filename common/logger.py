import inspect
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def get_class_name() -> str:
    frame = inspect.currentframe()
    while frame:
        if 'self' in frame.f_locals:
            return frame.f_locals['self'].__class__.__name__
        frame = frame.f_back
    return 'root'


class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_message = super().format(record)

        # Apply yellow color for INFO level messages
        if record.levelname == "INFO":
            log_message = f'\033[33m{log_message}\033[0m'  # Yellow color for the entire message

        return log_message

def setup_logger(log_file: str, class_name: Optional[str] = None) -> logging.Logger:
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if class_name is None:
        class_name = get_class_name()

    logger = logging.getLogger(class_name)
    logger.setLevel(logging.DEBUG)

    logger.propagate = False

    if not logger.handlers:

        if os.getenv('TEST_ENV'):
            filename = f'logs/{log_file}.log.test'
        else:
            filename = f'logs/{log_file}.log'

        file_handler = RotatingFileHandler(filename, maxBytes=10000000, backupCount=3)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s'))
        logger.addHandler(stream_handler)

    return logger

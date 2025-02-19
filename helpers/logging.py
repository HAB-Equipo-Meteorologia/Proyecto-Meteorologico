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


def setup_logger(log_file: str, class_name: Optional[str] = None) -> logging.Logger:
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if class_name is None:
        class_name = get_class_name()

    logger = logging.getLogger(class_name)
    logger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    handler = RotatingFileHandler(f'logs/{log_file}.log', maxBytes=10000000, backupCount=3)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

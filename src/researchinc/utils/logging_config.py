import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Create logger
    logger = logging.getLogger('researchinc')
    logger.setLevel(logging.INFO)
    
    # If the logger already has handlers, return it without adding new ones
    if logger.handlers:
        return logger

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        'researchinc.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)


    return logger
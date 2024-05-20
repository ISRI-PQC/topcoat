import logging
import os
import sys
from datetime import datetime


def get_logger(level, name):
    formatter = logging.Formatter(
        "%(levelname)-8s - %(asctime)s - %(name)-14s: %(message)s"
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    now = datetime.now()
    os.makedirs(f"logs/{now.strftime('%Y-%m-%d')}", exist_ok=True)

    logger = logging.getLogger(f"TOPCOAT-{name}")
    logger.setLevel(level)

    file_handler = logging.FileHandler(
        f"logs/{now.strftime('%Y-%m-%d')}/{name}.log", mode="a"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

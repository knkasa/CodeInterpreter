from loguru import logger
import sys

class Logger:
    def __init__(self):
        logger.remove()
        logger.add(
            sys.stdout,
            level="DEBUG",
            serialize=True,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        )
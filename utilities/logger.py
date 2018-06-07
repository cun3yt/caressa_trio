import daiquiri
import logging

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()


def log(str):
    logger.info(str)

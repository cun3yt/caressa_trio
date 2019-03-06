import daiquiri
import logging

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()


def log(msg):
    logger.info(msg)


def log_error(msg):
    logger.error(msg)


def log_warning(msg):
    logger.warning(msg)

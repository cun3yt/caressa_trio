import daiquiri
import logging

daiquiri.setup(level=logging.DEBUG)
logger = daiquiri.getLogger()


def log(msg):
    logger.info(msg)


def log_error(msg):
    logger.error(msg)


def log_warning(msg):
    logger.warning(msg)


def log_debug(msg):
    logger.debug(msg)

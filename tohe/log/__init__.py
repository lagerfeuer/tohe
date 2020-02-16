import logging
import os

LOGGER = logging.getLogger('Tohe')
DEBUG = LOGGER.debug
INFO = LOGGER.info
WARN = LOGGER.warning
ERROR = LOGGER.error

if os.getenv('DEBUG'):
    LOGGER.setLevel(logging.DEBUG)
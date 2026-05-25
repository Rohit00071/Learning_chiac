import logging
import logging.config
from utils.config import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name):
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name of the logger, usually __name__

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
import logging
from logging.handlers import TimedRotatingFileHandler
import os

def setup_log_rotation(log_file: str, backup_count: int = 30):
    """Configures a logger with timed rotation."""
    logger = logging.getLogger("forge.telemetry")
    logger.setLevel(logging.INFO)
    
    # TimedRotatingFileHandler: rotates daily ('midnight'), keeps 'backup_count' files.
    handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=backup_count
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

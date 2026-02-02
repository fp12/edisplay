import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_monitoring_logger():
    log_dir = Path('tmp')
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger('edisplay.monitoring')
    logger.setLevel(logging.INFO)
    
    file_handler = TimedRotatingFileHandler(
        log_dir / 'monitoring.log',
        when='midnight',
        interval=1,  # rotate daily
        backupCount=7  # keep for 7d
    )
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


monitoring_logger = setup_monitoring_logger()
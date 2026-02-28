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
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def setup_network_presence_logger():
    log_dir = Path('tmp')
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger('edisplay.network_presence')
    logger.setLevel(logging.INFO)
    
    file_handler = TimedRotatingFileHandler(
        log_dir / 'network_presence.log',
        when='midnight',
        interval=1,  # rotate daily
        backupCount=7  # keep for 7d
    )
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


monitoring_logger = setup_monitoring_logger()
network_presence_logger = setup_network_presence_logger()

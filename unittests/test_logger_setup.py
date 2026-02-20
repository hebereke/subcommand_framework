import tempfile
import os
import logging
from pathlib import Path
from logger import setup_logging, get_logger


def test_setup_logging_writes_file(tmp_path):
    cfg = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {'format': '%(message)s'}
        },
        'handlers': {
            'fileHandler': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'filename': '__LOGFILE__'
            }
        },
        'loggers': {
            'testlogger': {
                'level': 'INFO',
                'handlers': ['fileHandler'],
                'propagate': False
            }
        },
        'root': {'level': 'INFO'}
    }
    cfg_path = tmp_path / 'cfg.yaml'
    import yaml
    with open(cfg_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(cfg, f)

    logfile = tmp_path / 'out.log'
    setup_logging(config_file=str(cfg_path), logfile=str(logfile))
    logger = get_logger('testlogger')
    logger.info('hello')
    assert logfile.exists()
    data = logfile.read_text(encoding='utf-8')
    assert 'hello' in data

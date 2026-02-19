import logging
import logging.config
import yaml
import sys
import os
from pathlib import Path
import datetime

LOGGING_CONFIG_FILE = 'logging_config.yaml'
RESULT_LEVEL = 25
SCRIPT_NAME = 'application'

class ResultLogger(logging.Logger):
    default_prefix = None
    def __init__(self, name):
        super().__init__(name)
        self.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.addHandler(handler)
    def result(
        self, message, *,
        logfile=None,
        output_stdout=True,
        prefix=None,
        prefix_delimiter=' ',
        output_delimiter=' ',
        indent=0,
        **kwargs
        ):
        ## prefix
        if prefix is None and self.default_prefix is not None:
            prefix = self.default_prefix

        ## format message
        if isinstance(message, list):
            message = output_delimiter.join(str(s) for s in message)
        if prefix is not None:
            message = f'{prefix}{prefix_delimiter}{message}'
        if indent > 0:
            message = f"{' ' * indent}{message}"

        ## output to stdout
        if output_stdout:
            super().log(RESULT_LEVEL, message)

        ## output to logfile
        if logfile:
            fh = logging.FileHandler(logfile, mode='a', encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(message)s'))
            self.addHandler(fh)
            self.log(RESULT_LEVEL, message, **kwargs)
            self.removeHandler(fh)

## define level
logging.addLevelName(RESULT_LEVEL, 'RESULT')
logging.setLoggerClass(ResultLogger)

def setup_logging(config_file=LOGGING_CONFIG_FILE, logfile=None):
    with open(config_file, 'r', encoding='utf-8') as f:
        logging_config = yaml.safe_load(f)
    if logfile:
        if 'handlers' in logging_config and 'fileHandler' in logging_config['handlers']:
            handler = logging_config['handlers']['fileHandler']
            if handler.get('filename') == '__LOGFILE__':
                handler['filename'] = logfile
    logging.config.dictConfig(logging_config)

def get_logger(name=None):
    return logging.getLogger(name)

def default_logfile_name(script_name=SCRIPT_NAME):
    now = datetime.datetime.now().strftime('%y%m%d%H%M')
    logfile_name = f'{script_name}-{now}-{os.getpid()}.log'
    return Path.cwd() / Path(logfile_name)

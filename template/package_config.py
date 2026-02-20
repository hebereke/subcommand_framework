## must libraries and modules
import argparse
from dataclasses import dataclass
from config import config

@dataclass(kw_only=True)
class ConfigCommon:
    logfile: str | None = None
    loglevel: str = 'DEBUG'
    tmpfile: str| None = None
    verbose: bool = False

def common_arguments() -> argparse.ArgumentParser:
    '''parse arguments and return a parser for common options'''
    parser_common = argparse.ArgumentParser(add_help=False)

    ## common options
    args_common = parser_common.add_argument_group('common options')
    args_common.add_argument(
        '--verbose',
        default=config.verbose,
        action='store_true',
        help='enable verbose mode'
    )
    args_common.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {config.version}'
    )

    ## logging options
    args_log = parser_common.add_argument_group('logging options')
    args_log.add_argument(
        '--loglevel',
        default=config.loglevel,
        help='loglevel from "CRITICAL|ERROR|WARNING|INFO|DEBUG"',
        metavar="LOGLEVEL"
    )
    args_log.add_argument(
        '--logfile',
        default=config.logfile,
        help='logfile path',
        metavar='FILE'
    )

    return parser_common

def positional_arguments() -> argparse.ArgumentParser:
    '''parser of positional arguments for subcommands'''
    parser_positional = argparse.ArgumentParser(add_help=False)
    parser_positional.add_argument(
        'target',
        nargs='+',
        metavar='FILE',
        help='target files'
    )
    return parser_positional

def preproc_config():
    return None

def postproc_config(args=None):
    return None

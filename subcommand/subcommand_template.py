### template subcommand module
'''subcommand module template'''

## must libraries and modules
from dataclasses import dataclass
from args import CustomHelpFormatter
from config import config
from logger import get_logger

## define module config
@dataclass
class ConfigSubCommand:
    subcommand_template: bool = False
    prefix_template: str = 'TEMPLATE'
config.append_config(ConfigSubCommand)
logger = get_logger()

def register_subcommand(subparsers, parent_parsers):
    ## subcommand defaults
    conf_dict = config.to_dict()
    yaml_default = config.params.get('command', {}).get('template', {})
    defaults = {**conf_dict, **yaml_default}

    ## subcommand argument
    parser_subcommand = subparsers.add_parser(
        'template',
        help='subcommand template',
        description='Run template subcommand',
        formatter_class=CustomHelpFormatter,
        parents=parent_parsers
    )
    parser_subcommand.set_defaults(handler=cmd)
    args_subcommand = parser_subcommand.add_argument_group('template subcommand options')
    args_subcommand.add_argument(
        '--debug',
        dest='debug_flag',
        action='store_true',
        default=defaults['subcommand_template'],
        help='debug'
    )
    args_subcommand.add_argument(
        '--prefix',
        dest='prefix_template',
        default=defaults['prefix_template'],
        help='prefix',
        metavar='STRING'
    )

def cmd(j):
    '''template command'''
    if config.debug_flag:
        logger.debug(f'{config.prefix_template} w/ debug flag by config.debug_flag={config.debug_flag}')
        logger.debug(config.display())
    else:
        logger.info(f'{config.prefix_template} w/o debug flag by config.debug_flag={config.debug_flag}')
## load standard libraries
import yaml
import importlib
from dataclasses import make_dataclass, field
from pathlib import Path

## load subcommands_framework libraries
from config import config
from args import config_arguments, positional_arguments, build_root_parser, error_nosubcommand
from logger import get_logger
from package_config import ConfigCommon, common_arguments, preproc_config, postproc_config

## append common config
config.append_config(ConfigCommon)

## declare a safe default logger for module-level functions; main() will reinitialize
logger = get_logger(__name__)

## default user config files location
USER_CONFIG_FILES = [
    f'.{config.prog}',
    f'~/.{config.prog}',
    f'~/.config/{config.prog}.yaml'
]

def search_configfile(config_files: list) -> Path | None:
    '''search config file location'''
    for p in map(Path, config_files):
        p = p.expanduser().absolute()
        if p.is_file():
            logger.info(f'detect {p}')
            return p
    return None

def load_config_file(config_file: Path) -> dict:
    '''load YAML format config file'''
    defaults = {}
    if isinstance(config_file, Path) and config_file.is_file():
        logger.info(f'load config file ({config_file})')
        with config_file.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise ValueError('top-level YAML must be a mapping/dict')
            defaults.update(data)
    return defaults

def load_user_config_file(parser_config, user_config_files):
    '''determine config file path and load available config file'''
    args_config,_ = parser_config.parse_known_args()
    if args_config.config:
        user_config_files = [args_config.config] + user_config_files
    config_file = search_configfile(user_config_files)
    if config_file is not None:
        user_config_defaults = load_config_file(config_file)
        if 'common' in user_config_defaults:
            fields_spec = []
            for k, v in user_config_defaults['common'].items():
                fields_spec.append((k, type(v), field(default=v)))
            ConfigUserCommon = make_dataclass('ConfigUserCommon', fields_spec)
            config.append_config(ConfigUserCommon)
        if config.debug:
            logger.debug('Default configs:')
            for k,v in config.items():
                logger.debug(f'  {k} = {v}')
            config.params = {**config.params, **user_config_defaults}
    return config.params

def load_subcommands(subparsers, parent_parsers):
    '''load subcommand modules and register available config and arguments'''
    if 'package' in config.params:
        for module_name in config.params['package']['subcommand_modules']:
            if config.debug:
                logger.debug(f'load {module_name}')
                logger.debug(config.print_config())
            if config.subcommands_dir.name == '': # subcommands_dir = Path('.')
                module = importlib.import_module(module_name)
            else:
                module = importlib.import_module(f'{config.subcommands_dir.name}.{module_name}')
            module.register_subcommand(subparsers, parent_parsers)

def main():
    ## pre-processing
    preproc_config()

    # reinitialize logger with program name after config is ready
    global logger
    logger = get_logger(config.prog)

    ## define config file argument and load user config file
    parser_config = config_arguments(USER_CONFIG_FILES)
    load_user_config_file(parser_config, USER_CONFIG_FILES)

    ## define package common arguments
    parser_common = common_arguments()

    ## define positional argument for subcommands
    parser_positional = positional_arguments()

    ## build root parser
    parser, subparsers = build_root_parser(
        config.prog,
        config.description,
        [parser_config, parser_common]
    )

    ## load subcommands
    load_subcommands(
        subparsers,
        [parser_config, parser_common, parser_positional]
    )
    args = parser.parse_args()

    ## help printout if no subcommand is specified
    if args.command is None:
        error_nosubcommand(parser)
        parser.exit(2)
    ## otherwise call function related to subcommand
    else:
        postproc_config(args) # post-processing
        args.handler(args)

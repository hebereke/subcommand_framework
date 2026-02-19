from dataclasses import dataclass, fields, asdict
from pathlib import Path, PosixPath
import yaml
from typing import Type
from config import ConfigT

PACKAGE_CONFIG_FILE = 'package_configs.yaml'

def load_package_config(package_dir: Path) -> dict:
    '''load package configuration file'''
    package_config_file = package_dir / Path(PACKAGE_CONFIG_FILE)
    if not package_config_file.is_file():
        raise FileExistsError(f'no package config file {package_config_file}')
    package_config = {}
    with package_config_file.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError('top-level YAML must be a mapping/dict')
        package_config.update(data)
    return package_config

def initialize_params(config: Type[ConfigT], params: dict | None) -> dict:
    '''initialize parameter by defined type in config'''
    config_params = asdict(config())
    if params:
        for f in fields(config):
            if f.name in params:
                ftype = type(config_params[f.name])
                value = params[f.name]
                try:
                    if ftype == int:
                        value = int(value)
                    elif ftype == float:
                        value = float(value)
                    elif ftype == str:
                        value = str(value)
                    elif ftype == list:
                        value = list(value)
                    elif ftype == bool:
                        value = bool(value)
                    elif ftype == PosixPath:
                        value = Path(value)
                except Exception:
                    pass
                config_params[f.name] = value
    return config_params

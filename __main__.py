## check if yaml library is available
import importlib.util
if not importlib.util.find_spec('yaml'):
    Exception('taml module is required')

## load standard libraries
from dataclasses import dataclass, field
from pathlib import Path

## load subcommands_framework libraries
from config import GlobalConfig
from configfile import load_package_config, initialize_params

## run main routine
if __name__ == '__main__':
    ## determine package location and load package config file
    package_dir = Path(__file__).resolve().parent
    package_config = load_package_config(package_dir)

    ## define script config
    @dataclass(kw_only=True)
    class ConfigPackage:
        prog: str = str(package_dir.name)           # program name
        description: str = ''                       # program description
        version: float = 0.0                        # version
        package_dir: Path = package_dir             # package installation directory
        subcommands_dir: Path = Path('subcommands') # subcommands directory relatively to package_dir
        data_dir: Path = Path('data')               # data directory relatively to package_dir
        debug: bool = False                         # debug mode flag
        params: dict = field(default_factory=dict)  # package config and user defined config

    ## initialize GlobalConfig with ConfigPackage and update package field of package_config
    package_params = None
    if 'package' in package_config:
        package_params = package_config['package']
        params = initialize_params(ConfigPackage, package_params)
        GlobalConfig.set_config(ConfigPackage(**params))
        GlobalConfig.set('params', package_config)

    ## call main function
    from main import main
    main()

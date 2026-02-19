# Subcommand Framework

Project overview
----------------
This repository provides a small, lightweight framework for building Python command-line tools that expose subcommands. It includes utilities for:

- declarative configuration using dataclasses (`GlobalConfig`)
- loading YAML package/user configuration
- building argparse-based subcommands and argument groups
- helper utilities for installation, packaging and file operations
- logging helpers and a sample logging configuration

Requirements
------------
- Python 3.10+ (uses modern type syntax and dataclass features)
- See `requirements.txt` for test/runtime extras (PyYAML, pytest).

Quick start
-----------
1. Install dependencies for development and testing:

```bash
python -m pip install -r requirements.txt
```

2. Run tests:

```bash
pytest -q
```

Design notes
------------
- Global configuration is represented by a dataclass instance stored in `GlobalConfig`. Initialize it early in your entrypoint (for example in `main()`), before importing modules that use `config`.
- Module-level loggers use a safe default (`get_logger(__name__)`) and `main()` reinitializes the logger with the program name after `GlobalConfig` has been set.
- `initialize_params` attempts type conversion based on dataclass default values. For stricter validation, consider using `pydantic` models and replacing or wrapping `initialize_params`.

Repository structure
--------------------
- `__main__.py`, `main.py` - entry points and main runtime
- `config.py` - `GlobalConfig` and `config` proxy
- `configfile.py` - package/user configuration loader and `initialize_params`
- `args.py` - argparse helpers and custom formatters/actions
- `logger.py` - logger helpers and `ResultLogger`
- `install.py`, `utils.py` - installer and utility helpers
- `subcommand/` - subcommand modules and template
- `template/` - example package config and logging config
- `tests/` - pytest unit tests

Adding subcommands
------------------
Subcommands live under the `subcommand/` package. Each module should export a `register_subcommand(subparsers, parent_parsers)` function that creates a parser and sets `handler` on the parser defaults. See `subcommand/subcommand_template.py` for an example.

Configuration
-------------
- Package-level configuration is read from `package_configs.yaml` inside the package directory.
- User-level configuration files are searched from common locations (dotfile, `~/.config/`), and loaded via YAML.

Contributing
------------
- Run tests locally with `pytest` and open a PR. Add tests for any bugfix or behavior change.

License
-------
See the `LICENSE` file in the repository.

Contact
-------
If you need help or want improvements, open an issue or PR on the repo.

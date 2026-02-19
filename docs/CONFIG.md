About GlobalConfig

Overview
- `GlobalConfig` is a shared configuration store that holds an instance of a dataclass for the whole application.
- Important: You must call `GlobalConfig.set_config(...)` to initialize the global config before any module that uses `config` accesses it. Accessing the config before initialization will raise `RuntimeError('GlobalConfig not initialized')`.

Safe initialization pattern (example)

```python
# app.py (entry point)
from dataclasses import dataclass
from config import GlobalConfig

@dataclass
class AppConfig:
    prog: str = 'mytool'
    debug: bool = False

def main():
    GlobalConfig.set_config(AppConfig())
    # Import other modules here or perform logging/CLI initialization
    from logger import get_logger
    logger = get_logger(GlobalConfig.get('prog'))
    # ... application logic ...

if __name__ == '__main__':
    main()
```

- Note: If you call `get_logger(config.prog)` at module import time and `config` is not initialized yet, this will raise an exception. For such modules, move logger and config access into lazy initialization (for example inside `main()`).

Examples for explicit typing with `initialize_params`

The current `initialize_params` implementation infers types from default values and attempts conversion. This is convenient, but if you need stricter typing you should declare a schema explicitly.

1) Explicit dataclass declaration

```python
from dataclasses import dataclass

@dataclass
class ConfigPackage:
    prog: str
    version: float
    debug: bool = False

# package_yaml = {'prog': 'app', 'version': '1.2', 'debug': 'True'}
# initialize_params will attempt to convert types from defaults, but for stricter validation
# consider adding explicit validation or using a library like pydantic.
```

2) Using pydantic (recommended for strict validation)

```python
from pydantic import BaseModel

class ConfigPackageModel(BaseModel):
    prog: str
    version: float
    debug: bool = False

cfg = ConfigPackageModel(**package_yaml)
# cfg.version is a float and cfg.debug is normalized to bool
```

Summary
- For small utilities and scripts the current `initialize_params` is convenient.
- For production code where strict typing and validation are required, consider adopting `pydantic` and replacing `initialize_params` with a thin wrapper around pydantic models.

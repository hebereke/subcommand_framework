from dataclasses import is_dataclass, asdict, field, fields, make_dataclass, MISSING
from typing import Type, TypeVar, Any, Optional, Tuple, Dict

ConfigT = TypeVar('ConfigT')

class GlobalConfig:
    '''
    GlobalConfig class
    support dataclass only
    '''
    _instance: Optional[Any] = None

    @classmethod
    def _has_instance(cls) -> bool:
        '''check if _instance is None'''
        return cls._instance is not None

    @classmethod
    def _init_check(cls) -> None:
        '''sanity check if has been initialized'''
        if not cls._has_instance():
            raise RuntimeError('GlobalConfig not initialized')

    @classmethod
    def _ensure_field(cls, key: str) -> None:
        cls._init_check()
        if not any(f.name == key for f in fields(cls._instance)):
            raise AttributeError(f'Unknown dataclass field: {key!r}')

    @classmethod
    def _current_dict(cls) -> dict:
        '''helper method converting GlobalConfig to dict'''
        cls._init_check()
        return asdict(cls._instance)

    @classmethod
    def is_valid(cls) -> bool:
        '''return True if valid'''
        return cls._instance is not None and is_dataclass(cls._instance)

    @classmethod
    def count(cls) -> int:
        '''return number of fields'''
        if not cls._has_instance():
            return 0
        return len(asdict(cls._current_dict()))

    @classmethod
    def is_empty(cls) -> bool:
        '''return True if empty'''
        return cls.count() == 0

    @classmethod
    def describe(cls) -> str:
        '''return description strings'''
        if cls.is_empty():
            return '<GlobalConfig: empty>'
        return f'<GlobalConfig: {cls.count()} fields, current=cls._instance>'

    @classmethod
    def set(cls, key: str, value:Any) -> None:
        '''set value to specific key'''
        cls._ensure_field(key)
        setattr(cls._instance, key, value)

    @classmethod
    def get(cls, key: str) -> Any:
        '''get value of specific key'''
        cls._ensure_field(key)
        getattr(cls._instance, key)

    @classmethod
    def set_config(cls, config: ConfigT) -> None:
        '''set local config instance'''
        if not is_dataclass(config):
            raise TypeError('set_config expects a dataclass instance')
        cls._instance = config

    @classmethod
    def get_config(cls) -> ConfigT:
        '''get stored config as instance'''
        cls._init_check()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        '''clear GlobalConfig'''
        cls._instance = None

    @classmethod
    def keys(cls) -> Tuple[str, ...]:
        '''return all keys stored in GlobalConfig'''
        data = cls._current_dict()
        return tuple(data.keys())

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        '''return all values stored in GlobalConfig'''
        data = cls._current_dict()
        return tuple(data.values())

    @classmethod
    def items(cls) -> Tuple[str, ...]:
        '''return all combinations of keys and values stored in GlobalConfig'''
        data = cls._current_dict()
        return tuple(data.items())

    @classmethod
    def extend_schema(cls, *schema_classes: Type[Any], prefer_existing: bool = True):
        '''append specific dataclass fields
            - prefer_existing: True to prioritize existed schema
        '''
        if not schema_classes:
            return

        current_values: Dict[str, Any] = {}
        current_fields: Dict[str, Any] = {}
        if cls._has_instance():
            current_values = asdict(cls._instance)
            for f in fields(cls._instance):
                current_fields[f.name] = f

        merged: Dict[str, Any] = dict(current_fields)
        for sc in schema_classes:
            if not is_dataclass(sc):
                raise TypeError('extend_schema expects dataclass types')
            for f in fields(sc):
                if f.name in merged:
                    if not prefer_existing:
                        merged[f.name] = f
                else:
                    merged[f.name] = f

        spec = []
        for name, f in merged.items():
            ftype = f.type
            if f.default is not MISSING:
                spec.append((name, ftype, field(default=f.default)))
            elif f.default_factory is not MISSING:
                spec.append((name, ftype, field(default_factory=f.default_factory)))
            else:
                spec.append((name, ftype))

        MergedConfig = make_dataclass('MergedConfig', spec, kw_only=True)

        init_kwargs = {}
        for f in fields(MergedConfig):
            if f.name in current_values:
                init_kwargs[f.name] = current_values[f.name]
            else:
                pass

        cls._instance = MergedConfig(**init_kwargs)

class _ConfigProxy:
    '''proxy class to GlobalConfig for syntax sugar'''
    def __dir__(self):
        try:
            return list(GlobalConfig.keys())
        except Exception:
            return []
    ## accessing field via attribute
    def __getattr__(self, name: str):
        '''get field'''
        GlobalConfig.get(name)
    def __setattr__(self, name: str, value: Any):
        '''set field'''
        GlobalConfig.set(name, value)

    ## sccessing fields as dict method
    def keys(self):
        '''return all keys stored in GlobalConfig'''
        return GlobalConfig.keys()
    def values(self):
        '''return all values stored in GlobalConfig'''
        return GlobalConfig.values()
    def items(self):
        '''return all combinations of keys and values stored in GlobalConfig'''
        return GlobalConfig.items()

    ## alias to extend_schema
    def append_config(self, config_class: ConfigT):
        '''append one dataclass schema to GlobalConfig'''
        return GlobalConfig.extend_schema(config_class)

    ## convert to dict
    def to_dict(self):
        '''export to dict'''
        return GlobalConfig.__current_dict()

    ## display config
    def display(self, indent=4):
        '''display config keys and values with readable format'''
        out = 'Config:\n'
        indent_space = indent * ' '
        for k,v in self.items():
            out += f'{indent_space}{k} = {v}\n'
        return out

## alias to _ConfigProxy class
config = _ConfigProxy()
